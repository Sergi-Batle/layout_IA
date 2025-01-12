import json

# Función para verificar si las coordenadas de las cajas (box) están dentro del rango [0, 1000]
def check_bbox_range(bbox):
    for i, coord in enumerate(bbox):
        if coord < 0 or coord > 1000:
            print(f"Warning: Box has out-of-range values: {bbox}")
            return False
    return True

# Función principal que recibe el archivo JSON y verifica las coordenadas 'box'
def validate_bbox_in_json(json_path):
    # Cargar el archivo JSON
    try:
        with open(json_path, 'r') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error al cargar el archivo JSON: {e}")
        return
    
    # Asegúrate de que las claves que contienen las cajas 'box' existan en el JSON
    if 'form' not in data:
        print("Error: El archivo JSON no contiene la clave 'form'")
        return
    
    # Iterar sobre cada formulario en la lista 'form'
    for idx, form in enumerate(data['form']):
        if 'box' not in form:
            print(f"Error: El formulario {idx} no contiene la clave 'box'")
            continue
        
        # Verificar las coordenadas de la caja principal 'box'
        box = form['box']
        if not check_bbox_range(box):
            print(f"Formulario {idx} tiene coordenadas de 'box' fuera de rango.")
        
        # También se debe verificar cada 'box' en las palabras dentro de 'words'
        if 'words' in form:
            for word_idx, word in enumerate(form['words']):
                if 'box' not in word:
                    print(f"Error: La palabra {word_idx} en el formulario {idx} no contiene la clave 'box'")
                    continue
                
                word_box = word['box']
                if not check_bbox_range(word_box):
                    print(f"Palabra {word_idx} en el formulario {idx} tiene coordenadas 'box' fuera de rango.")

# Ruta del archivo JSON
json_path = fr'dataset\testing_data\annotations\TC_page_1.json'  # Aquí debes poner la ruta de tu archivo JSON

# Validar las coordenadas bbox en el archivo JSON
validate_bbox_in_json(json_path)
