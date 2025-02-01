import logging
from convert_to_base64 import data_to_base64
from ai_request import call_openai_api, extract_info_from_response
import json

# ログ設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def lambda_handler(event, context):
    # eventからバイナリデータを取得
    binary_data = event.get("binary_data")
    if not binary_data:
        return {
            "statusCode": 400,
            "body": json.dumps("バイナリデータが提供されていません")
        }
    
    result = main(binary_data)

    if isinstance(result, dict) and "error" in result:
        return {
            "statusCode": 500,
            "body": json.dumps(result["error"])
        }
    elif result:
        return {
            "statusCode": 200,
            "body": json.dumps(result)
        }
    else:
        return {
            "statusCode": 500,
            "body": json.dumps("不明なエラーが発生しました")
        }

def get_file_format(binary_data):
    header = binary_data[:4]
    
    if header.startswith(b'\xff\xd8\xff\xe0') or header.startswith(b'\xff\xd8\xff\xe1'):
        return 'jpg'
    elif header.startswith(b'\x89PNG'):
        return 'png'
    elif header.startswith(b'%PDF'):
        return 'pdf'
    elif header.startswith(b'PK'):
        return 'xlsx'
    else:
        return 'unsupported'

def main(binary_data):
    file_size = len(binary_data)
    file_format = get_file_format(binary_data)

    logging.info(f"ファイル形式：{file_format}, ファイルサイズ：{file_size} bytes")
    
    try:
        base64_images = data_to_base64(binary_data, file_format)
        if not base64_images:
            raise ValueError("ファイルのbase64変換に失敗しました")
    except Exception as e:
        error_message = f"base64変換中にエラーが発生しました: {e}"
        logging.error(error_message)
        return {"error": error_message}

    try:
        response = call_openai_api(base64_images)
        if response:
            logging.info("APIリクエスト成功")
        else:
            error_message = "APIリクエスト失敗"
            logging.error(error_message)
            return {"error": error_message}
    except Exception as e:
        error_message = f"APIリクエスト送信中にエラーが発生しました: {e}"
        logging.error(error_message)
        return {"error": error_message}

    try:
        extracted_info = extract_info_from_response(response)
        logging.info(extracted_info)
        return extracted_info
    except Exception as e:
        error_message = f"レスポンスから情報抽出中にエラーが発生しました: {e}"
        logging.error(error_message)
        return {"error": error_message}