import openai
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
import os
from PIL import Image
import argparse

def main():
    # Argumentparser för att läsa in bildfilen
    parser = argparse.ArgumentParser(description='Skicka en bild för tolkning med OpenAI API.')
    parser.add_argument('--file', type=str, default='image.png', help='Sökvägen till bildfilen som ska tolkas.')
    args = parser.parse_args()

    # Läs API-nyckel och orgid från miljövariabler
    # TODO: The 'openai.organization' option isn't read in the client API. You will need to pass it when you instantiate the client, e.g. 'OpenAI(organization=os.getenv("OPENAI_ORGID"))'
    # openai.organization = os.getenv("OPENAI_ORGID")

    # Öppna och läs bilden
    image_path = args.file
    image = Image.open(image_path)

    # Använd OpenAI API för att tolka bilden
    response = client.images.generate(file=open(image_path, "rb"),
    purpose="text_extraction")

    # Visa resultatet
    print(response)

if __name__ == "__main__":
    main()
