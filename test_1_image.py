from ai_request import call_openai_api, extract_info_from_response
from convert_to_base64 import file_to_base64

def test_1_image():
    file_path = "input_testcase/MMAデザインコンサルティング様_請求書_v2_20240703.pdf のコピー.pdf"
    base64_data = file_to_base64(file_path)
    response = call_openai_api(base64_data)
    print(response)
    extracted_info = extract_info_from_response(response)
    print(extracted_info)

if __name__ == "__main__":
    test_1_image()

