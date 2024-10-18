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
                                画像から、次の情報を抽出してください：

                                1, 取引合計金額 (amount): 日本円で表され、カンマが含まれている場合はそのままカンマを保持する。例えば、「5,000円」「1,200円」のように表示されている金額。金額が認識できない場合は、何も返さない(null)。
                                2, 取引年月日 (date): YYYYMMDD形式で表示された日付。日付が取得できない場合は、何も返さない(null)。
                                3, 取引相手 (trading_partner): 「御中」「〜様」といった言葉の近くにある名前を優先して抽出する。請求元や発行者の情報ではなく、相手方の名前を抽出すること。取引相手が不明の場合、何も返さない(null)。
                                4, 登録番号 (Invoice Registration Number): Tと13桁の数字で構成される番号。郵便番号や請求書番号、Rから始まる番号、その他の番号は登録番号として扱わない。登録番号が見つからない場合、何も返さない(null)。

                                注意事項：
                                ・取得できないデータがある場合は、何も返さない(null)。ピリオドや空文字列、"null"を文字列として返すのではなく、必ず何も入力せずに返すこと。
                                ・推測は行わず、明確に取得できない場合は何も返さない(null)。
                                ・手書きの領収書の場合、取引相手は一番上に書かれている名前を優先して抽出する。
                                ・請求書番号や無関係な番号を誤って抽出しないようにする。
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
