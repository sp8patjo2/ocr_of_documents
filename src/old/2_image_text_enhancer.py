import openai
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
import pytesseract
from PIL import Image
import os
import argparse

def main():
    # Argumentparser för att läsa in bildfilen
    parser = argparse.ArgumentParser(description='Använd Tesseract och OpenAI API för textutvinning och förbättring.')
    parser.add_argument('--file', type=str, default='image.png', help='Sökvägen till bildfilen som ska tolkas.')
    args = parser.parse_args()

    # Läs API-nyckel och orgid från miljövariabler
    # TODO: The 'openai.organization' option isn't read in the client API. You will need to pass it when you instantiate the client, e.g. 'OpenAI(organization=os.getenv("OPENAI_ORGID"))'
    # openai.organization = os.getenv("OPENAI_ORGID")

    # Öppna och läs bilden
    image_path = args.file
    image = Image.open(image_path)

    # Använd Tesseract för att extrahera text
    text = pytesseract.image_to_string(image)

    # Använd OpenAI API för att förbättra tolkningen
    response = client.completions.create(engine="davinci",
    prompt=f"Tolka följande text och rätta eventuella fel:\n\n{text}",
    max_tokens=100)

    # Visa resultatet
    print(response.choices[0].text.strip())


if __name__ == "__main__":
    main()
