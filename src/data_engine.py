import os
import json
import random
from PIL import Image, ImageDraw, ImageFont





class GDTDatasetGenerator:
    def __init__(self, output_dir="gdt_training_data"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        self.symbol_list = [
            "Circularity", "Cylindricity", "Flatness", "Straightness",
            "Concentricity", "Position", "Symmetry", "Angularity",
            "Parallelism", "Perpendicularity", "Circular Runout",
            "Total Runout", "Profile of a Line", "Profile of a Surface"
        ]
        self.datums = ["A", "B", "C", "D", "E", "F"]
        
    def draw_symbol(self, draw, x, y, size, sym_type):
        """La logique de dessin validée"""
        cx, cy = x + size // 2, y + size // 2
        r = size // 3
        sw = 4 # Stroke width

        if sym_type == "Circularity":
            draw.ellipse([cx-r, cy-r, cx+r, cy+r], outline="black", width=sw)
        elif sym_type == "Cylindricity":
            draw.ellipse([cx-r+5, cy-r+5, cx+r-5, cy+r-5], outline="black", width=sw)
            draw.line([cx-r-2, cy+r, cx-r+8, cy-r], fill="black", width=sw)
            draw.line([cx+r-8, cy+r, cx+r+2, cy-r], fill="black", width=sw)
        elif sym_type == "Flatness":
            pts = [(cx-r, cy+r/2), (cx+r/2, cy+r/2), (cx+r, cy-r/2), (cx-r/2, cy-r/2)]
            draw.polygon(pts, outline="black", width=sw)
        elif sym_type == "Straightness":
            draw.line([cx-r, cy, cx+r, cy], fill="black", width=sw)
        elif sym_type == "Concentricity":
            draw.ellipse([cx-r, cy-r, cx+r, cy+r], outline="black", width=sw)
            draw.ellipse([cx-r+12, cy-r+12, cx+r-12, cy+r-12], outline="black", width=sw)
        elif sym_type == "Position":
            draw.ellipse([cx-r, cy-r, cx+r, cy+r], outline="black", width=sw)
            draw.line([cx, cy-r-5, cx, cy+r+5], fill="black", width=sw)
            draw.line([cx-r-5, cy, cx+r+5, cy], fill="black", width=sw)
        elif sym_type == "Symmetry":
            draw.line([cx-r, cy-12, cx+r, cy-12], fill="black", width=sw)
            draw.line([cx-r-10, cy, cx+r+10, cy], fill="black", width=sw)
            draw.line([cx-r, cy+12, cx+r, cy+12], fill="black", width=sw)
        elif sym_type == "Angularity":
            draw.line([cx-r, cy+r, cx+r, cy+r], fill="black", width=sw)
            draw.line([cx-r, cy+r, cx+r, cy-r], fill="black", width=sw)
        elif sym_type == "Parallelism":
            draw.line([cx-8, cy+r, cx+8, cy-r], fill="black", width=sw)
            draw.line([cx+2, cy+r, cx+18, cy-r], fill="black", width=sw)
        elif sym_type == "Perpendicularity":
            draw.line([cx-r, cy+r, cx+r, cy+r], fill="black", width=sw)
            draw.line([cx, cy+r, cx, cy-r], fill="black", width=sw)
        elif sym_type == "Circular Runout":
            draw.line([cx-r, cy+r, cx+r, cy-r], fill="black", width=sw)
            draw.polygon([(cx+r, cy-r), (cx+r-10, cy-r+2), (cx+r-2, cy-r+10)], fill="black")
        elif sym_type == "Total Runout":
            draw.line([cx-r, cy+r, cx+r-10, cy-r], fill="black", width=sw)
            draw.line([cx-r+15, cy+r, cx+r+5, cy-r], fill="black", width=sw)
            draw.line([cx-r, cy+r, cx-r+15, cy+r], fill="black", width=sw)
            draw.polygon([(cx+r-10, cy-r), (cx+r-20, cy-r+5), (cx+r-12, cy-r+15)], fill="black")
            draw.polygon([(cx+r+5, cy-r), (cx+r-5, cy-r+5), (cx+r+3, cy-r+15)], fill="black")
        elif sym_type == "Profile of a Line":
            draw.arc([cx-r, cy-r, cx+r, cy+r], start=180, end=0, fill="black", width=sw)
        elif sym_type == "Profile of a Surface":
            draw.arc([cx-r, cy-r, cx+r, cy+r], start=180, end=0, fill="black", width=sw)
            draw.line([cx-r, cy, cx+r, cy], fill="black", width=sw)

    def intersects(self, new_box, existing_boxes):
        """Vérifie si la nouvelle boîte chevauche les anciennes"""
        for box in existing_boxes:
            # box = [x1, y1, x2, y2]
            if not (new_box[2] < box[0] or new_box[0] > box[2] or 
                    new_box[3] < box[1] or new_box[1] > box[3]):
                return True
        return False

    

    def generate_sample(self, img_idx):
        canvas_size = 1024
        img = Image.new('RGB', (canvas_size, canvas_size), "white")
        draw = ImageDraw.Draw(img)
        
        try: font = ImageFont.truetype("arial.ttf", 36)
        except: font = ImageFont.load_default()

        num_gdts = random.randint(2, 4) # 2 à 4 GDTs par page pour le bruit
        placed_boxes = []
        yolo_annotations = []
        donut_labels = []

        for i in range(num_gdts):
            h = 100
            cell_widths = [100, 220, 100, 100]
            w_total = sum(cell_widths)
            
            # Recherche d'un emplacement sans collision
            found_spot = False
            for _ in range(100):
                x = random.randint(50, canvas_size - w_total - 50)
                y = random.randint(50, canvas_size - h - 50)
                new_box = [x, y, x + w_total, y + h]
                
                if not self.intersects(new_box, placed_boxes):
                    placed_boxes.append(new_box)
                    found_spot = True
                    break
            
            if not found_spot: continue 

            # Données aléatoires pour le GDT
            sym_name = random.choice(self.symbol_list)
            tol_val = f"0.{random.randint(10, 99)}"
            d1, d2 = random.sample(self.datums, 2)

            # Dessin du cadre
            curr_x = x
            for idx, w in enumerate(cell_widths):
                draw.rectangle([curr_x, y, curr_x + w, y + h], outline="black", width=4)
                mid = (curr_x + w//2, y + h//2)
                if idx == 0: self.draw_symbol(draw, curr_x, y, 100, sym_name)
                elif idx == 1: draw.text(mid, tol_val, fill="black", font=font, anchor="mm")
                elif idx == 2: draw.text(mid, d1, fill="black", font=font, anchor="mm")
                elif idx == 3: draw.text(mid, d2, fill="black", font=font, anchor="mm")
                curr_x += w

            # 1. Annotation YOLO OBB (Normalisée)[cite: 1]
            x1, y1 = x/canvas_size, y/canvas_size
            x2, y2 = (x+w_total)/canvas_size, y/canvas_size
            x3, y3 = (x+w_total)/canvas_size, (y+h)/canvas_size
            x4, y4 = x/canvas_size, (y+h)/canvas_size
            yolo_annotations.append(f"0 {x1} {y1} {x2} {y2} {x3} {y3} {x4} {y4}")

            # 2. Label JSON pour Donut/VLM[cite: 1]
            donut_labels.append({
                "box_2d": [y, x, y + h, x + w_total], # format [ymin, xmin, ymax, xmax]
                "symbol": sym_name,
                "tolerance": tol_val,
                "datums": [d1, d2]
            })

        # Sauvegardes
        base_name = f"gdt_train_{img_idx}"
        img.save(os.path.join(self.output_dir, f"{base_name}.png"))
        
        with open(os.path.join(self.output_dir, f"{base_name}.txt"), "w") as f:
            f.write("\n".join(yolo_annotations))
            
        with open(os.path.join(self.output_dir, f"{base_name}.json"), "w") as f:
            json.dump({"image": f"{base_name}.png", "annotations": donut_labels}, f, indent=2)

        print(f"Généré : {base_name} avec {len(donut_labels)} GDTs")

# Génération du dataset de 13 images
engine = GDTDatasetGenerator()
for i in range(13):
    engine.generate_sample(i)