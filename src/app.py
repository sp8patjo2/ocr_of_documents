import os
import argparse
import re
import logging
from dotenv import load_dotenv
from openai import OpenAI
from classes.pdf_to_text_and_images import PDFToTextAndImages
from classes.ai_image_processor import AIImageProcessor
logger = None

def setup_logger(log_level: int) -> logging.Logger:
    logger    = logging.getLogger("pdf_to_html_converter")
    logger.setLevel(log_level)
    handler   = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


def pdf_to_html_jpeg(pdf_path,output_folder):
    global logger
    converter = PDFToTextAndImages(logger)

    # do it in two steps
    logger.info(f"Starting PDF to HTML conversion of {pdf_path} in folder: {os.getcwd()}")
    pages_elements   = converter.extract_images_and_text(pdf_path, output_folder)
    output_html_path = os.path.join(output_folder, f"{output_folder}.html")

    converter.generate_html(pages_elements, output_html_path)
    logger.info(f"HTML file created at: {output_html_path}")
    return output_html_path


def jpeg_to_markdown(jpeg_directory):
    global logger
    processor = AIImageProcessor()
    jpeg_pattern = re.compile(r'^.*\.jpe?g$', re.IGNORECASE)

    for root, _, files in os.walk(jpeg_directory):
        for file in files:
            if jpeg_pattern.match(file):
                source_image = os.path.join(root, file)
                output_file  = os.path.splitext(source_image)[0] + '.md'
                processor.process_image(source_image, output_file)
                logger.info(f"AI-analyzing {source_image} - result is in {output_file}")


def main() -> None:
    global logger 
    load_dotenv()  # Load variables from .env file

    # init setup logging - read level from .env. Level "warning" is fallback
    log_level_str = os.getenv('LOG_LEVEL', 'WARNING').upper()
    log_level     = getattr(logging, log_level_str, logging.WARNING)
    logger        = setup_logger(log_level)

    # parse arguments, there is a default file set
    parser = argparse.ArgumentParser(description="Convert PDF to HTML with extracted images.")
    parser.add_argument("--pdf", default="images/test1.pdf", help="Path to the PDF file.")
    args   = parser.parse_args()

    # process file
    pdf_path      = args.pdf
    output_folder     = os.path.splitext(os.path.basename(pdf_path))[0]
    
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    html_file = pdf_to_html_jpeg(pdf_path,output_folder)
    jpeg_to_markdown(output_folder)
    


if __name__ == "__main__":
    main()
