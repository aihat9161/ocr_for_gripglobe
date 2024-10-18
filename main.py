import logging
from convert_to_base64 import data_to_base64
from ai_request import call_openai_api, extract_info_from_response

# ログ設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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
    
    # 拡張子を取得
    file_format = get_file_format(binary_data)
    
    # ログにファイル形式とサイズを出力
    logging.info(f"ファイル形式：{file_format}, ファイルサイズ：{file_size} bytes")
    
    try:
        base64_images = data_to_base64(binary_data, file_format)
        if not base64_images:
            error_message = f"ファイルのbase64変換に失敗しました"
            logging.error(error_message)
            return
    except Exception as e:
        error_message = f"base64変換中にエラーが発生しました: {e}"
        logging.error(error_message)
        return

    try:
        response = call_openai_api(base64_images)
        if response:
            logging.info(f"APIリクエスト成功")
            logging.info(response)
        else:
            logging.error(f"APIリクエスト失敗")
            return
    except Exception as e:
        error_message = f"APIリクエスト送信中にエラーが発生しました: {e}"
        logging.error(error_message)
        return

    try:
        extracted_info = extract_info_from_response(response)
        logging.info(extracted_info)
    except Exception as e:
        error_message = f"レスポンスから情報抽出中にエラーが発生しました: {e}"
        logging.error(error_message)
        return