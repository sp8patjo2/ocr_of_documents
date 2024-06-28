import os
import base64
import argparse
from dotenv import load_dotenv
from openai import OpenAI

class AIImageProcessor:
    def __init__(self):
        load_dotenv(override=True)
        self.api_key, self.org_id = self.get_api_details()
        self.client = self.create_client(self.api_key, self.org_id)

    def get_api_details(self):
        api_key = os.getenv("OPENAI_API_KEY")
        org_id = os.getenv("OPENAI_ORGID")

        if not api_key:
            raise ValueError("API-nyckel saknas. Sätt OPENAI_API_KEY som en miljövariabel.")
        
        if not org_id:
            raise ValueError("Organisations-ID saknas. Sätt OPENAI_ORGID som en miljövariabel.")
        
        return api_key, org_id

    def encode_image(self, image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def create_client(self, api_key, org_id):
        print(f"Connecting to OpenAI with api-key: ...{api_key[-5:]} and orgid: ...{org_id[-5:]}")
        if org_id[-5:] != "7v5uQ":
            raise Exception(f"Error: using the wrong orgid: {org_id}")
        
        return OpenAI(api_key=api_key, organization=org_id)

    def generate_image_url(self, image_path):
        encoded_image = self.encode_image(image_path)
        return f"data:image/jpeg;base64,{encoded_image}"

    def get_response(self, base64_image_url, instructions):
        response = self.client.chat.completions.create(
            model='gpt-4o',
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": instructions},
                        {"type": "image_url", "image_url": {"url": base64_image_url}}
                    ]
                }
            ],
            max_tokens=4096,
        )
        return response

    def extract_markdown(self, response):
        markdown_content = response.choices[0].message.content
        return markdown_content

    def save_markdown_to_file(self, markdown_content, output_file):
        with open(output_file, 'w') as file:
            file.write(markdown_content)
        print(f"Markdown content saved to {output_file}")

    def generate_infix(self, response):
        model_name = response.model
        tokens_used = response.usage.total_tokens
        return f"_model_{model_name}_tokens_{tokens_used}"

    def process_image(self, source_image, output_file):
        base64_image_url = self.generate_image_url(source_image)
        
        instructions = """Return a markdown with the texts in the image.
        Create a table with the layout, and each word at the approximate place in the table.
        If any word is highlighted in the image with a square make it bold in the markdown text.
        Only return the markdown. 
        Please do not include any ```markdown or other other indications that this is markdown.
        """
        
        response = self.get_response(base64_image_url, instructions)
        markdown_content = self.extract_markdown(response)

        if output_file:
            base_output_file = output_file
        else:
            filename_without_extension = os.path.splitext(os.path.basename(source_image))[0]
            base_output_file = f"{filename_without_extension}.md"

        infix = self.generate_infix(response)
        name, ext = os.path.splitext(base_output_file)
        output_file = f"{name}__{infix}{ext}"

        self.save_markdown_to_file(markdown_content, output_file)
