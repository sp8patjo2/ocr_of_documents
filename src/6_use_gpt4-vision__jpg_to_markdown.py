import os
import base64
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
    print(f"connecting to OpenAI with api-key: ...{api_key[-5:]} and orgid: ...{org_id[-5:]}")
    if org_id[-5:] != "7v5uQ":
        raise Exception(f"Error: using the wrong orgid: {org_id}")
    
    return OpenAI(api_key=api_key, organization=org_id)


def generate_image_url(image_path):
    encoded_image = encode_image(image_path)
    return f"data:image/jpeg;base64,{encoded_image}"


def get_response(client, image_url,instructions):
    response = client.chat.completions.create(
        model='gpt-4-vision-preview', 
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", 
                     "text": instructions},
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


def extract_markdown(response):
    markdown_content = response.choices[0].message.content
    return markdown_content


def save_markdown_to_file(markdown_content, output_file):
    with open(output_file, 'w') as file:
        file.write(markdown_content)

    print(f"Markdown content saved to {output_file}")


def main():
    load_dotenv(override=True) # use .env ... and overwrite, .env rulez
    
    #for key, value in os.environ.items():
    #    if key.startswith("OPENAI_"):  # Filtrera för att bara se dina specifika variabler
    #       print(f"{key}={value}")
    
    
    parser = argparse.ArgumentParser(description="Process an image and save the extracted markdown data.")
    parser.add_argument('--from', dest='source_image', default='images/test1_image.jpg', help="Path to the image file")
    parser.add_argument('--to', dest='output_file', help="Path to save the output markdown file")
    args = parser.parse_args()

    api_key, org_id = get_api_details()
    client = create_client(api_key, org_id)
    image_url = generate_image_url(args.source_image)
    
    instructions = """Return a markdown with the texts in the image.
    Create a table with the layout, and each word at the approximate place in the table.
    If any word is higlighted in the image with a square make it bold in the markdown text.
    Only return the markdown!
    """
    response = get_response(client, image_url, instructions)
    markdown_content = extract_markdown(response)

    if args.output_file:
        output_file = args.output_file
    else:
        filename_without_extension = os.path.splitext(os.path.basename(args.source_image))[0]
        output_file = f"{filename_without_extension}.md"

    save_markdown_to_file(markdown_content, output_file)

if __name__ == "__main__":
    main()
