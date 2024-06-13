import fitz  # PyMuPDF
import os
import argparse
from PIL import Image
from io import BytesIO
import logging
from dotenv import load_dotenv
load_dotenv()  # Ladda variabler från .env-filen
logger = None

def setup_logger(log_level):
    logger = logging.getLogger("pdf_to_html_converter")
    logger.setLevel(log_level)
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger



def save_image_as_jpeg(image_bytes, output_folder, image_filename):
    image = Image.open(BytesIO(image_bytes))
    jpeg_filename = os.path.splitext(image_filename)[0] + '.jpeg'
    jpeg_path = os.path.join(output_folder, jpeg_filename)
    image.convert("RGB").save(jpeg_path, "JPEG")
    return jpeg_filename


def extract_elements_from_page(doc, page_num, output_folder):
    elements = []
    page = doc.load_page(page_num)
    blocks = page.get_text("dict")["blocks"]
    
    y_tolerance = 2  # Tolerans i y-led

    def find_matching_element(elements, y_pos, y_tolerance):
        for element in elements:
            if element["type"] == "text" and abs(element["bbox"][1] - y_pos) <= y_tolerance:
                return element
        return None

    for block in blocks:
        if block["type"] == 0:  # Text block
            text_lines = block["lines"]
            for line in text_lines:
                spans = line["spans"]
                for span in spans:
                    y_pos = block["bbox"][1]
                    matching_element = find_matching_element(elements, y_pos, y_tolerance)
                    if matching_element:
                        matching_element["content"] += " " + span["text"]
                    else:

                        elements.append({
                            "type": "text",
                            "content": span["text"],
                            "bbox": block["bbox"]
                        })

    image_list = page.get_images(full=True)
    for img_index, img in enumerate(image_list):
        xref = img[0]
        
        if not isinstance(xref, int):
            raise TypeError(f"Expected xref to be an int, but got {type(xref).__name__}")
        
        base_image = doc.extract_image(xref)
        image_bytes = base_image["image"]
        image_filename = f"image_{page_num+1}_{img_index+1}.jpeg"
        jpeg_filename = save_image_as_jpeg(image_bytes, output_folder, image_filename)
        
        # Get the bounding box for the image
        bbox = page.get_image_bbox(img)
        
        elements.append({
            "type": "image",
            "content": jpeg_filename,
            "bbox": [bbox.x0, bbox.y0, bbox.x1, bbox.y1]
        })
    
    sorted_elements = sorted(elements, key=lambda element: element["bbox"][1])
    return sorted_elements



def extract_images_and_text(pdf_path, output_folder):
    doc = fitz.open(pdf_path)
    pages_elements = []
    
    for page_num in range(len(doc)):
        page_elements = extract_elements_from_page(doc, page_num, output_folder)
        pages_elements.append(page_elements)
    
    return pages_elements

def generate_html(pages_elements, output_html_path):
    html_content = "<html><body>"
    
    for page_num, elements in enumerate(pages_elements):
        html_content += f'<div class="page" id="page_{page_num+1}">'
        for element in elements:
            if element["type"] == "text":
                html_content += '<p>{}</p>'.format(element['content'].replace('\n', '<br>'))
            elif element["type"] == "image":
                html_content += '<img src="{}" alt="{}"><br>'.format(element["content"], element["content"])
        html_content += '</div><div style="page-break-after: always;"></div>'
    
    html_content += "</body></html>"
    
    with open(output_html_path, "w", encoding="utf-8") as html_file:
        html_file.write(html_content)


def main():
    #setup logging    
    log_level_str = os.getenv('LOG_LEVEL', 'WARNING').upper()
    log_level = getattr(logging, log_level_str, logging.WARNING)
    global logger
    logger = setup_logger(log_level)

    # parse arguments
    parser = argparse.ArgumentParser(description="Convert PDF to HTML with extracted images.")
    parser.add_argument("--pdf", default="images/test1.pdf", help="Path to the PDF file.")
    args = parser.parse_args()

    # doit
    pdf_path = args.pdf
    base_name = os.path.splitext(os.path.basename(pdf_path))[0]
    output_folder = base_name
    
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    logger.info("Starting PDF to HTML conversion.")
    pages_elements = extract_images_and_text(pdf_path, output_folder)
    output_html_path = os.path.join(output_folder, f"{base_name}.html")
    
    generate_html(pages_elements, output_html_path)
    logger.info(f"HTML file created at: {output_html_path}")
    
if __name__ == "__main__":
    main()
