import os
import logging
from convert_to_base64 import file_to_base64
from ai_request import call_openai_api, extract_info_from_response

# ログ設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    folder_path = 'input_testcase'
    
    image_files = [f for f in os.listdir(folder_path) if f.endswith(('.png', '.jpg', '.jpeg', '.heif', '.pdf'))]
    
    if not image_files:
        logging.info("input_testcaseフォルダに画像ファイルが見つかりませんでした。")
        return
    
    for image_file in image_files:
        image_path = os.path.join(folder_path, image_file)
        
        logging.info(f"{image_file}をbase64に変換中...")
        base64_images = file_to_base64(image_path)
        
        logging.info(f"OpenAI APIにリクエスト送信中...")
        response = call_openai_api(base64_images)
        
        logging.info(f"レスポンスから情報を抽出中...")
        extracted_info = extract_info_from_response(response)
        
        logging.info(f"抽出された情報: {extracted_info}")
        print(extract_info_from_response(response))

if __name__ == "__main__":
    main()
