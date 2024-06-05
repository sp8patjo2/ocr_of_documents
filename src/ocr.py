import pytesseract
from PIL import Image
import argparse

def main():
    parser = argparse.ArgumentParser(description='OCR using Tesseract')
    parser.add_argument('--in', dest='input_file', required=True, help='Input image file')
    parser.add_argument('--out', dest='output_file', required=True, help='Output text file')
    args = parser.parse_args()

    # Öppna bilden
    image = Image.open(args.input_file)
    
    # Använd Tesseract för att läsa text från bilden
    text = pytesseract.image_to_string(image)
    
    # Skriv texten till en utdatafil
    with open(args.output_file, 'w') as file:
        file.write(text)

if __name__ == '__main__':
    main()
