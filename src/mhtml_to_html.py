import os
import argparse
from email import policy
from email.parser import BytesParser
from bs4 import BeautifulSoup
from PIL import Image
import io

def create_folder(folder_name):
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

def generate_unique_filename(folder_name, base_name, extension):
    counter  = 1
    new_name = base_name
    while os.path.exists(os.path.join(folder_name, f"{new_name}.{extension}")):
        new_name = f"{base_name}_{counter}"
        counter += 1
    return f"{new_name}.{extension}"

def get_identifier(part):
    content_id       = part.get('Content-ID')
    content_location = part.get('Content-Location')
    if content_id:
        return content_id.strip('<>')
    if content_location:
        return content_location.split('/')[-1]
    return None

def save_image(part, folder_name, image_name):
    image_path = os.path.join(folder_name, image_name)
    if part.get_content_type() == "image/jpeg":
        with open(image_path, 'wb') as img_file:
            img_file.write(part.get_payload(decode=True))
    else:
        image = Image.open(io.BytesIO(part.get_payload(decode=True)))
        image = image.convert('RGB')  # Konvertera till RGB om det behövs
        image.save(image_path, 'JPEG')
    return image_name

def save_resources(message, folder_name):
    """Sparar alla resurser och returnerar sammansatt HTML-innehåll samt en lista över resurser."""
    resources  = []
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

        identifier = get_identifier(part)
        if not identifier:
            continue

        base_name        = os.path.splitext(identifier)[0]
        image_name       = generate_unique_filename(folder_name, base_name, 'jpeg')
        saved_image_name = save_image(part, folder_name, image_name)
        resources.append((identifier, saved_image_name))

    full_body_content = "\n".join(body_parts)
    html_content      = f"<html><body>{full_body_content}</body></html>"
    return html_content, resources

def adjust_links(html_content, resources):
    """Justera länkar i HTML-innehållet så att de pekar på sparade bilder."""
    soup = BeautifulSoup(html_content, 'html.parser')
    for img_tag in soup.find_all('img'):
        src = img_tag['src']
        if src.startswith('cid:'):
            content_id = src[4:]
            for cid, image_name in resources:
                if cid == content_id:
                    img_tag['src'] = image_name
                    break
    return str(soup)

def save_html(html_content, folder_name):
    html_path = os.path.join(folder_name, 'index.html')
    with open(html_path, 'w', encoding='utf-8') as html_file:
        html_file.write(html_content)

def convert_mhtml(file):
    """Huvudmetoden som orkestrerar hela konverteringen."""
    folder_name = os.path.splitext(file)[0]

    with open(file, 'rb') as f:
        message = BytesParser(policy=policy.default).parse(f)

    create_folder(folder_name)                             # Skapa en mapp för att spara HTML och resurser
    html_content, resources = save_resources(message, folder_name)  # Spara resurser och samla HTML-innehåll
    adjusted_html_content   = adjust_links(html_content, resources) # Justera länkarna i HTML-innehållet
    save_html(adjusted_html_content, folder_name)          # Spara det justerade HTML-innehållet till en fil

def main():
    parser = argparse.ArgumentParser(description='Convert MHTML file to a folder with HTML and images.')
    parser.add_argument('--file', type=str, default='exempel/handheld/Instruktion återställning av Wi-Fi, mobildata och Bluetooth på modell EDA52.mhtml', help='Path to the MHTML file.')
    args = parser.parse_args()
    
    convert_mhtml(args.file)

if __name__ == "__main__":
    main()
