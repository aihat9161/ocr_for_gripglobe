import base64
import fitz  # PyMuPDF
import io
from PIL import Image
import os
import logging
import pandas as pd
import openpyxl
import docx
import pillow_heif  # HEIF/HEIC support for PIL
from ai_request import process_base64_list

# ログの設定
logging.basicConfig(filename="log.txt", level=logging.INFO, format='%(asctime)s - %(message)s')

# 画像ファイルをBase64形式に変換する関数
def image_to_base64(image_path):
    try:
        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
        logging.info(f"画像 {image_path} をBase64にエンコードしました。")
        return encoded_string
    except Exception as e:
        error_message = f"画像 {image_path} のエンコード中にエラーが発生しました: {e}"
        logging.error(error_message)
        return None

# HEIFファイルをBase64形式に変換する関数
def heif_to_base64(heif_path):
    try:
        heif_file = pillow_heif.open_heif(heif_path)
        img = Image.frombytes(heif_file.mode, heif_file.size, heif_file.data)
        
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
        logging.info(f"HEIFファイル {heif_path} をBase64にエンコードしました。")
        return img_str
    except Exception as e:
        error_message = f"HEIFファイル {heif_path} のエンコード中にエラーが発生しました: {e}"
        logging.error(error_message)
        return None

# PDFファイルを画像に変換し、各ページをBase64形式に変換する関数
def pdf_to_base64(pdf_path):
    try:
        doc = fitz.open(pdf_path)
        base64_images = []
        
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            pix = page.get_pixmap()
            img = Image.open(io.BytesIO(pix.tobytes("png")))
            
            buffered = io.BytesIO()
            img.save(buffered, format="PNG")
            logging.info(f"PDF {pdf_path} のページ {page_num + 1} をPNGに変換しました。")
            
            img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
            base64_images.append(img_str)
            logging.info(f"PNG {pdf_path} のページ {page_num + 1} をBase64にエンコードしました。")
        
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
        logging.info(f"Excelファイル {xlsx_path} からテキストを抽出し、Base64にエンコードしました。")
        return encoded_string
    except Exception as e:
        error_message = f"Excelファイル {xlsx_path} の処理中にエラーが発生しました: {e}"
        logging.error(error_message)
        return None

# .docファイルを処理する関数
def doc_to_base64(doc_path):
    try:
        doc = docx.Document(doc_path)
        full_text = []
        for para in doc.paragraphs:
            full_text.append(para.text)
        text_data = '\n'.join(full_text)
        encoded_string = base64.b64encode(text_data.encode('utf-8')).decode('utf-8')
        logging.info(f"Wordファイル {doc_path} からテキストを抽出し、Base64にエンコードしました。")
        return encoded_string
    except Exception as e:
        error_message = f"Wordファイル {doc_path} の処理中にエラーが発生しました: {e}"
        logging.error(error_message)
        return None

# ファイルタイプに応じて適切な処理を行う関数
def file_to_base64(file_path):
    file_extension = os.path.splitext(file_path)[1].lower()
    file_size = os.path.getsize(file_path)

    logging.info(f"ファイル取得: {file_path}, ファイルサイズ: {file_size} bytes")

    if file_extension == ".pdf":
        logging.info(f"{file_path} をPDFとして処理します。")
        return pdf_to_base64(file_path)
    elif file_extension in ['.jpg', '.jpeg', '.png']:
        logging.info(f"{file_path} を画像として処理します。")
        return [image_to_base64(file_path)]
    elif file_extension == ".heif" or file_extension == ".heic":
        logging.info(f"{file_path} をHEIFとして処理します。")
        return [heif_to_base64(file_path)]
    elif file_extension == ".xlsx":
        logging.info(f"{file_path} をExcelファイルとして処理します。")
        return [xlsx_to_base64(file_path)]
    elif file_extension == ".doc" or file_extension == ".docx":
        logging.info(f"{file_path} をWordファイルとして処理します。")
        return [doc_to_base64(file_path)]
    else:
        logging.error(f"未対応のファイル形式です: {file_path}")
        return []

# フォルダ内のすべてのファイルを処理する関数
def process_folder(folder_path):
    all_base64 = []
    processed_files = 0

    for root, dirs, files in os.walk(folder_path):
        for filename in files:
            file_path = os.path.join(root, filename)
            file_extension = os.path.splitext(filename)[1].lower()
            if file_extension in ['.jpg', '.jpeg', '.png', '.pdf', '.xlsx', '.doc', '.docx', '.heif', '.heic']:
                file_base64 = file_to_base64(file_path)
                for base64_data in file_base64:
                    all_base64.append((filename, base64_data))
                processed_files += 1
                logging.info(f"ファイル {filename} を処理しました。")

    logging.info(f"合計 {processed_files} 個のファイルを処理しました。")
    return all_base64
