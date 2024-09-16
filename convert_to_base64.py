import base64
import fitz  # PyMuPDF
import io
from PIL import Image
import logging

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

# 画像ファイルをBase64に変換し、ログに記録
image_base64 = image_to_base64("path/to/image.jpg")  # 画像ファイルのパスを指定
logging.info(f"Base64 string for image: {image_base64}")  # 省略せずに記録

# PDFを画像に変換し、Base64に変換してログに記録
pdf_base64_list = pdf_to_base64("path/to/document.pdf")  # PDFファイルのパスを指定
for idx, img_base64 in enumerate(pdf_base64_list):
    logging.info(f"Base64 string for PDF page {idx + 1}: {img_base64}")  # 省略せずに記録

print("Encoding completed. Check log.txt for details.")
