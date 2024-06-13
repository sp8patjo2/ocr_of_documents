# classes/pdf_to_html_converter.py

import fitz  # PyMuPDF
import os
from PIL import Image
from io import BytesIO
from typing import List, Dict, Any
import logging

class PDFToTextAndImages:
    def __init__(self, logger: logging.Logger):
        self._logger = logger

    def _save_image_as_jpeg(self, image_bytes: bytes, output_folder: str, image_filename: str) -> str:
        image = Image.open(BytesIO(image_bytes))
        jpeg_filename = os.path.splitext(image_filename)[0] + '.jpeg'
        jpeg_path = os.path.join(output_folder, jpeg_filename)
        image.convert("RGB").save(jpeg_path, "JPEG")
        return jpeg_filename

    def _save_vector_as_svg(self, page: fitz.Page, block: Dict[str, Any], output_folder: str, svg_filename: str) -> str:
        self._logger.warning("SVG is not tested. Please double check the result")
        svg_path = os.path.join(output_folder, svg_filename)
        with open(svg_path, "w") as svg_file:
            svg_file.write(page.get_svg_image(block))
        return svg_filename

    def _find_matching_element(self, elements: List[Dict[str, Any]], y_pos: float, y_tolerance: float) -> Dict[str, Any]:
        for element in elements:
            if element["type"] == "text" and abs(element["bbox"][1] - y_pos) <= y_tolerance:
                return element
        return None

    def _extract_text_elements_from_page(self, block: Dict[str, Any], elements: List[Dict[str, Any]], y_tolerance: float) -> None:
        text_lines = block["lines"]
        for line in text_lines:
            spans = line["spans"]
            for span in spans:
                y_pos = block["bbox"][1]
                matching_element = self._find_matching_element(elements, y_pos, y_tolerance)
                if matching_element:
                    matching_element["content"] += " " + span["text"]
                else:
                    elements.append({
                        "type"      : "text",
                        "content"   : span["text"],
                        "bbox"      : block["bbox"],
                        "font_size" : span["size"],
                        "font"      : span["font"]
                    })

    def _extract_image_elements_from_page(self, doc: fitz.Document, page: fitz.Page, page_num: int, output_folder: str, elements: List[Dict[str, Any]]) -> None:
        image_list = page.get_images(full=True)
        for img_index, img in enumerate(image_list):
            xref = img[0]
            base_image     = doc.extract_image(xref)
            image_bytes    = base_image["image"]
            image_filename = f"image_{page_num+1}_{img_index+1}.jpeg"
            jpeg_filename  = self._save_image_as_jpeg(image_bytes, output_folder, image_filename)
            bbox = page.get_image_bbox(img)
            elements.append({
                "type"    : "image",
                "content" : jpeg_filename,
                "bbox"    : [bbox.x0, bbox.y0, bbox.x1, bbox.y1]
            })

    def _extract_vector_elements_from_page(self, page: fitz.Page, block: Dict[str, Any], page_num: int, output_folder: str, elements: List[Dict[str, Any]]) -> None:
        svg_filename = f"vector_{page_num+1}_{block['number']}.svg"
        svg_path = self._save_vector_as_svg(page, block, output_folder, svg_filename)
        elements.append({
            "type"    : "vector",
            "content" : svg_path,
            "bbox"    : block["bbox"]
        })

    def _extract_elements_from_page(self, doc: fitz.Document, page_num: int, output_folder: str) -> List[Dict[str, Any]]:
        elements = []
        page = doc.load_page(page_num)
        blocks = page.get_text("dict")["blocks"]

        y_tolerance = 2  # Tolerance in y-direction

        for block in blocks:
            if block["type"] == 0:  # 0 = Text block
                self._extract_text_elements_from_page(block, elements, y_tolerance)

            elif block["type"] == 2:  # 2 = Vector block
                self._extract_vector_elements_from_page(page, block, page_num, output_folder, elements)

        self._extract_image_elements_from_page(doc, page, page_num, output_folder, elements)

        sorted_elements = sorted(elements, key=lambda element: element["bbox"][1])
        return sorted_elements

    def extract_images_and_text(self, pdf_path: str, output_folder: str) -> List[List[Dict[str, Any]]]:
        doc = fitz.open(pdf_path)
        pages_elements = []

        for page_num in range(len(doc)):
            page_elements = self._extract_elements_from_page(doc, page_num, output_folder)
            pages_elements.append(page_elements)

        return pages_elements

    def generate_html(self, pages_elements: List[List[Dict[str, Any]]], output_html_path: str) -> None:
        html_content = "<html><body>"

        for page_num, elements in enumerate(pages_elements):
            html_content += f'<div class="page" id="page_{page_num+1}">'
            for element in elements:
                if element["type"] == "text":
                    font_size        = round(element["font_size"], 1)
                    font             = "'Helvetica Neue', Helvetica, Arial, sans-serif"
                    content_fixed_nl = element["content"].replace("\n", "<br>")
                    html_content    += f'<p style="font-size:{font_size}px; font-family:{font};">{content_fixed_nl}</p>'

                elif element["type"] == "image":
                    html_content += f'<img src="{element["content"]}" alt="{element["content"]}"><br>'

                elif element["type"] == "vector":
                    html_content += f'<img src="{element["content"]}" alt="vector"><br>'

            html_content += '</div><div style="page-break-after: always;"></div>'

        html_content += "</body></html>"

        with open(output_html_path, "w", encoding="utf-8") as html_file:
            html_file.write(html_content)
