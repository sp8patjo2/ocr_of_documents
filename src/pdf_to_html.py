import os
import argparse
import logging
from dotenv import load_dotenv
from classes.pdf_to_text_and_images import PDFToTextAndImages

def setup_logger(log_level: int) -> logging.Logger:
    logger = logging.getLogger("pdf_to_html_converter")
    logger.setLevel(log_level)
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger

def main() -> None:
    load_dotenv()  # Load variables from .env file

    # init setup logging - read level from .env. Level "warning" is fallback
    log_level_str = os.getenv('LOG_LEVEL', 'WARNING').upper()
    log_level = getattr(logging, log_level_str, logging.WARNING)
    logger = setup_logger(log_level)

    # parse arguments, there is a default file set
    parser = argparse.ArgumentParser(description="Convert PDF to HTML with extracted images.")
    parser.add_argument("--pdf", default="images/test1.pdf", help="Path to the PDF file.")
    args = parser.parse_args()

    # process file
    pdf_path = args.pdf
    base_name = os.path.splitext(os.path.basename(pdf_path))[0]
    output_folder = base_name

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    converter = PDFToTextAndImages(logger)


    # do it in two steps
    logger.info("Starting PDF to HTML conversion.")
    pages_elements = converter.extract_images_and_text(pdf_path, output_folder)
    output_html_path = os.path.join(output_folder, f"{base_name}.html")

    converter.generate_html(pages_elements, output_html_path)
    logger.info(f"HTML file created at: {output_html_path}")

if __name__ == "__main__":
    main()
