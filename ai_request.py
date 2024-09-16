from openai import OpenAI
import json
import os
from datetime import datetime

# OpenAIのAPIキーを設定
  # 必要に応じてAPIキーを更新してください
client = OpenAI(api_key="Enter your API key here")  #  APIキーを入力

# 生成されたjsonファイルの保存先フォルダを設定
json_folder = "jsons"

# jsonsフォルダが存在しない場合は作成
if not os.path.exists(json_folder):
    os.makedirs(json_folder)

# OpenAI APIを呼び出す関数
def call_openai_api(base64_content):
    try:
        # APIにリクエストを送信
        response = client.chat.completions.create(model="gpt-4o-2024-08-06",
        messages=[
            {"role": "system", "content": "You are an assistant."},
            {"role": "user", "content": f"Analyze the following Base64-encoded content: {base64_content}"}
        ],
        max_tokens=150)
        return response.to_dict()  # レスポンスを辞書に変換して返す
    except Exception as e:
        print(f"Error calling OpenAI API: {e}")
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

    print(f"Response saved to {json_file_path}")

# Base64エンコードされたコンテンツのリストを受け取り、処理する関数
def process_base64_list(base64_list):
    for base64_content in base64_list:
        # OpenAI APIを呼び出し
        response = call_openai_api(base64_content)

        # レスポンスをJSON形式で保存
        save_response_as_json(response)

# ファイル名を変更し、'convert_to_base64.py' からBase64リストをインポート
from convert_to_base64 import file_to_base64

# ファイルパスを指定してBase64リストを取得
base64_list = file_to_base64("/path/to/your/image_or_pdf")  # 画像やPDFのパスを指定

# Base64リストを処理し、OpenAI APIを呼び出して結果を保存
process_base64_list(base64_list)
