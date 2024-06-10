import os
import argparse
import openai
from openai import OpenAI
import base64

def encode_image(image_path):
    with open(image_path,"rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def get_api_details():
    # Läs API-nyckel och orgid från miljövariabler
    api_key = os.getenv("OPENAI_API_KEY")
    org_id = os.getenv("OPENAI_ORGID")

    # Kontrollera att API-nyckeln finns
    if not api_key:
        raise ValueError("API-nyckel saknas. Sätt OPENAI_API_KEY som en miljövariabel.")
    
    if not org_id:
        raise ValueError("Organisations-ID saknas. Sätt OPENAI_ORGID som en miljövariabel.")
    
    return api_key, org_id


def interpret_image(client,image_local):
    image_url = f"data:image/jpeg;base64,{encode_image(image_local)}"
    
    # Använd file_id i din förfrågan
    response = openai.ChatCompletion.create(
        model="gpt-4-vision-preview",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text", 
                        "text": "What text is in this image?"
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": image_url }
                    },
                ],
            }
        ],
        max_tokens=300,
    )
    return response['choices'][0]

def delete_file(file_id):
    try:
        delete_response = openai.File.delete(file_id)
        print(f"Deleted file: {delete_response}")
    except Exception as e:
        print(f"Failed to delete file: {e}")

def main():    
    parser = argparse.ArgumentParser(description='Skicka en bild till OpenAI GPT-4 för tolkning.')
    parser.add_argument('--file', type=str, default='image.png', help='Sökvägen till bildfilen som ska tolkas.')
    args = parser.parse_args()

    api_key, org_id = get_api_details()

    print(f"Using API: ...{api_key[-5:]} with org: ...{org_id[-5:]}")

    openai.api_key = api_key
    openai.organization = org_id
    
    client = OpenAI()


    result  = interpret_image(client,args.file)
    print(result)




if __name__ == "__main__":
    main()
