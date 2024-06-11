# ocr av dokument

## syftet

Det finns ett stort antal dokument som används av verksamheten som inte är i text-form, d.v.s. instruktionerna är skrivna med bilder som illustrationer och bilderna är viktiga eftersom de visar var man ska klicka och hur man ska göra.  Caset var supporten men det gäller fler anar vi.

Behöver se om det går att läsa ut texterna och på vilken kvalitet det blir.

Testar dels:
1. “vanlig” OCR - d.v.s tessaract
2. AI-motor, med start på OpenAI



# beskrivning av mappstruktur
beskriver inte det som är samma i alla projekt, test, setup, documentation m.fl.

## src/old

saker och ting som inte gick bra, men ändå tester värda att spara för att visa vad som inte fungerar.

## images

bilder jag hade som underlag när jag gjorde testerna
lade även PDFer där som underlag

## result

Resultat från körningar.
Försöker 

## program

**src/0_using_python_ocr.py**

ett enkelt program som läser en bild och genererar en text med `pytesseract`
```bash
#usage:
src/0_using_python_ocr.py --in=image/file.png --out=resultat/out.txt
```

**src/5_use_gpt4-vision__jpg_to_json.py**

ett enkelt program som använder `gpt-4-vision-preview`

```bash
#usage:
src/0_using_python_ocr.py
```


