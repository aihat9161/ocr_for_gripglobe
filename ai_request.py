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
            "model": "gpt-4o-2024-08-06",
            "messages": [
                {"role": "system", "content": "あなたはアシスタントです。"},
                {"role": "user", "content": "以下の画像から取引合計金額、取引年月日、取引相手を抽出してください。"},
                {"role": "user", "content": f"データ: {base64_content}"}
            ],
            "max_tokens": 150,
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": "invoice_extraction",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "amount": {"type": "integer"},
                            "day": {"type": "integer"},
                            "trading_partner": {"type": "string"}
                        },
                        "required": ["amount", "day", "trading_partner"],
                        "additionalProperties": False
                    },
                    "strict": True
                }
            }
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

# JSON形式で出力して保存する関数
def save_response_as_json(response_data):
    if response_data is None:
        return

    # 現在の日時を使ってファイル名を生成
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_file_name = f"response_{timestamp}.json"

    # JSONファイルの保存先パスを生成
    json_file_path = os.path.join(json_folder, json_file_name)

    # APIからのレスポンスをJSON形式で保存
    with open(json_file_path, "w", encoding='utf-8') as json_file:
        json.dump(response_data, json_file, ensure_ascii=False, indent=4)

    print(f"レスポンスが {json_file_path} に保存されました。")

# Base64エンコードされたコンテンツのリストを受け取り、処理する関数
def process_base64_list(base64_list):
    for base64_content in base64_list:
        # OpenAI APIを呼び出し
        response = call_openai_api(base64_content)

        # レスポンスをJSON形式で保存
        save_response_as_json(response)
