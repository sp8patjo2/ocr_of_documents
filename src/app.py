import os
import argparse
import re
import logging
from dotenv import load_dotenv
from classes.ai_image_processor       import AIImageProcessor
from classes.pdf_to_text_and_images   import PDFToTextAndImages
from classes.mhtml_to_text_and_images import MHTMLToTextAndImages

logger = None

def setup_logger(log_level: int) -> logging.Logger:
    logger = logging.getLogger("file_to_html_converter")
    logger.setLevel(log_level)
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


def pdf_to_html_jpeg(pdf_path, output_folder):
    global logger
    converter = PDFToTextAndImages(logger)

    logger.info(f"Starting PDF to HTML conversion of {pdf_path} in folder: {os.getcwd()}")
    pages_elements = converter.extract_images_and_text(pdf_path, output_folder)
    output_html_path = os.path.join(output_folder, f"{output_folder}.html")

    converter.generate_html(pages_elements, output_html_path)
    logger.info(f"HTML file created at: {output_html_path}")
    return output_html_path


def mhtml_to_html_jpeg(mhtml_path, output_folder):
    global logger
    mhtml_to_html_converter = MHTMLToTextAndImages(logger)

    logger.info(f"Starting MHTML to HTML conversion of {mhtml_path} in folder: {os.getcwd()}")
    output_html_path, _ = mhtml_to_html_converter.convert(mhtml_path, output_folder)
    
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
                output_file = os.path.splitext(source_image)[0] + '.md'
                processor.process_image(source_image, output_file)
                logger.info(f"AI-analyzing {source_image} - result is in {output_file}")


def process_file(file_path):
    output_folder = os.path.splitext(os.path.basename(file_path))[0]

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    if file_path.lower().endswith('.pdf'):
        pdf_to_html_jpeg(file_path, output_folder)
    elif file_path.lower().endswith('.mhtml') or file_path.lower().endswith('.mht'):
        mhtml_to_html_jpeg(file_path, output_folder)
    else:
        return False

    jpeg_to_markdown(output_folder)
    return True


def process_directory(path):
    unprocessed_files = []
    for file in os.listdir(path):
        file_path = os.path.join(path, file)

        if not os.path.isfile(file_path):
            continue  # do not collect subfolders in unprocessed ... it's expected. NEXT
        
        if not process_file(file_path):
            unprocessed_files.append(file_path)  # save to be able to inform user (last)

    if not unprocessed_files:
        return
    
    logger.info("The following files were not processed:")
    for file in unprocessed_files:
        logger.info(file)


def main() -> None:
    global logger 
    load_dotenv()  # Load variables from .env file

    # init setup logging - read level from .env. Level "warning" is fallback
    log_level_str = os.getenv('LOG_LEVEL', 'WARNING').upper()
    log_level = getattr(logging, log_level_str, logging.WARNING)
    logger = setup_logger(log_level)

    # parse arguments, there is a default file set
    parser = argparse.ArgumentParser(description="Convert PDF or MHTML to HTML with extracted images.")
    parser.add_argument("--pdf", help="Path to the PDF file.")
    parser.add_argument("--path", help="Path to the directory containing PDF or MHTML files.")
    args = parser.parse_args()

    logger.info(f"Current working dir is: {os.getcwd()}")

    if args.pdf and args.path:
        raise ValueError("Both --pdf and --path cannot be specified at the same time.")

    if not args.path:
        args.path = 'Handdatorer'
        
    if not args.pdf and not args.path:
        logger.error("Either --pdf or --path must be specified.")
        return

    if args.path:
        debug = f"{os.path.join(os.getcwd(), args.path)}"
        logger.info(f"Processing {debug}")
        process_directory(args.path)
        return

    process_file(args.pdf)


if __name__ == "__main__":
    main()
