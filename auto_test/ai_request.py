import requests
import json
import os
from datetime import datetime
import re
from openpyxl import Workbook, load_workbook
from openpyxl.utils import get_column_letter
from openpyxl.styles import PatternFill

# OpenAIのAPIキーを設定 (環境変数から読み込み)
OPENAI_API_KEY = os.getenv("OPENAI_APIKEY")

# 生成されたJSONファイルの保存先フォルダを設定 (絶対パス)
json_folder = os.path.join(os.path.dirname(__file__), "jsons")

# jsonsフォルダが存在しない場合は作成
if not os.path.exists(json_folder):
    os.makedirs(json_folder)

# OpenAI APIを呼び出す関数
def call_openai_api(base64_content):
    try:
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "gpt-4o-2024-08-06",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "この画像から、取引合計金額、取引日付（年、月、日を一つのフィールドにまとめる）、取引相手を抽出してください。"
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_content}"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 2000,
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": "invoice_extraction",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "amount": { "type": "integer" },
                            "date": { "type": "string" },
                            "trading_partner": { "type": "string" }
                        },
                        "required": ["amount", "date", "trading_partner"],
                        "additionalProperties": False
                    },
                    "strict": True
                }
            }
        }
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"OpenAI API呼び出しエラー: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"OpenAI API呼び出し中にエラーが発生しました: {e}")
        return None

# APIレスポンスから情報を抽出する関数
def extract_info_from_response(response_data):
    if response_data is None or 'choices' not in response_data:
        return None
    
    content = response_data['choices'][0]['message']['content']
    
    # JSON形式の文字列を抽出
    json_match = re.search(r'\{.*\}', content, re.DOTALL)
    if json_match:
        try:
            extracted_info = json.loads(json_match.group())
            return extracted_info
        except json.JSONDecodeError:
            print("JSONの解析に失敗しました。")
            return None
    else:
        print("JSONデータが見つかりませんでした。")
        return None

# JSON形式で出力して保存する関数
def save_response_as_json(response_data):
    if response_data is None:
        return None
    
    extracted_info = extract_info_from_response(response_data)
    if extracted_info is None:
        print("情報の抽出に失敗しました。")
        return None
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_file_name = f"response_{timestamp}.json"
    json_file_path = os.path.join(json_folder, json_file_name)
    
    with open(json_file_path, "w", encoding='utf-8') as json_file:
        json.dump(extracted_info, json_file, ensure_ascii=False, indent=4)
    
    print(f"レスポンスが {json_file_path} に保存されました。")
    return extracted_info

# データの完全性をチェックする関数
def check_data_completeness(data):
    return all(data.get(field) for field in ['amount', 'date', 'trading_partner'])

# Excelファイルに書き込む関数
def write_to_excel(data_list):
    excel_file = "json_check.xlsx"
    
    # Excelファイルが存在する場合は読み込み、存在しない場合は新規作成
    if os.path.exists(excel_file):
        wb = load_workbook(excel_file)
        ws = wb.active
        row = ws.max_row + 1
    else:
        wb = Workbook()
        ws = wb.active
        ws.title = "json_check"
        headers = ["Amount", "Date", "Trading Partner", "Completeness"]
        for col, header in enumerate(headers, start=1):
            ws.cell(row=1, column=col, value=header)
        row = 2

    # データを書き込む
    for data in data_list:
        ws.cell(row=row, column=1, value=data.get('amount'))
        ws.cell(row=row, column=2, value=data.get('date'))
        ws.cell(row=row, column=3, value=data.get('trading_partner'))
        
        # データの完全性をチェックし、結果を書き込む
        is_complete = check_data_completeness(data)
        completeness_cell = ws.cell(row=row, column=4, value='True' if is_complete else 'False')
        
        # セルの背景色を設定
        if is_complete:
            completeness_cell.fill = PatternFill(start_color="00FF00", end_color="00FF00", fill_type="solid")
        else:
            completeness_cell.fill = PatternFill(start_color="FF0000", end_color="FF0000", fill_type="solid")
        
        row += 1

    # 列幅を自動調整
    for column in ws.columns:
        max_length = 0
        column_letter = get_column_letter(column[0].column)
        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(cell.value)
            except:
                pass
        adjusted_width = (max_length + 2)
        ws.column_dimensions[column_letter].width = adjusted_width

    # ファイルを保存
    wb.save(excel_file)
    print(f"データが {excel_file} に書き込まれました。")

# Base64エンコードされたコンテンツのリストを受け取り、処理する関数
def process_base64_list(base64_list):
    all_data = []
    for base64_content in base64_list:
        response = call_openai_api(base64_content)
        extracted_info = save_response_as_json(response)
        if extracted_info:
            all_data.append(extracted_info)
    
    if all_data:
        write_to_excel(all_data)
    else:
        print("処理可能なデータがありませんでした。")