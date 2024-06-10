import os
import argparse
import openai

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

def upload_image(file_path):
    # Ladda upp bilden och få en fil-ID
    with open(file_path, "rb") as image_file:
        response = openai.File.create(
            file=image_file,
            purpose='vision'
        )
    return response['id']

def interpret_image(file_id):
    # Använd file_id i din förfrågan
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text", "text": "What text is in this image?"
                    },
                    {
                        "type": "image",
                        "image": {
                            "file_id": file_id
                        }
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

    file_id = None

    try:
        file_id = upload_image(args.file)
        result  = interpret_image(file_id)
        print(result)

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        if file_id:
            delete_file(file_id)

if __name__ == "__main__":
    main()
