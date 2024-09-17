import base64
import fitz  # PyMuPDF
import io
from PIL import Image
import os
import logging
from ai_request import process_base64_list  # ai_request.py から関数をインポート

# ログの設定
logging.basicConfig(filename="log.txt", level=logging.INFO, format='%(asctime)s - %(message)s')

# 画像ファイルをBase64形式に変換する関数
def image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
    logging.info(f"Encoded image {image_path} to Base64.")  # ログに記録
    return encoded_string

# PDFファイルを画像に変換し、各ページをBase64形式に変換する関数 (PyMuPDFを使用)
def pdf_to_base64(pdf_path):
    doc = fitz.open(pdf_path)  # PDFを開く
    base64_images = []
    
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)  # 各ページをロード
        pix = page.get_pixmap()  # ページをピクセルマップに変換
        img = Image.open(io.BytesIO(pix.tobytes("png")))  # PILで画像として読み込み
        
        # 画像データをメモリに一時保存
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        
        # Base64エンコード
        img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
        base64_images.append(img_str)
        logging.info(f"Encoded page {page_num + 1} of {pdf_path} to Base64.")  # 各ページをログに記録
    
    return base64_images

# ファイルタイプに応じて適切な処理を行う関数
def file_to_base64(file_path):
    file_extension = os.path.splitext(file_path)[1].lower()
    
    if file_extension == ".pdf":
        logging.info(f"Processing {file_path} as PDF.")
        return pdf_to_base64(file_path)
    else:
        logging.info(f"Processing {file_path} as image.")
        return [image_to_base64(file_path)]

# ファイルをBase64に変換し、ログに記録
file_base64 = file_to_base64("/Users/higuchiyoshikazu/外部プロジェクト/AIHAT/ocr_for_gripglobe/input_testcase/images/invoice.jpg")  # 画像またはPDFのパス

for idx, encoded_str in enumerate(file_base64):
    logging.info(f"Base64 string for file part {idx + 1}: {encoded_str}")  # 省略せずに記録

# Base64エンコードが完了したら、OpenAI API処理を呼び出す
print("Encoding completed. Calling OpenAI API...")

# Base64リストをOpenAIリクエストの処理に渡す
process_base64_list(file_base64)  # ai_request.pyの関数を呼び出す
