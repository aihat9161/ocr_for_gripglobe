import os
import logging
from convert_to_base64 import file_to_base64
from ai_request import call_openai_api, extract_info_from_response

# ログ設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    folder_path = 'input_testcase'
    
    try:
        image_files = [f for f in os.listdir(folder_path) if f.endswith(('.png', '.jpg', '.jpeg', '.heif', '.pdf'))]
        
        if not image_files:
            logging.info("input_testcaseフォルダに画像ファイルが見つかりませんでした。")
            return
        
        for image_file in image_files:
            image_path = os.path.join(folder_path, image_file)
            file_size = os.path.getsize(image_path)
            file_format = image_file.split('.')[-1]
            logging.info(f"ファイル形式：{file_format}, ファイルサイズ：{file_size} bytes")

            try:
                base64_images = file_to_base64(image_path, file_format)
            except Exception as e:
                error_message = f"{image_file}のbase64変換中にエラーが発生しました: {e}"
                logging.error(error_message)
                continue
            
            try:
                logging.info(f"OpenAI APIにリクエスト送信中...")
                response = call_openai_api(base64_images)
                if response:
                    logging.info(f"APIリクエスト成功: {response}")
                else:
                    logging.error(f"APIリクエスト失敗: {response}")
            except Exception as e:
                error_message = f"{image_file}のAPIリクエスト送信中にエラーが発生しました: {e}"
                logging.error(error_message)
                continue
            
            try:
                extracted_info = extract_info_from_response(response)
                logging.info(f"抽出された情報: {extracted_info}")
                print(extracted_info)
            except Exception as e:
                error_message = f"{image_file}のレスポンスから情報抽出中にエラーが発生しました: {e}"
                logging.error(error_message)
                continue
    
    except Exception as e:
        logging.error(f"フォルダ処理中にエラーが発生しました: {e}")

if __name__ == "__main__":
    main()
