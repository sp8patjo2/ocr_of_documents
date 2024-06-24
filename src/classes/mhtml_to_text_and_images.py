import os
import logging
from email import policy
from email.parser import BytesParser
from bs4 import BeautifulSoup
from PIL import Image
import io

"""
This class provides functionality to convert MHTML documents into HTML and JPEG images.
It parses the MHTML file, extracts HTML content and embedded images, and saves them in
the desired format. The extracted HTML content and images are processed and stored in
specified output directories.

main method:
- convert(mhtml_path, output_folder): Converts the MHTML document to HTML and JPEG images, saving them to the output folder.


see also:
- mhtml_to_text_and_images.py - similar class for MHTML conversion
"""
class MHTMLToTextAndImages:
    def __init__(self, logger: logging.Logger):
        self._logger = logger

    def _create_folder(self, folder_name):
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)

    def _generate_unique_filename(self, folder_name, base_name, extension):
        counter = 1
        new_name = base_name
        while os.path.exists(os.path.join(folder_name, f"{new_name}.{extension}")):
            new_name = f"{base_name}_{counter}"
            counter += 1
        return f"{new_name}.{extension}"

    def _get_identifier(self, part):
        content_id = part.get('Content-ID')
        content_location = part.get('Content-Location')
        if content_id:
            return content_id.strip('<>')
        if content_location:
            return content_location.split('/')[-1]
        return None

    def _save_image(self, part, folder_name, image_name):
        image_path = os.path.join(folder_name, image_name)
        if part.get_content_type() == "image/jpeg":
            with open(image_path, 'wb') as img_file:
                img_file.write(part.get_payload(decode=True))
        else:
            image = Image.open(io.BytesIO(part.get_payload(decode=True)))
            image = image.convert('RGB')  # Konvertera till RGB om det behövs
            image.save(image_path, 'JPEG')
        return image_name

    def _save_resources(self, message, folder_name):
        resources = []
        body_parts = []

        for part in message.walk():
            content_type = part.get_content_type()

            if content_type == "text/html":
                html_part = part.get_payload(decode=True).decode()
                soup = BeautifulSoup(html_part, 'html.parser')
                body = soup.body
                if body:
                    body_parts.append("".join(str(tag) for tag in body.contents))
                continue

            if not content_type.startswith("image/"):
                continue

            identifier = self._get_identifier(part)
            if not identifier:
                continue

            image_name = self._generate_unique_filename(folder_name, identifier, "jpeg")
            saved_image_name = self._save_image(part, folder_name, image_name)
            resources.append(saved_image_name)

        html_content = "".join(body_parts)
        return html_content, resources

    def convert(self, mhtml_path, output_folder):
        self._create_folder(output_folder)
        with open(mhtml_path, 'rb') as mhtml_file:
            message = BytesParser(policy=policy.default).parse(mhtml_file)

        html_content, resources = self._save_resources(message, output_folder)
        html_filename = os.path.join(output_folder, 'output.html')
        with open(html_filename, 'w') as html_file:
            html_file.write(html_content)

        return html_filename, resources
