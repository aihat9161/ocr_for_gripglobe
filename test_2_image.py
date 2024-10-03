import os
from ai_request import call_openai_api, extract_info_from_response
from convert_to_base64 import file_to_base64

# 指定したフォルダ内およびサブフォルダ内の全ファイルを処理する関数
def process_all_files_in_folder(folder_path):
    # フォルダを再帰的に探索
    for root, dirs, files in os.walk(folder_path):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            # ファイルをbase64に変換してAPIリクエストを行う
            base64_data = file_to_base64(file_path)
            response = call_openai_api(base64_data)
            print(f"ファイル: {file_name}")
            # print(f"APIレスポンス: {response}")
            extracted_info = extract_info_from_response(response)
            print(f"抽出された情報: {extracted_info}\n")

# テスト関数
def test_all_images_in_folder():
    folder_path = "input_testcase"
    process_all_files_in_folder(folder_path)

if __name__ == "__main__":
    test_all_images_in_folder()
