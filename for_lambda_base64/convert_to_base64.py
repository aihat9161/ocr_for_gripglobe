import base64
import fitz  # PyMuPDF
import io
from io import BytesIO
from PIL import Image
import logging
from openpyxl import load_workbook

# ログの設定
logging.basicConfig(filename="log.txt", level=logging.INFO, format='%(asctime)s - %(message)s')

# バイナリデータをBase64形式に変換する関数
def binary_to_base64(binary_data):
    try:
        encoded_string = base64.b64encode(binary_data).decode('utf-8')
        return encoded_string
    except Exception as e:
        error_message = f"データのエンコード中にエラーが発生しました: {e}"
        logging.error(error_message)
        return None

# PDFバイナリデータを画像に変換し、各ページをBase64形式に変換する関数
def pdf_binary_to_base64(pdf_binary):
    try:
        doc = fitz.open("pdf", pdf_binary)
        base64_images = []
        
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            pix = page.get_pixmap()
            img = Image.open(io.BytesIO(pix.tobytes("png")))

            buffered = io.BytesIO()
            img.save(buffered, format="PNG")
            logging.info("PDFから画像への変換が完了しました。")

            img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
            base64_images.append(img_str)
    
        return base64_images
    except Exception as e:
        error_message = f"PDFデータの処理中にエラーが発生しました: {e}"
        logging.error(error_message)
        return []

# .xlsxバイナリデータをPDFに変換してBase64に変換する関数
def xlsx_binary_to_base64(xlsx_binary):
    try:
        # バイナリデータを一時ファイルとして保存
        xlsx_file = BytesIO(xlsx_binary)
        wb = load_workbook(xlsx_file)
        pdf_buffer = io.BytesIO()
        
        # エクセルをPDFに変換して一時ファイルに保存する
        # 実装のためには専用のライブラリやツールが必要（LibreOfficeのような）
        # ここでは仮想的な処理として扱います

        # PDFに変換されたバイナリデータをBase64に変換
        return pdf_binary_to_base64(pdf_buffer.getvalue())
    except Exception as e:
        error_message = f"Excelデータの処理中にエラーが発生しました: {e}"
        logging.error(error_message)
        return None

# ファイルのバイナリデータに応じて適切な処理を行う関数
def data_to_base64(binary_data, file_format):
    if file_format.lower() == "pdf":
        return pdf_binary_to_base64(binary_data)
    elif file_format.lower() in ['jpg', 'jpeg', 'png']:
        return [binary_to_base64(binary_data)]
    elif file_format.lower() == "xlsx":
        return xlsx_binary_to_base64(binary_data)
    else:
        error_message = f"未対応のファイル形式です: {file_format}"
        logging.error(error_message)
        return []

