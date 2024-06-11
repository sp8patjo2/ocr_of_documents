# ocr_of_documents

# installera paket
sudo apt-get update
sudo apt-get install tesseract-ocr

# setup av miljö:
conda create --name ocr_env python=3.9
conda activate ocr_env

# installera paket
conda install -c conda-forge pytesseract
conda install -c conda-forge pillow


# installera andra
pip install -r setup/requirements.txt




