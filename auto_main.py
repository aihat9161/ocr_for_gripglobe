import os
import logging
from convert_to_base64 import file_to_base64  # 正しい関数名を使用
from ai_request import call_openai_api, extract_info_from_response

# ログ設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
file_path = 'input_testcase/一時保存'

def main(path):
    for pathname, dirnames, filenames in os.walk(path):
        for filename in filenames:
            file = os.path.join(pathname, filename)

            try:
                supported_formats = ('.png', '.jpg', '.jpeg', '.heif', '.pdf', '.xlsx')
                
                # ファイル形式チェック
                if not filename.lower().endswith(supported_formats):
                    logging.error(f"未対応のファイル形式です: {file}")
                    continue
                
                # ファイルサイズと形式をログ出力
                file_size = os.path.getsize(file)
                file_format = filename.split('.')[-1]
                logging.info(f"ファイル形式：{file_format}, ファイルサイズ：{file_size} bytes")

                try:
                    # base64に変換
                    base64_data = file_to_base64(file, file_format)  # 修正
                    logging.info(base64_data)
                    if not base64_data:
                        logging.error(f"ファイルのbase64変換に失敗しました: {file}")
                        continue
                except Exception as e:
                    logging.error(f"{file}のbase64変換中にエラーが発生しました: {e}")
                    continue

                try:
                    # OpenAI APIリクエスト
                    logging.info(f"OpenAI APIにリクエスト送信中...")
                    response = call_openai_api(base64_data)
                    if response:
                        logging.info(f"APIリクエスト成功: {response}")
                    else:
                        logging.error(f"APIリクエスト失敗: {response}")
                except Exception as e:
                    logging.error(f"{file}のAPIリクエスト送信中にエラーが発生しました: {e}")
                    continue

                try:
                    # レスポンスから情報抽出
                    extracted_info = extract_info_from_response(response)
                    logging.info(f"抽出された情報: {extracted_info}")
                    print(extracted_info)
                except Exception as e:
                    logging.error(f"{file}のレスポンスから情報抽出中にエラーが発生しました: {e}")
                    continue

            except Exception as e:
                logging.error(f"ファイル処理中にエラーが発生しました: {e}")

if __name__ == "__main__":
    main(file_path)
