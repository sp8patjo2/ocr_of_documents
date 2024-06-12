import fitz  # PyMuPDF
import os
import argparse
from PIL import Image

def extract_images(pdf_path, output_folder):
    doc = fitz.open(pdf_path)
    image_paths = []
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        image_list = page.get_images(full=True)
        
        for image_index, img in enumerate(image_list):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]
            image_filename = f"image_{page_num+1}_{image_index+1}.{image_ext}"
            image_path = os.path.join(output_folder, image_filename)
            with open(image_path, "wb") as img_file:
                img_file.write(image_bytes)
            image_paths.append(image_filename)
    
    return image_paths

def extract_text(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        text += page.get_text()
    
    return text

def generate_html(text, image_paths, output_html_path):
    html_content = "<html><body>"
    html_content += "<p>{}</p>".format(text.replace("\n", "<br>"))
    
    for image_path in image_paths:
        html_content += f'<img src="{image_path}" alt="{image_path}"><br>'
    
    html_content += "</body></html>"
    
    with open(output_html_path, "w", encoding="utf-8") as html_file:
        html_file.write(html_content)

def main(pdf_path):
    base_name = os.path.splitext(os.path.basename(pdf_path))[0]
    output_folder = base_name
    
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    text = extract_text(pdf_path)
    image_paths = extract_images(pdf_path, output_folder)
    output_html_path = os.path.join(output_folder, f"{base_name}.html")
    
    generate_html(text, image_paths, output_html_path)
    print(f"HTML file created at: {output_html_path}")
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert PDF to HTML with extracted images.")
    parser.add_argument("--pdf", required=True,default='images/test1.pdf' help="Path to the PDF file.")
    args = parser.parse_args()
    
    main(args.pdf)
