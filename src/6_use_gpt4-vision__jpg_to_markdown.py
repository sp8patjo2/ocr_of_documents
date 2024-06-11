import base64
import json
import os
import argparse
from dotenv import load_dotenv

from openai import OpenAI



def get_api_details():
    api_key = os.getenv("OPENAI_API_KEY")
    org_id = os.getenv("OPENAI_ORGID")

    if not api_key:
        raise ValueError("API-nyckel saknas. Sätt OPENAI_API_KEY som en miljövariabel.")
    
    if not org_id:
        raise ValueError("Organisations-ID saknas. Sätt OPENAI_ORGID som en miljövariabel.")
    
    return api_key, org_id



def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')



def create_client(api_key, org_id):
    print(f"connecting to OpenAI with api-key {api_key} and orgid: {org_id} ")
    return OpenAI(api_key=api_key, organization=org_id)



def generate_image_url(image_path):
    encoded_image = encode_image(image_path)
    return f"data:image/jpeg;base64,{encoded_image}"



def get_response(client, image_url):
    response = client.chat.completions.create(
        model='gpt-4-vision-preview', 
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Return JSON document with data. Only return JSON not other text"},
                    {
                        "type": "image_url",
                        "image_url": {"url": image_url}
                    }
                ],
            }
        ],
        max_tokens=500,
    )
    return response



def extract_json(response):
    json_string = response.choices[0].message.content
    json_string = json_string.replace("```json\n", "").replace("\n```", "")
    return json.loads(json_string)



def save_json_to_file(json_data, output_file):
    with open(output_file, 'w') as file:
        json.dump(json_data, file, indent=4)

    print(f"JSON data saved to {output_file}")



def main():
    load_dotenv() # dra in .env
    
    parser = argparse.ArgumentParser(description="Process an image and save the extracted JSON data.")
    parser.add_argument('--from', dest='source_image', default='images/test1_image.jpg', help="Path to the image file")
    parser.add_argument('--to', dest='output_file', help="Path to save the output JSON file")
    args = parser.parse_args()

    api_key, org_id = get_api_details()
    client = create_client(api_key, org_id)
    image_url = generate_image_url(args.source_image)
    response = get_response(client, image_url)
    json_data = extract_json(response)

    if args.output_file:
        output_file = args.output_file
    else:
        filename_without_extension = os.path.splitext(os.path.basename(args.source_image))[0]
        output_file = f"{filename_without_extension}.json"

    save_json_to_file(json_data, output_file)

if __name__ == "__main__":
    main()
