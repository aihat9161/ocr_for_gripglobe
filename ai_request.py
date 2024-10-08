import requests
import json
import os
from datetime import datetime
import re

# OpenAIのAPIキーを設定 (環境変数から読み込み)
OPENAI_API_KEY = os.getenv("OPENAI_APIKEY")

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
                            "text": """
                                画像から、取引合計金額(amount)、取引年月日(date。YYYYMMDD形式)、取引相手(trading_partner)、および登録番号(Invoice Registration Number)を抽出する。
                                登録番号はTから始まり、少なくとも8桁以上の数字または英字で構成されるものとする。郵便番号や他の番号は登録番号として扱わないこと。請求書番号は登録番号ではないため、抽出しないこと。
                                取引相手は、請求書内の「御中」や「〜様」のような言葉の近くにある名前を優先して抽出すること。取引相手が「請求元」や「発行者」の情報である場合、それを取引相手として抽出しないこと。
                                請求書上の会社名や発行者名を除外し、相手の名前だけを取引相手として抽出すること。
                                請求書番号は登録番号ではないため、抽出しないこと。
                                手書きの領収書の場合、取引相手の名前は一番上に書かれていることが多いため、その部分を取得すること。金額は「5,000円」のように「,」が含まれる場合、そのままカンマを含む数値として認識してください。また、取引金額は日本円で表されているものとし、「1,000円」「2,500円」などカンマが正しく入っていることを期待しています。
                                もしそれぞれのpropertyの値が取得できない場合、必ずnullを返してください。推測は禁止です。
                                """
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
                            "trading_partner": { "type": "string" },
                            "invoice_registration_number": { "type": "string" }
                        },
                        "required": ["amount", "date", "trading_partner", "invoice_registration_number"],
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
        return
    
    extracted_info = extract_info_from_response(response_data)
    if extracted_info is None:
        print("情報の抽出に失敗しました。")
        return
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_file_name = f"response_{timestamp}.json"
    json_file_path = os.path.join(os.path.dirname(__file__), json_file_name)  # jsonsフォルダを使わず、現在のディレクトリに保存
    
    with open(json_file_path, "w", encoding='utf-8') as json_file:
        json.dump(extracted_info, json_file, ensure_ascii=False, indent=4)
    
    print(f"レスポンスが {json_file_path} に保存されました。")

# Base64エンコードされたコンテンツのリストを受け取り、処理する関数
def process_base64_list(base64_list):
    for base64_content in base64_list:
        response = call_openai_api(base64_content)
        save_response_as_json(response)
