import argparse
import logging
from classes.mhtml_to_text_and_images import MHTMLToTextAndImages

def main():
    parser = argparse.ArgumentParser(description='Convert MHTML to HTML and JPEG.')
    #parser.add_argument('mhtml_file', help='Path to the MHTML file.')
    parser.add_argument('--file', type=str, default='../exempel/handheld/Instruktion återställning av Wi-Fi, mobildata och Bluetooth på modell EDA52.mhtml', help='Path to the MHTML file.')
    parser.add_argument('--output', default="removeme_test", help='Path to the output folder.')
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)

    converter = MHTMLToTextAndImages(logger)
    html_file, resources = converter.convert(args.file, args.output)
    logger.info(f'HTML file saved to {html_file}')
    logger.info(f'Resources saved: {resources}')

if __name__ == '__main__':
    main()
