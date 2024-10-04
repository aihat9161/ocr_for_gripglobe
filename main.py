import os
from convert_to_base64 import file_to_base64
from ai_request import call_openai_api, extract_info_from_response

# Define the input folder
input_folder = "input_testcase"

if __name__ == "__main__":
    # Loop through all files in the input_testcase folder
    for filename in os.listdir(input_folder):
        file_path = os.path.join(input_folder, filename)
        
        # Ensure it's a file (and not a directory)
        if os.path.isfile(file_path):
            base64_data = file_to_base64(file_path)
            
            # You can proceed with further steps such as sending the base64 to OpenAI API
            response = call_openai_api(base64_data)
            extracted_info = extract_info_from_response(response)
            print(extracted_info)
