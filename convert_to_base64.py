import base64
import fitz  # PyMuPDF
import io
from PIL import Image
import os
import logging
import pandas as pd
import openpyxl

# ログの設定
logging.basicConfig(filename="log.txt", level=logging.INFO, format='%(asctime)s - %(message)s')

# 画像ファイルをBase64形式に変換する関数
def image_to_base64(image_path):
    try:
        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
        return encoded_string
    except Exception as e:
        error_message = f"画像 {image_path} のエンコード中にエラーが発生しました: {e}"
        logging.error(error_message)
        return None

# PDFファイルを画像に変換し、各ページをBase64形式に変換する関数
def pdf_to_base64(pdf_path, file_format):
    try:
        doc = fitz.open(pdf_path)
        base64_images = []
        
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            pix = page.get_pixmap()
            img = Image.open(io.BytesIO(pix.tobytes("png")))
            
            buffered = io.BytesIO()
            img.save(buffered, format="PNG")
            logging.info(f"{file_format}から画像への変換が完了しました。")
            
            img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
            base64_images.append(img_str)
    
        return base64_images
    except Exception as e:
        error_message = f"PDF {pdf_path} の処理中にエラーが発生しました: {e}"
        logging.error(error_message)
        return []

# .xlsxファイルを処理する関数
def xlsx_to_base64(xlsx_path):
    try:
        df = pd.read_excel(xlsx_path)
        text_data = df.to_string(index=False)
        encoded_string = base64.b64encode(text_data.encode('utf-8')).decode('utf-8')
        return encoded_string
    except Exception as e:
        error_message = f"Excelファイル {xlsx_path} の処理中にエラーが発生しました: {e}"
        logging.error(error_message)
        return None

# ファイルタイプに応じて適切な処理を行う関数
def file_to_base64(file_path, file_format):
    file_extension = os.path.splitext(file_path)[1].lower()

    if file_extension == ".pdf":
        return pdf_to_base64(file_path, file_format)
    elif file_extension in ['.jpg', '.jpeg', '.png']:
        return [image_to_base64(file_path)]
    elif file_extension == ".xlsx":
        return [xlsx_to_base64(file_path)]
    else:
        print(f"未対応のファイル形式です: {file_path}")
        logging.error(f"未対応のファイル形式です: {file_path}")
        return []