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
                                以下の項目を画像から正確に抽出してください。データが不明または推測される場合はnullを返し、.や/、または無関係なプレースホルダを返さないでください。しっかりと数字や文字を認識し、誤りのない抽出を目指してください。
                                    1,取引合計金額 (amount)
                                    表示されている金額の中で、取引全体の合計を抽出してください。「お預かり」や「預金」項目の金額を除外してください。
                                    金額はカンマをそのまま含めず、"¥"を誤って"7"などの数字に変換しないでください。例: ¥5,000円 => 5000。
                                    金額がない場合や認識できない場合はnullを返してください。

                                    2,取引年月日 (date)
                                    日付はYYYYMMDDの形式で抽出し、和暦（例: R6など）は西暦に変換してください。例: R6は2024年。
                                    日付が正確に認識できない場合はnullを返し、数字以外の文字を含まないようにしてください。

                                    3,取引相手 (trading_partner)
                                    「御中」や「～様」などの敬称が近くにある場合、その名称を優先して取引相手としてください。また、会社名や店舗名が書かれている場合にはそれを抽出してください。
                                    取引相手が手書きの場合、手書きの部分も読み取ってください。
                                    左上や上部に書かれている会社名や店舗名も確認し、それらが取引相手として適切であれば抽出してください。
                                    判別できない場合はnullを返し、余分なプレースホルダ（.や/）を使用しないでください。

                                    4,登録番号 (Invoice Registration Number)
                                    "T"から始まる13桁の番号を抽出してください。T以外から始まる番号や、"/"が含まれるもの、郵便番号や請求書番号、領収書番号、Rから始まる番号は無視してください。
                                    "T"の直後に13桁の数字が続くものだけを抽出し、正確に13桁あることを確認してください。文字数が異なる場合や、余分な文字が混ざっている場合は無効とし、nullを返してください。
                                    登録番号に連続するゼロが不足しないように、正確に抽出してください。例えば、"T0000000000000"は正確にそのまま認識するようにしてください。

                                注意事項:
                                    書かれている内容を推測せず、可能な限り正確に読み取ってください。数字や文字を逆に読み取らないように気をつけてください。
                                    ¥が横線2本である場合なども含め、金額の通貨記号が誤って他の文字に変換されないようにしてください。
                                    もしブレやかすれがある場合でも、明確に読める部分を優先して抽出し、正確に記録してください。
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
