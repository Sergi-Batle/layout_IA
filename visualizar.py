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


# data = {
#     "cod_factura": "241113415050",
#     "fecha_factura": "25/04/2024",
#     "cif_proveedor": "A41810920 ",
#     "cif_cliente": "B07099047",
#     "importe_total": "94,24",
#     "importe_total_antes_de_impuestos": "85,67",
#     "importe_de_iva": "8,57",
#     "porcentaje_de_iva": "10"
# }
dades =  list(data.values())

label2color = {
        'cif_cliente': 'blue',
        'cif_proveedor': 'green',
        'cod_factura': 'orange',
        'fecha_factura': 'violet',
        'fecha_vencimiento': 'red',
        'importe_de_iva': 'yellow',
        'importe_total': 'pink',
        'importe_total_antes_de_impuestos': 'magenta',
        'porcentaje_de_iva': 'cyan',
        'others': 'violet',
        '': 'violet'}

def draw(img, BBOX, color, label):
    # Dibujar la caja delimitadora
    cv.rectangle(img, (BBOX[0], BBOX[1]), (BBOX[2], BBOX[3]), color, 2)
    
    # Poner el nombre de la etiqueta
    font = cv.FONT_HERSHEY_SIMPLEX
    cv.putText(img, label, (BBOX[0], BBOX[1] - 10), font, 0.5, color, 2, cv.LINE_AA)



def visualize_pdf_with_annotations(pdf_path, json_path, output_img_path):
    # Cargar el archivo JSON con las anotaciones
    with open(json_path, 'r', encoding='utf-8') as f:
        annotations = json.load(f)
    
    # Cargar la imagen del PDF
    img = cv.imread(pdf_path)
    
    # Dibujar las anotaciones en la imagen
    for annotation in annotations['form']:
        bbox = annotation['box']
        label = annotation['label']
        
        if label in label2color:
            color = label2color[label]            

            draw(img, bbox, color, label)
    
    # Guardar la imagen con las anotaciones
    cv.imwrite(output_img_path, img)
    print(f"Image saved to {output_img_path}")

# Ejemplo de uso
pdf_path = fr'dataset\testing_data\images\TC_page_1.png'
json_path = fr'dataset\testing_data\annotations\TC_page_1.json'
output_img_path = 'output_image_with_annotations.jpg'

def main():
    visualize_pdf_with_annotations(pdf_path, json_path, output_img_path)