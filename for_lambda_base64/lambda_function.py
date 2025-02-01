import logging
from convert_to_base64 import data_to_base64
from ai_request import call_openai_api, extract_info_from_response
import json
import base64

# ログ設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def lambda_handler(event, context):
    # リクエスト全体をログに記録
    logging.info(f"Received event: {json.dumps(event)}")

    # eventからbase64エンコードデータを取得
    base64_data = event.get("base64_data")
    if not base64_data:
        return {
            "statusCode": 400,
            "body": json.dumps("base64エンコードデータが提供されていません")
        }
    
    # 受け取ったbase64データの一部をログ出力
    logging.info(f"Received base64_data: {base64_data[:30]}...")

    # Data URL形式の処理
    if base64_data.startswith("data:"):
        try:
            header, encoded = base64_data.split(",", 1)
            # MIMEタイプからファイル形式を判断
            mime_type = header.split(";")[0].split(":")[1]
            if mime_type == "image/png":
                file_format = "png"
            elif mime_type == "image/jpeg":
                file_format = "jpg"
            elif mime_type == "application/pdf":
                file_format = "pdf"
            elif mime_type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
                file_format = "xlsx"
            else:
                return {
                    "statusCode": 400,
                    "body": json.dumps("サポートされていないMIMEタイプです")
                }
            # base64エンコード部分をデコード
            binary_data = base64.b64decode(encoded)
        except Exception as e:
            logging.error(f"base64データの解析中にエラーが発生しました: {e}")
            return {
                "statusCode": 400,
                "body": json.dumps(f"base64データの解析中にエラーが発生しました: {e}")
            }
    else:
        # Data URL形式ではない場合の処理
        try:
            binary_data = base64.b64decode(base64_data)
            file_format = get_file_format(binary_data)
        except Exception as e:
            logging.error(f"base64データの解析中にエラーが発生しました: {e}")
            return {
                "statusCode": 400,
                "body": json.dumps(f"base64データの解析中にエラーが発生しました: {e}")
            }
    
    result = main(binary_data, file_format)

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

def main(binary_data, file_format):
    file_size = len(binary_data)
    
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
