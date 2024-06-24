import pytesseract
from PIL import Image
import argparse

def ocr_image(image_path):
    # Öppna bilden
    image = Image.open(image_path)
    
    # Använd Tesseract för att läsa text från bilden
    text = pytesseract.image_to_string(image)
    
    return text

def main():
    parser = argparse.ArgumentParser(description='OCR using Tesseract')
    parser.add_argument('--in', dest='input_file', required=True, help='Input image file')
    parser.add_argument('--out', dest='output_file', required=True, help='Output text file')
    args = parser.parse_args()

    # Använd funktionen ocr_image
    text = ocr_image(args.input_file)
    
    # Skriv texten till en utdatafil
    with open(args.output_file, 'w') as file:
        file.write(text)

if __name__ == '__main__':
    main()
