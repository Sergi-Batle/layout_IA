import json
import fitz
import numpy as np
import cv2 as cv



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


data = {
    "cod_factura": "241113415050",
    "fecha_factura": "25/04/2024",
    "cif_proveedor": "A41810920 ",
    "cif_cliente": "B07099047",
    "importe_total": "94,24",
    "importe_total_antes_de_impuestos": "85,67",
    "importe_de_iva": "8,57",
    "porcentaje_de_iva": "10"
}
dades =  list(data.values())

def draw(img, BBOX, randomcolor=False):
    rsx, rsy, rex, rey = BBOX
    if randomcolor:
        B, G, R = np.random.randint(0, 255, 3).tolist()
    else:
        B, G, R = 0, 255, 0
    cv.rectangle(img, (int(rsx), int(rsy)), (int(rex), int(rey)), (B, G, R), 2)

def visualize_pdf_with_annotations(pdf_path, json_path, output_img_path):
    # Cargar el archivo JSON con las anotaciones
    with open(json_path, 'r', encoding='utf-8') as f:
        annotations = json.load(f)

    # Abrir el archivo PDF
    pdf_document = fitz.open(pdf_path)
    num_pages = pdf_document.page_count

    # Iterar sobre las páginas del PDF
    for page_num in range(num_pages):
        if page_num == 1:
            break
        
        # Obtener la página y renderizarla como imagen
        page = pdf_document[page_num]
        pix = page.get_pixmap()
        img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)

        # Convertir a formato adecuado para OpenCV (BGR)
        if pix.n == 4:  # Si tiene canal alpha
            img = cv.cvtColor(img, cv.COLOR_BGRA2BGR)

        # Invertir la imagen verticalmente
        img = cv.flip(img, 0)

        # Hacer una copia de la imagen para que no sea de solo lectura
        img_copy = img.copy()

        # Extraer las coordenadas de las cajas delimitadoras de las palabras
        list_of_BBOXes = [word['box'] for ann in annotations['form'] for word in ann['words'] if word]
        words = [word['text'] for ann in annotations['form'] for word in ann['words'] if word]
        labels = [ann['label'] for ann in annotations['form']]

        datos = []
        clean = {}
        
        for label in labels:
            if label == 'others':
                continue
            
            datos.append((label, words[labels.index(label)]))
        datos = set(datos)
            
        for fila in datos:
            clean[fila[0]] = fila[1]
        
        # print(clean)
        # for word in words:
        #     print(word) 

        # Dibujar las cajas delimitadoras sobre la imagen de la página
        for BBOX in list_of_BBOXes:
            if labels[list_of_BBOXes.index(BBOX)] == 'others':
                continue
            draw(img_copy, BBOX, randomcolor=True)

        # Invertir la imagen con las anotaciones verticalmente
        img_copy = cv.flip(img_copy, 0)

        # Guardar la imagen con las anotaciones
        output_filename = f"{output_img_path}_page_{page_num+1}.png"
        cv.imwrite(output_filename, img_copy)
        print(f"Página {page_num + 1} guardada en {output_filename}")

# Rutas del PDF, JSON y la imagen de salida
pdf_path = 'pdfs/TC_page_1.pdf'
json_path = 'dataset/training_data/annotations/TC_page_1.json'
output_img_path = 'output_image_with_annotations'

# Visualizar el PDF con anotaciones
visualize_pdf_with_annotations(pdf_path, json_path, output_img_path)