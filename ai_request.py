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
                                ・取引合計金額 (amount): 日本円で表され、カンマが含まれている場合はそのままカンマを保持する。表示されている金額が合計金額であることを確認してください。「お預かり」や「預金」は無視してください。金額が認識できない場合、nullを返す。
                                ・取引年月日 (date): YYYYMMDD形式で表示された日付。和暦（R6など）は西暦（令和6年は2024年）に変換してください。日付が取得できない場合、nullを返す。
                                ・取引相手 (trading_partner): 「御中」や「〜様」といった言葉の近くにある名前を優先して抽出する。また、会社名や店舗名（例: セブンイレブン）が上部に書かれている場合はそれを取引相手として認識する。取引相手が不明の場合、nullを返す。
                                ・登録番号 (Invoice Registration Number): "T"から始まる13桁の数字で構成された番号。T以外から始まる番号や、"/"が含まれている番号、郵便番号、請求書番号、領収書番号、Rから始まる番号は無視してください。登録番号が見つからない場合、nullを返す。

                                注意事項:
                                ・不明確なデータや推測されるデータはnullを返してください。"/"や"."などのプレースホルダを返さないでください。
                                ・取引相手の抽出が困難な場合、特に上部に書かれている会社名や店舗名を優先してください。
                                ・和暦の変換には注意し、R6（令和6年）は2024年として認識するようにしてください。
                                ・合計金額は「お預かり」や「預金」の金額ではなく、取引全体の合計を選んでください。
                                ・不適切な番号や形式のデータ（領収書番号や"/"が含まれる番号など）は登録番号として返さないでください。
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
