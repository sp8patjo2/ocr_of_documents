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

def extract_elements_from_page(doc, page_num, output_folder):
    elements = []
    page = doc.load_page(page_num)
    blocks = page.get_text("dict")["blocks"]
    
    
    sorted_blocks = sorted(blocks, key=lambda block: block["bbox"][1])  # for debug - sort on first Y coordinate, easier to compare if texts are in the correct order
    for block in sorted_blocks:
        debug2 = block["type"]
        print(block["bbox"])
        print(block["bbox"][1])
    
        
        print(f"debug: block-type: {debug2}")
        if block["type"] == 0:  # Text block
            text_lines = block["lines"]
            for line in text_lines:
                spans = line["spans"]
                for span in spans:
                    debug = span["text"]
                    print(f"debug - text i denna position är: \"{debug}\"")
                    elements.append({
                        "type": "text",
                        "content": span["text"],
                        "bbox": block["bbox"]
                    })
                    debug2 = block["bbox"][1]
                    print(f"debug - y-position är: \"{debug2}\"")

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
    
    sorted_elements = sorted(elements, key=lambda elements: elements["bbox"][1])    
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
    parser = argparse.ArgumentParser(description="Convert PDF to HTML with extracted images.")
    parser.add_argument("--pdf", default="images/test1.pdf", help="Path to the PDF file.")
    args = parser.parse_args()

    pdf_path = args.pdf
    base_name = os.path.splitext(os.path.basename(pdf_path))[0]
    output_folder = base_name
    
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    pages_elements = extract_images_and_text(pdf_path, output_folder)
    output_html_path = os.path.join(output_folder, f"{base_name}.html")
    
    generate_html(pages_elements, output_html_path)
    print(f"HTML file created at: {output_html_path}")
    
if __name__ == "__main__":
    main()
