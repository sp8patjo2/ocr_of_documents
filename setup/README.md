# ocr_of_documents

### installera paket
```bash
sudo apt-get update  && sudo apt-get install tesseract-ocr
```

### setup av miljö:
```bash
conda create --name ocr_of_documents python=3.9
conda activate ocr_of_documents
```
### installera paket
```bash
conda install -c conda-forge pytesseract
conda install -c conda-forge pillow
```

### installera andra
```bash
pip install -r setup/requirements.txt
```

### fixa .env

Möjligen, om du inte satt OPENAI-nycklar i din miljö så läses de ifrån .env då behöver du gör följande

Det finns en fil `setup/env.frag` med environment-variabler.
Den ser ut något som:
```
#OPENAI_API_KEY="sk-*"
#OPENAI_ORGID="org-*5uQ"
```
kopiera env.frag till rooten, `cp -i setup/env.frag .env`

Editera den - d.v.s. rita dit din nyckel / orgid och plocka bort kommentarstecknet.

