from openai import OpenAI
import base64
import json
import os
from urllib.parse import urlparse

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

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


image_local = './image.jpg'
image_url = f"data:image/jpeg;base64,{encode_image(image_local)}"
#image_url = 'https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2021/02/19/ML-1955-2.jpg'


api_key, org_id = get_api_details()
client = OpenAI(api_key = api_key, organization = org_id)


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



# Extract JSON data from the response and remove Markdown formatting
json_string = response.choices[0].message.content
json_string = json_string.replace("```json\n", "").replace("\n```", "")

# Parse the string into a JSON object
json_data = json.loads(json_string)

filename_without_extension = os.path.splitext(os.path.basename(urlparse(image_url).path))[0] #for URL image
#filename_without_extension = os.path.splitext(os.path.basename(image_local))[0] #for local image

# Add .json extension to the filename
json_filename = f"{filename_without_extension}.json"

# Save the JSON data to a file with proper formatting
with open("./Data/" + json_filename, 'w') as file:
    json.dump(json_data, file, indent=4)

print(f"JSON data saved to {json_filename}")