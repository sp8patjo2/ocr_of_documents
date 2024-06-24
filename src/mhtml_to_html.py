import argparse
import logging
from classes.mhtml_to_text_and_images import MHTMLToTextAndImages

def main():
    parser = argparse.ArgumentParser(description='Convert MHTML to HTML and JPEG.')
    parser.add_argument('mhtml_file', help='Path to the MHTML file.')
    parser.add_argument('output_folder', help='Path to the output folder.')
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    converter = MHTMLToTextAndImages(logger)
    html_file, resources = converter.convert(args.mhtml_file, args.output_folder)
    logger.info(f'HTML file saved to {html_file}')
    logger.info(f'Resources saved: {resources}')

if __name__ == '__main__':
    main()
