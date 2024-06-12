import fitz  # PyMuPDF
import os
import argparse
from PIL import Image
from io import BytesIO

def save_image_as_jpeg(image_bytes, output_folder, image_filename):
    image = Image.open(BytesIO(image_bytes))
    jpeg_filename = os.path.splitext(image_filename)[0] + '.jpeg'
    jpeg_path = os.path.join(output_folder, jpeg_filename)
    image.convert("RGB").save(jpeg_path, "JPEG")
    return jpeg_filename

def extract_images(doc, page_num, output_folder):
    image_elements = []
    page = doc.load_page(page_num)
    image_list = page.get_images(full=True)
    
    for img_index, img in enumerate(image_list):
        xref = img[0]
        base_image = doc.extract_image(xref)
        image_bytes = base_image["image"]
        image_filename = f"image_{page_num+1}_{img_index+1}.jpeg"
        jpeg_filename = save_image_as_jpeg(image_bytes, output_folder, image_filename)
        image_elements.append({"type": "image", "content": jpeg_filename})
    
    return image_elements

def extract_text(page):
    text_elements = []
    blocks = page.get_text("dict")["blocks"]
    
    for block in blocks:
        if block["type"] == 0:  # Text block
            text_lines = block["lines"]
            for line in text_lines:
                spans = line["spans"]
                for span in spans:
                    text_elements.append({"type": "text", "content": span["text"]})
    
    return text_elements

def extract_elements_from_page(doc, page_num, output_folder):
    elements = []
    page = doc.load_page(page_num)
    blocks = page.get_text("dict")["blocks"]
    
    for block in blocks:
        if block["type"] == 0:  # Text block
            text_lines = block["lines"]
            for line in text_lines:
                spans = line["spans"]
                for span in spans:
                    elements.append({"type": "text", "content": span["text"]})
        elif block["type"] == 1:  # Image block
            image_elements = extract_images(doc, page_num, output_folder)
            elements.extend(image_elements)
        elif block["type"] == 2:  # Drawing block
            elements.append({"type": "drawing", "content": "Drawing content (not processed)"})
        elif block["type"] == 3:  # Unknown block
            elements.append({"type": "unknown", "content": "Unknown content (not processed)"})
    
    return elements

def extract_images_and_text(pdf_path, output_folder):
    doc = fitz.open(pdf_path)
    elements = []
    
    for page_num in range(len(doc)):
        page_elements = extract_elements_from_page(doc, page_num, output_folder)
        elements.extend(page_elements)
    
    return elements

def generate_html(elements, output_html_path):
    html_content = "<html><body>"
    
    for element in elements:
        if element["type"] == "text":
            html_content += "<p>{}</p>".format(element['content'].replace('\n', '<br>'))
        elif element["type"] == "image":
            html_content += '<img src="{}" alt="{}"><br>'.format(element["content"], element["content"])
        elif element["type"] == "drawing":
            html_content += "<p>{}</p>".format(element["content"])
        elif element["type"] == "unknown":
            html_content += "<p>{}</p>".format(element["content"])
    
    html_content += "</body></html>"
    
    with open(output_html_path, "w", encoding="utf-8") as html_file:
        html_file.write(html_content)

def main():
    parser = argparse.ArgumentParser(description="Convert PDF to HTML with extracted images.")
    parser.add_argument("--pdf", default="images/test1.pdf", help="Path to the PDF file.")
    args = parser.parse_args()

    pdf_path = args.pdf
    base_name = os.path.splitext(os.path.basename(pdf_path))[0]
    output_folder = base_name
    
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    elements = extract_images_and_text(pdf_path, output_folder)
    output_html_path = os.path.join(output_folder, f"{base_name}.html")
    
    generate_html(elements, output_html_path)
    print(f"HTML file created at: {output_html_path}")
    
if __name__ == "__main__":
    main()
