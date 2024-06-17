import os
import argparse
from mhtml2html import parse_mhtml
from bs4 import BeautifulSoup
from PIL import Image
import io

def create_folder(folder_name):
    """Skapar en mapp med angivet namn om den inte redan finns."""
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

def save_resources(parts, folder_name):
    """Sparar resurser och returnerar HTML-innehåll samt en lista över resurser."""
    resources = []
    html_content = ""
    for part in parts:
        headers = part["headers"]
        content = part["content"]
        
        if headers["Content-Type"].startswith("text/html"):
            html_content = content.decode()
        elif headers["Content-Type"].startswith("image/"):
            content_id = headers["Content-ID"].strip('<>')
            image_name = f"{content_id}.jpeg"
            image_path = os.path.join(folder_name, image_name)
            
            if headers["Content-Type"].startswith("image/jpeg"):
                with open(image_path, 'wb') as img_file:
                    img_file.write(content)
            else:
                image = Image.open(io.BytesIO(content))
                image = image.convert('RGB')  # Konvertera till RGB om det behövs
                image.save(image_path, 'JPEG')

            resources.append((content_id, image_name))
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
    return str(soup)

def save_html(html_content, folder_name):
    """Sparar det justerade HTML-innehållet till en fil."""
    html_path = os.path.join(folder_name, 'index.html')
    with open(html_path, 'w', encoding='utf-8') as html_file:
        html_file.write(html_content)

def convert_mhtml(file):
    """Huvudmetoden som orkestrerar hela konverteringen."""
    folder_name = os.path.splitext(file)[0]
    create_folder(folder_name)

    with open(file, 'rb') as f:
        parts = parse_mhtml(f)

    html_content, resources = save_resources(parts, folder_name)
    adjusted_html_content = adjust_links(html_content, resources)
    save_html(adjusted_html_content, folder_name)

def main():
    """Hanterar kommandoradsargument och anropar convert_mhtml."""
    parser = argparse.ArgumentParser(description='Convert MHTML file to a folder with HTML and images.')
    parser.add_argument('--file', type=str, default='1.mhtml', help='Path to the MHTML file.')
    args = parser.parse_args()
    
    convert_mhtml(args.file)

if __name__ == "__main__":
    main()
