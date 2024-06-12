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
    if org_id[-5:] != "7v5uQ":  # FIXME - bara för att jag gör fel ibland ... detta är Mio(T)
        raise Exception(f"Error: using the wrong orgid: {org_id}")
    
    return OpenAI(api_key=api_key, organization=org_id)


def generate_image_url(image_path):
    encoded_image = encode_image(image_path)
    return f"data:application/pdf;base64,{encoded_image}"


def get_response(client, base64_image_url, instructions):
    response = client.chat.completions.create(
        model='gpt-4o',
        #model='gpt-4-vision-preview',
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", 
                     "text": instructions},
                    {
                        "type": "image_url",
                        "image_url": {"url": base64_image_url}
                    }
                ],
            }
        ],
        max_tokens=4096,
    )
    return response


def extract_markdown(response):
    markdown_content = response.choices[0].message.content
    return markdown_content


def save_markdown_to_file(markdown_content, output_file):
    with open(output_file, 'w') as file:
        file.write(markdown_content)

    print(f"Markdown content saved to {output_file}")


def generate_infix_name(response):
    model_name = response.model
    tokens_used = response.usage.total_tokens
    return f"_model_{model_name}_tokens_{tokens_used}"


def main():
    load_dotenv(override=True) # use .env ... and overwrite, .env rulez
    
    parser = argparse.ArgumentParser(description="Process an image and save the extracted markdown data.")
    parser.add_argument('--from', dest='source_image', default='images/test1.pdf', help="Path to the image file")
    parser.add_argument('--to', dest='output_file', help="Path to save the output markdown file")
    args = parser.parse_args()

    api_key, org_id  = get_api_details()
    client           = create_client(api_key, org_id)
    base64_image_url = generate_image_url(args.source_image)
    
    instructions = """
    Read this PDF and concert to an markdown. Move text as-is, do not change any words at all.
    
    Important! 
    For images embedded in the PDF (and only for images) do the following:
    Analyze each of them separately and add a markdown-table for each with the texts contained in the image. 
    Do this by creating a table with the layout, and put each word at the approximate place in the table.
    If any word is highlighted in the image with a square make it bold in the markdown text. 
    

    Translate everything till Swedish.
    When all texts are read and images are processed return the mardown and only the markdown!
    """
    response         = get_response(client, base64_image_url, instructions)
    markdown_content = extract_markdown(response)

    if args.output_file:
        base_output_file = args.output_file
    else:
        filename_without_extension = os.path.splitext(os.path.basename(args.source_image))[0]
        base_output_file = f"{filename_without_extension}.md"

    infix = generate_infix_name(response)
    name, ext = os.path.splitext(base_output_file)
    output_file = f"{name}__{infix}{ext}"

    save_markdown_to_file(markdown_content, output_file)


if __name__ == "__main__":
    main()