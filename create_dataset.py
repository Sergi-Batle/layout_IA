import os
import uuid
import json, fitz
import pdfminer
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.layout import LAParams, LTTextBox, LTTextLine, LTChar, LTTextBoxVertical, LTFigure, LTTextLineHorizontal, LTTextBoxHorizontal
from pdfminer.converter import PDFPageAggregator
from pathlib import Path
import cv2 as cv
import numpy as np
from visualizar import main

# Datos de ejemplo
data = {
    "cod_factura": "BC52024030628",
    "fecha_factura": "29-04-24",
    "cif_proveedor": "ESB20861282",
    "cif_cliente": "ESB57687295",
    "importe_total": "58.08",
    "importe_total_antes_de_impuestos": "48.00",
    "importe_de_iva": "10.08",
    "porcentaje_de_iva": "21.0"
}


# data = {
#     "cod_factura": "241113415050",
#     "fecha_factura": "25/04/2024",
#     "cif_proveedor": "A41810920",
#     "cif_cliente": "B07099047",
#     "importe_total": "94,24",
#     "importe_total_antes_de_impuestos": "85,67",
#     "importe_de_iva": "8,57",
#     "porcentaje_de_iva": "10"
# }
dades =  list(data.values())


def get_clave(valor_buscado):
    clave = None  # Si no se encuentra el valor, clave será None
    for key, value in data.items():
        if value == valor_buscado:
            clave = key
            break

    return clave if clave else None


def get_text_and_coordinates(pdf_path):
    with open(pdf_path, 'rb') as fp:
        # Create PDF parser
        parser = pdfminer.pdfparser.PDFParser(fp)
        document = pdfminer.pdfdocument.PDFDocument(parser)

        # Check if document allows text extraction
        if not document.is_extractable:
            raise pdfminer.pdftext.PDFTextExtractionNotAllowed

        # Create resource manager
        resource_manager = pdfminer.pdfinterp.PDFResourceManager()

        # Set parameters for analysis using LAParams
        la_params = LAParams(detect_vertical=True)
        device = PDFPageAggregator(resource_manager, laparams=la_params)
        interpreter = PDFPageInterpreter(resource_manager, device)

        form_data = []

        # Function to parse objects and extract word-level information
        def parse_obj(lt_objects, page_height):
            for obj in lt_objects:                                                               
                if isinstance(obj, (LTTextBox)):
                    words = []
                    for line in obj:
                        if isinstance(line, (LTTextLine, LTTextBoxVertical, LTTextLineHorizontal)):                           
                            current_word = ""
                            current_word_bbox = [float('inf'), float('inf'), float('-inf'), float('-inf')]               

                            for char in line:
                                if isinstance(char, LTChar):
                                    if char.get_text().isspace():
                                        if current_word:
                                            words.append({
                                                "text": current_word,
                                                "box": [int(coord) for coord in current_word_bbox]
                                            })
                                            current_word = ""
                                            current_word_bbox = [float('inf'), float('inf'), float('-inf'), float('-inf')]
                                    else:
                                        current_word += char.get_text()
                                        current_word_bbox[0] = min(current_word_bbox[0], char.bbox[0])
                                        current_word_bbox[1] = min(current_word_bbox[1], char.bbox[1])
                                        current_word_bbox[2] = max(current_word_bbox[2], char.bbox[2])
                                        current_word_bbox[3] = max(current_word_bbox[3], char.bbox[3])
                                           
                            if current_word:
                                words.append({
                                    "text": current_word,
                                    "box": current_word_bbox
                                })
                    
                                
                    for word in words:
                        label = "others"
                        clean_word = str(word["text"]).strip().replace("%", "")
                        
                        if (clean_word in dades):
                            label = get_clave(clean_word)
                        
                        # Invertir las coordenadas verticales
                        word["box"][1] = int(page_height - word["box"][1])
                        word["box"][3] = int(page_height - word["box"][3])
                        word["box"][1], word["box"][3] = int(word["box"][3]), int(word["box"][1])
                        
                        word["box"][0] = int(word["box"][0])
                        word["box"][2] = int(word["box"][2])   
                        form_data.append({
                            "box": word["box"],  
                            "text": word["text"],
                            "label": label,
                            "words": [word],
                            "linking": [],
                            "id": str(uuid.uuid4())
                        })
                elif isinstance(obj, LTFigure):
                    parse_obj(obj._objs, page_height)

        # Loop through pages
        for page in PDFPage.create_pages(document):
            interpreter.process_page(page)
            layout = device.get_result()

            # Get the page height for flipping
            page_height = layout.height

            # Process page objects
            parse_obj(layout._objs, page_height)

        return {"form": form_data}


def save_image_from_pixmap(pix, output_dir, filename):
    # Convertir la imagen desde el buffer
    img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
    
    # Si la imagen tiene un canal alfa (transparente), la convertimos a BGR
    if pix.n == 4:
        img = cv.cvtColor(img, cv.COLOR_BGRA2BGR)
    
    # Asegurarnos de que el directorio de salida exista
    os.makedirs(output_dir, exist_ok=True)
    
    # Guardar la imagen sin escalar
    output_path = os.path.join(output_dir, filename)
    cv.imwrite(output_path, img)
    print(f"Image saved to {output_path}")
    
    
def save_annotation(output_dir, json_data, json_filename):
    output_path = os.path.join(output_dir, json_filename)

    # Save the output to a JSON file
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, indent=2)
    print(f"salida guardada en {output_path}")
    

def create_json(pdf_path):
    # Extract text and coordinates
    json_data = get_text_and_coordinates(pdf_path)
    json_filename = os.path.basename(pdf_path).replace(".pdf", ".json")
    
    save_annotation(fr"dataset/training_data/annotations", json_data, json_filename)
    save_annotation(fr"dataset/testing_data/annotations", json_data, json_filename)
    

def create_images(pdf_path):
    pdf_document = fitz.open(pdf_path)
    page = pdf_document[0]
    pix = page.get_pixmap()
    
    save_image_from_pixmap(pix, fr"dataset\testing_data\images", f"{os.path.basename(pdf_path).replace('.pdf', '.png')}")
    save_image_from_pixmap(pix, fr"dataset\training_data\images", f"{os.path.basename(pdf_path).replace('.pdf', '.png')}")

    # Cerrar el documento PDF
    pdf_document.close()


pdf_dir = Path("pdfs")
pdf_files = pdf_dir.glob("*.pdf")

for pdf_file in pdf_files:
    create_json(pdf_file)
    create_images(pdf_file)

main()    