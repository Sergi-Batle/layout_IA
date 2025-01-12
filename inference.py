from torch.nn import CrossEntropyLoss
from PIL import Image, ImageDraw, ImageFont
import pytesseract
from layout_lm_tutorial.layoutlm_preprocess import preprocess, convert_to_features, model_load
from collections import defaultdict

# Configuración de Tesseract
pytesseract.pytesseract.tesseract_cmd = rf'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Funciones auxiliares
def get_labels(path):
    """Lee las etiquetas desde un archivo y asegura que 'O' esté presente."""
    with open(path, "r") as f:
        labels = f.read().splitlines()
    if "O" not in labels:
        labels = ["O"] + labels
    return labels

def iob_to_label(label):
    """Convierte etiquetas IOB a su representación base."""
    return label[2:] if label != 'O' else ""

# Lectura de etiquetas y configuración del modelo
labels = get_labels("dataset/labels.txt")

num_labels = len(labels)
label_map = {i: label for i, label in enumerate(labels)}
pad_token_label_id = CrossEntropyLoss().ignore_index

model_path = 'layoutlm.pt'
model = model_load(model_path, num_labels)

# Preprocesamiento de la imagen
image, words, boxes, actual_boxes = preprocess(rf"images\dhl_2.png")
word_level_predictions, final_boxes = convert_to_features(image, words, boxes, actual_boxes, model)

# Configuración de colores y fuente
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
    '': 'violet'
}

draw = ImageDraw.Draw(image)
font = ImageFont.load_default()

# Mapeo de cajas a etiquetas múltiples
boxes_labels = defaultdict(list)

# Registrar etiquetas para cada caja
for prediction, box in zip(word_level_predictions, final_boxes):
    predicted_label = iob_to_label(label_map[prediction]).lower()
    boxes_labels[tuple(box)].append(predicted_label)

# Dibujado de predicciones
for box, labels in boxes_labels.items():
    not_other=False
    labels = list(set(labels))
    if len(labels) > 1 and 'others' in labels:
        labels.remove('others')
        
    if 'fecha_vencimiento' in labels:
        labels.remove('fecha_vencimiento')
                          
    if len(labels) == 0:
        continue
    
    combined_labels = ", ".join(labels)
    print(f"Box: {box}, Labels: {combined_labels}")  # Mostrar las cajas y etiquetas en la consola
    
    # Dibujar la caja y etiquetas
    color = label2color.get(labels[0], "gray")  # Usar el color del primer label como referencia
    
    padding_x = 20  # Aumento del padding en la dirección horizontal
    padding_y = 20  # Aumento del padding en la dirección vertical
    box = (box[0] - padding_x, box[1] - padding_y, box[2] + padding_x, box[3] + padding_y)

    if labels[0] != 'others':
        # Dibujar el rectángulo con mayor grosor
        draw.rectangle(box, outline=color, width=3)  # Aumentar grosor de la línea a 5 píxeles
        # Dibujar el texto con el nuevo tamaño de fuente
        draw.text((box[0] + 20, box[1] - 20), text=combined_labels, fill=color, font=font) 
    
    else:
        violet_with_opacity = (238, 130, 238, 10)
        draw.rectangle(box, outline=violet_with_opacity)     
        # Dibujar el texto con el nuevo tamaño de fuente
        draw.text((box[0] + 20, box[1] - 20), text=combined_labels, fill=violet_with_opacity, font=font) 

    

# Guardado del resultado
image.save("resultado.png")
