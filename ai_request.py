import requests
import json
import os
from datetime import datetime

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
        # APIにリクエストを送信
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "gpt-4-vision-preview",
            "messages": [
                {"role": "system", "content": "あなたはアシスタントです。"},
                {"role": "user", "content": [
                    {"type": "text", "text": "以下の画像から取引合計金額、取引年月日、取引相手を抽出してください。"},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_content}"}}
                ]}
            ],
            "max_tokens": 300
        }
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)
        if response.status_code == 200:
            return response.json()  # レスポンスをJSON形式に変換して返す
        else:
            print(f"OpenAI API呼び出しエラー: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"OpenAI API呼び出し中にエラーが発生しました: {e}")
        return None

# APIレスポンスから必要な情報を抽出する関数
def extract_info_from_response(response_data):
    if response_data is None or 'choices' not in response_data:
        return None
    
    content = response_data['choices'][0]['message']['content']
    
    # 文字列から数値と日付を抽出
    import re
    
    amount_match = re.search(r'(?:取引合計金額|金額)[:：]?\s*(\d{1,3}(?:,\d{3})*)', content)
    date_match = re.search(r'(?:取引年月日|日付)[:：]?\s*(\d{4}[-/年]\d{1,2}[-/月]\d{1,2})', content)
    partner_match = re.search(r'(?:取引相手|相手)[:：]?\s*(.+)', content)
    
    amount = int(amount_match.group(1).replace(',', '')) if amount_match else None
    date = date_match.group(1) if date_match else None
    trading_partner = partner_match.group(1) if partner_match else None
    
    return {
        "amount": amount,
        "date": date,
        "trading_partner": trading_partner
    }

# JSON形式で出力して保存する関数
def save_response_as_json(response_data):
    if response_data is None:
        return
    
    extracted_info = extract_info_from_response(response_data)
    if extracted_info is None:
        print("情報の抽出に失敗しました。")
        return
    
    # 現在の日時を使ってファイル名を生成
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_file_name = f"response_{timestamp}.json"
    
    # JSONファイルの保存先パスを生成
    json_file_path = os.path.join(json_folder, json_file_name)
    
    # 抽出した情報をJSON形式で保存
    with open(json_file_path, "w", encoding='utf-8') as json_file:
        json.dump(extracted_info, json_file, ensure_ascii=False, indent=4)
    
    print(f"レスポンスが {json_file_path} に保存されました。")

# Base64エンコードされたコンテンツのリストを受け取り、処理する関数
def process_base64_list(base64_list):
    for base64_content in base64_list:
        # OpenAI APIを呼び出し
        response = call_openai_api(base64_content)
        # レスポンスをJSON形式で保存
        save_response_as_json(response)