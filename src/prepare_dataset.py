import os
import json
import shutil
from PIL import Image
import random

# --- CONFIGURATION ---
SOURCE_DIR =  "iso_technical_sheets" # Le dossier où ton générateur a mis les images/json
YOLO_DIR = "data/yolo_dataset"     # Le dossier qui sera créé pour YOLO
SPLIT_RATIO = 0.8             # 80% pour l'entraînement, 20% pour la validation

# Nos classes (Idées basées sur ton générateur)
CLASSES = {
    "title_block": 0,
    "notes": 1,
    "gdt_feature": 2
}

def convert_bbox_to_yolo(bbox, img_w, img_h):
    """Convertit [xmin, ymin, xmax, ymax] en [x_center, y_center, width, height] normalisés"""
    x_min, y_min, x_max, y_max = bbox
    
    # Calcul des dimensions et centres
    w = x_max - x_min
    h = y_max - y_min
    x_center = x_min + (w / 2)
    y_center = y_min + (h / 2)
    
    # Normalisation (entre 0 et 1)
    return x_center / img_w, y_center / img_h, w / img_w, h / img_h

def setup_directories():
    """Crée l'arborescence YOLO"""
    for split in ['train', 'val']:
        os.makedirs(os.path.join(YOLO_DIR, 'images', split), exist_ok=True)
        os.makedirs(os.path.join(YOLO_DIR, 'labels', split), exist_ok=True)

def process_dataset():
    setup_directories()
    
    # Lister tous les fichiers JSON
    json_files = [f for f in os.listdir(SOURCE_DIR) if f.endswith('.json')]
    random.shuffle(json_files) # Mélanger pour une bonne répartition
    
    split_index = int(len(json_files) * SPLIT_RATIO)
    train_files = json_files[:split_index]
    
    for count, json_file in enumerate(json_files):
        # Déterminer si on va dans train ou val
        split_folder = 'train' if json_file in train_files else 'val'
        
        with open(os.path.join(SOURCE_DIR, json_file), 'r') as f:
            data = json.load(f)
            
        img_name = data["filename"]
        img_path = os.path.join(SOURCE_DIR, img_name)
        
        # Obtenir la taille de l'image (nécessaire pour la normalisation)
        with Image.open(img_path) as img:
            img_w, img_h = img.size
            
        # --- Création du fichier .txt YOLO ---
        txt_name = img_name.replace('.png', '.txt')
        label_path = os.path.join(YOLO_DIR, 'labels', split_folder, txt_name)
        
        with open(label_path, 'w') as f_out:
            comps = data["components"]
            
            # 1. Title Block
            if "title_block" in comps:
                x, y, w, h = convert_bbox_to_yolo(comps["title_block"], img_w, img_h)
                f_out.write(f"{CLASSES['title_block']} {x:.6f} {y:.6f} {w:.6f} {h:.6f}\n")
                
            # 2. Notes
            if "notes" in comps:
                x, y, w, h = convert_bbox_to_yolo(comps["notes"], img_w, img_h)
                f_out.write(f"{CLASSES['notes']} {x:.6f} {y:.6f} {w:.6f} {h:.6f}\n")
                
            # 3. GD&T Features (Boîtes englobantes des cadres GD&T)
            if "gdt_features" in comps:
                for gdt in comps["gdt_features"]:
                    x, y, w, h = convert_bbox_to_yolo(gdt["bbox_pixels"], img_w, img_h)
                    f_out.write(f"{CLASSES['gdt_feature']} {x:.6f} {y:.6f} {w:.6f} {h:.6f}\n")
                    
        # Copier l'image dans le bon dossier
        shutil.copy(img_path, os.path.join(YOLO_DIR, 'images', split_folder, img_name))
        
    # --- Création du fichier YAML pour l'entraînement ---
    yaml_content = f"""path: {os.path.abspath(YOLO_DIR)} # Chemin absolu requis
train: images/train
val: images/val

names:
  0: title_block
  1: notes
  2: gdt_feature
"""
    with open("dataset.yaml", "w") as f:
        f.write(yaml_content)

    print(f"Dataset prêt ! {len(json_files)} fichiers traités.")
    print(f"Structure sauvegardée dans '{YOLO_DIR}' et config dans 'dataset.yaml'.")

if __name__ == "__main__":
    process_dataset()