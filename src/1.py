
import os
from PIL import Image
import argparse
from openai import OpenAI

def main():
    # Argumentparser för att läsa in bildfilen
    parser = argparse.ArgumentParser(description='Skicka en bild till OpenAI GPT-4 för tolkning.')
    parser.add_argument('--file', type=str, default='image.png', help='Sökvägen till bildfilen som ska tolkas.')
    args = parser.parse_args()

    # Läs API-nyckel och orgid från miljövariabler
    api_key = os.getenv("OPENAI_API_KEY")
    org_id = os.getenv("OPENAI_ORGID")

    # Kontrollera att API-nyckeln finns
    if not api_key:
        raise ValueError("API-nyckel saknas. Sätt OPENAI_API_KEY som en miljövariabel.")
    
    if not org_id:
        raise ValueError("Organisations-ID saknas. Sätt OPENAI_ORGID som en miljövariabel.")


    client = OpenAI(api_key=api_key, organization=org_id)
    if client is None:
        raise Exception("Could not init OpenAI client")


    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
            "role": "user",
            "content": [
                {
                    "type": "text", "text": "What text is in this image?"
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": "https://commons.wikimedia.org/wiki/Main_Page#/media/File:WLE_Austria_Logo.svg",
                    },
                },
            ],
            }
        ],
        max_tokens=300,
    )

    print(response.choices[0])



if __name__ == "__main__":
    main()
