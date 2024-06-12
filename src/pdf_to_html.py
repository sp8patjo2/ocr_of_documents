import fitz  # PyMuPDF
from fitz import Page
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

def extract_images(doc, page, output_folder, page_num):
    image_elements = []
    #page.clean_contents()  # https://pymupdf.readthedocs.io/en/latest/functions.html#Page.clean_contents
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
        
        image_elements.append({
            "type": "image",
            "content": jpeg_filename,
            "bbox": [bbox.x0, bbox.y0, bbox.x1, bbox.y1]  # Extracting coordinates from bbox
        })
    
    print(f"Extracted {len(image_elements)} images from page {page_num + 1}")
    return image_elements

def extract_text(block):
    text_elements = []
    text_lines = block["lines"]
    for line in text_lines:
        spans = line["spans"]
        for span in spans:
            text_elements.append({
                "type": "text",
                "content": span["text"],
                "bbox": block["bbox"]
            })
    
    return text_elements

def extract_elements_from_page(doc, page_num, output_folder):
    elements = []
    page = doc.load_page(page_num)
    blocks = page.get_text("dict")["blocks"]
    
    for block in blocks:
        if block["type"] == 0:  # Text block
            text_elements = extract_text(block)
            elements.extend(text_elements)
    
    # Extract images separately after processing text blocks
    image_elements = extract_images(doc, page, output_folder, page_num)
    elements.extend(image_elements)
    
    return elements

def extract_images_and_text(pdf_path, output_folder):
    doc = fitz.open(pdf_path)
    elements = []
    
    for page_num in range(len(doc)):
        page_elements = extract_elements_from_page(doc, page_num, output_folder)
        elements.extend(page_elements)
    

    # Filter elements to ensure all have valid bbox
    filtered_elements = []
    for e in elements:
        print(f"Before filtering: Element type: {e['type']}, content: {e.get('content', '')}, bbox: {e['bbox']}")
        if e["type"] == "image":
            debug =1
        if isinstance(e["bbox"], (list, tuple)) and len(e["bbox"]) >= 2:
            filtered_elements.append(e)
        else:
            print(f"Filtered out: Element type: {e['type']}, content: {e.get('content', '')}, bbox: {e['bbox']}")
    

    # Sort elements by their position (bbox)
    sorted_elements = []
    for e in filtered_elements:
        inserted = False
        for i, se in enumerate(sorted_elements):
            if (e["bbox"][1], e["bbox"][0]) < (se["bbox"][1], se["bbox"][0]):
                sorted_elements.insert(i, e)
                inserted = True
                break
        if not inserted:
            sorted_elements.append(e)
    
    # Debugging print to check sorted elements
    for element in sorted_elements:
        print(f"After sorting: Element type: {element['type']}, content: {element.get('content', '')}, bbox: {element['bbox']}")
    
    return sorted_elements

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
