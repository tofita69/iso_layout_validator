import os
import json
import random
from PIL import Image, ImageDraw, ImageFont


class ISOEngineeringDrawingGenerator:
    def __init__(self, output_dir="iso_technical_sheets"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.canvas_size = (1600, 1200)

        self.materials = ["AL-6061", "C-45 STEEL", "SUS304", "PVC-U", "AISI 4140"]
        self.finishes = ["BLUE ZINC", "NICKEL PLATED", "ANODIZED BLACK", "POWDER COATED"]
        self.datums = ["A", "B", "C", "D", "E", "F"]

        self.symbol_list = [
            "Circularity", "Cylindricity", "Flatness", "Straightness",
            "Concentricity", "Position", "Symmetry", "Angularity",
            "Parallelism", "Perpendicularity", "Circular Runout",
            "Total Runout", "Profile of a Line", "Profile of a Surface"
        ]

        try:
            self.font = ImageFont.truetype("arial.ttf", 20)
        except:
            self.font = ImageFont.load_default()

    def draw_border_and_grid(self, draw):
        w, h = self.canvas_size
        # Marges ISO : 20mm à gauche (reliure), 10mm ailleurs
        m_left, m_right, m_top, m_bottom = 80, 40, 40, 40
        
        # Cadre extérieur (épais)
        draw.rectangle([m_left, m_top, w - m_right, h - m_bottom], outline="black", width=4)
        
        # Quadrillage de repérage (Nombres en haut/bas, Lettres à gauche/droite)
        # On divise en sections de 100-200px
        cols = 8
        rows = 6
        
        for i in range(cols):
            x = m_left + (i * (w - m_left - m_right) // cols)
            draw.line([x, m_top, x, m_top - 15], fill="black", width=2)
            draw.line([x, h - m_bottom, x, h - m_bottom + 15], fill="black", width=2)
            draw.text((x + 40, m_top - 25), str(i+1), fill="black", anchor="mm", font=self.font)

        for i in range(rows):
            y = m_top + (i * (h - m_top - m_bottom) // rows)
            draw.line([m_left, y, m_left - 15, y], fill="black", width=2)
            draw.line([w - m_right, y, w - m_right + 15, y], fill="black", width=2)
            label = chr(65 + i) # A, B, C...
            draw.text((m_left - 25, y + 40), label, fill="black", anchor="mm", font=self.font)


    def draw_title_block(self, draw):
        w_img, h_img = self.canvas_size
        # Dimensions basées sur le ratio 190mm x 40mm (approx 760x160 pixels)
        bw, bh = 760, 160
        x, y = w_img - 40 - bw, h_img - 40 - bh
        
        # 1. Structure extérieure
        draw.rectangle([x, y, x + bw, y + bh], outline="black", width=4)
        
        # 2. Lignes horizontales (15mm, 15mm, 10mm -> Ratio 3:3:2)
        h1, h2 = y + 60, y + 120
        draw.line([x, h1, x + bw, h1], fill="black", width=2)
        draw.line([x, h2, x + bw, h2], fill="black", width=2)
        
        # 3. Lignes verticales
        v1, v2, v3 = x + 160, x + 320, x + 600 # Ratio 40, 40, 70, 40
        draw.line([v1, y, v1, y + bh], fill="black", width=2)
        draw.line([v2, y, v2, y + 60], fill="black", width=2) # Ligne courte pour "matière"
        draw.line([v3, y, v3, y + bh], fill="black", width=2)
        
        # 4. Symbole de Projection (Méthode E : Europe)
        self.draw_projection_symbol(draw, x + 10, y + 65, 140, 50)
        
        # 5. Textes fixes
        try: 
            f_small = ImageFont.truetype("arial.ttf", 16)
            f_med = ImageFont.truetype("arial.ttf", 22)
        except: 
            f_small = f_med = ImageFont.load_default()

        # Labels (Ligne 1)
        draw.text((x+5, y+5), "Echelle:", font=f_small, fill="black")
        draw.text((v1+5, y+5), "Matière:", font=f_small, fill="black")
        draw.text((v2+5, y+5), "Lycée Condorcet - Montreuil", font=f_med, fill="black")
        draw.text((v3+5, y+5), "Dessiné par:", font=f_small, fill="black")
        
        # Labels (Ligne 2 & 3)
        draw.text((x+5, y + 125), "Format: A3", font=f_small, fill="black")
        draw.text((v1+40, y + 70), "Désignation de la pièce", font=f_small, fill="black")
        draw.text((v1+40, y + 100), "ADMISSION SHAFT - V2", font=f_med, fill="black")
        draw.text((v3+5, y+65), "Le 04/05/2026", font=f_small, fill="black")
        draw.text((v3+5, y+125), "Classe: 1STI", font=f_small, fill="black")
        
        return [x, y, x + bw, y + bh]
    
    def draw_projection_symbol(self, draw, x, y, w, h):
        """Dessine le symbole ISO de projection européenne (cône + cercles)"""
        cx, cy = x + 30, y + h//2
        # Cercles à gauche
        draw.ellipse([cx-15, cy-15, cx+15, cy+15], outline="black", width=2)
        draw.ellipse([cx-8, cy-8, cx+8, cy+8], outline="black", width=1)
        # Axe central
        draw.line([x+5, cy, x+w-5, cy], fill="black", width=1, joint=None)
        # Cône à droite
        draw.line([x+60, cy-10, x+110, cy-18], fill="black", width=2)
        draw.line([x+60, cy+10, x+110, cy+18], fill="black", width=2)
        draw.line([x+60, cy-10, x+60, cy+10], fill="black", width=2)
        draw.line([x+110, cy-18, x+110, cy+18], fill="black", width=2)


    def draw_notes_block(self, draw):
        # On récupère les marges définies dans draw_border_and_grid
        m_left = 80
        m_bottom = 40
        
        # Dimensions du bloc
        w, h = 380, 180
        
        # Positionnement : on s'aligne sur la marge gauche + un petit padding (20px)
        # Et on se place juste au-dessus de la marge du bas
        x = m_left + 20
        y = self.canvas_size[1] - m_bottom - h - 20
        
        # Dessin du rectangle (Passage en noir pour la conformité ISO)
        draw.rectangle([x, y, x + w, y + h], outline="black", width=2)

        notes = [
            "NOTES:",
            "- ALL DIMENSIONS ARE IN mm",
            f"- UNSPECIFIED TOLERANCE: {random.choice(['0.05', '0.10', '0.02'])} mm",
            "- SHARP EDGES: 0.5 CHAMFER",
            "- INTERPRET PER ASME Y14.5-2018"
        ]

        # Utilisation d'une police légèrement plus petite pour les notes si nécessaire
        curr_y = y + 15
        for line in notes:
            draw.text((x + 15, curr_y), line, fill="black", font=self.font)
            curr_y += 30

        return [x, y, x + w, y + h]
    

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
        for box in existing_boxes:
            if not (new_box[2] < box[0] or new_box[0] > box[2] or
                    new_box[3] < box[1] or new_box[1] > box[3]):
                return True
        return False

    def draw_gdt_frame(self, draw, x, y, symbol, tol, datums):
        h = 60
        cell_widths = [60, 150] + [60] * len(datums)
        curr_x = x
        
        try: font = ImageFont.truetype("arial.ttf", 28)
        except: font = ImageFont.load_default()

        # 1. Compartiment Symbole
        draw.rectangle([curr_x, y, curr_x + cell_widths[0], y + h], outline="black", width=3)
        self.draw_symbol(draw, curr_x, y, h, symbol)
        curr_x += cell_widths[0]

        # 2. Compartiment Tolérance
        draw.rectangle([curr_x, y, curr_x + cell_widths[1], y + h], outline="black", width=3)
        
        display_tol = tol
        text_x_offset = curr_x + 15
        mid_y = y + h // 2

        # --- RANDOMISATION DES SYMBOLES DE ZONE ---
        # Gestion du Diamètre Sphérique (SØ)
        if display_tol.startswith("S\u2300"):
            # Dessin du 'S'
            draw.text((text_x_offset, mid_y), "S", fill="black", font=font, anchor="lm")
            # Dessin du Ø décalé
            dia_x = text_x_offset + 30
            draw.ellipse([dia_x-10, mid_y-10, dia_x+10, mid_y+10], outline="black", width=2)
            draw.line([dia_x-12, mid_y+12, dia_x+12, mid_y-12], fill="black", width=2)
            display_tol = display_tol[2:]
            text_x_offset += 55
            
        # Gestion du Diamètre simple (Ø)
        elif display_tol.startswith("\u2300"):
            dia_x = text_x_offset + 12
            draw.ellipse([dia_x-10, mid_y-10, dia_x+10, mid_y+10], outline="black", width=2)
            draw.line([dia_x-12, mid_y+12, dia_x+12, mid_y-12], fill="black", width=2)
            display_tol = display_tol[1:]
            text_x_offset += 35

        # Gestion de la Zone Carrée (□)
        elif display_tol.startswith("\u25FB"):
            sq_x = text_x_offset + 12
            draw.rectangle([sq_x-10, mid_y-10, sq_x+10, mid_y+10], outline="black", width=2)
            display_tol = display_tol[1:]
            text_x_offset += 35

        # Dessin de la valeur numérique et des modificateurs (M, L)
        # (On réutilise la logique de détection des modificateurs de l'étape précédente ici)
        draw.text((text_x_offset, mid_y), display_tol, fill="black", font=font, anchor="lm")
        
        curr_x += cell_widths[1]

        # 3. Compartiments Datums
        for datum in datums:
            draw.rectangle([curr_x, y, curr_x + 60, y + h], outline="black", width=3)
            draw.text((curr_x + 30, mid_y), datum, fill="black", font=font, anchor="mm")
            curr_x += 60

    def generate_sheet(self, idx):
        img = Image.new('RGB', self.canvas_size, "white")
        draw = ImageDraw.Draw(img)

        # Dessin des éléments structurels
        self.draw_border_and_grid(draw)
        title_box = self.draw_title_block(draw) # Cartouche ISO 7200
        notes_box = self.draw_notes_block(draw) # Notes alignées

        # Initialisation pour la détection de collision
        placed_boxes = [title_box, notes_box]
        gdt_annotations = []
        
        margin = 80
        h_frame = 60

        for _ in range(random.randint(3, 6)):
            

            # 1. Configurer les données d'abord pour calculer la largeur réelle
            num_datums = random.randint(1, 3)
            datums = random.sample(self.datums, num_datums)
            w_total = 210 + (60 * num_datums) # Largeur exacte : 60+150+(60*N)

            # 2. Chercher une position libre
            for _ in range(100):
                gx = random.randint(margin + 20, self.canvas_size[0] - w_total - margin - 20)
                gy = random.randint(margin + 20, self.canvas_size[1] - h_frame - 350) # Évite le cartouche

                new_box = [gx, gy, gx + w_total, gy + h_frame]

                if not self.intersects(new_box, placed_boxes):
                    placed_boxes.append(new_box)

                    # Génération du contenu ISO
                    symbol = random.choice(self.symbol_list)
                    # Choisir aléatoirement un type de zone de tolérance
                    # 40% Ø, 10% SØ, 10% Carré, 40% Rien (tolérance linéaire/planéité)
                    prefix_choice = random.choices(
                        ["\u2300", "S\u2300", "\u25FB", ""], 
                        weights=[0.4, 0.1, 0.1, 0.4]
                    )[0]

                    modifier = random.choice(["", " (M)", " (L)"])
                    val = f"{random.uniform(0.01, 0.5):.2f}"
                    tol = f"{prefix_choice}{val}{modifier}"
                    # 3. APPEL DE LA FONCTION DE DESSIN
                    self.draw_gdt_frame(draw, gx, gy, symbol, tol, datums)

                    # Annotation pour le dataset
                    gdt_annotations.append({
                        "symbol": symbol,
                        "tolerance": tol,
                        "datums": datums,
                        "bbox_pixels": new_box
                    })
                    break

        # Sauvegarde finale
        base = f"iso_sheet_{idx}"
        img.save(os.path.join(self.output_dir, f"{base}.png"))
        
        # Métadonnées sans les variables orphelines (mat_box, etc.)
        metadata = {
            "filename": f"{base}.png",
            "components": {
                "title_block": title_box,
                "notes": notes_box,
                "gdt_features": gdt_annotations
            }
        }
        with open(os.path.join(self.output_dir, f"{base}.json"), "w") as f:
            json.dump(metadata, f, indent=4)


import os

# --- Configuration et Exécution ---
if __name__ == "__main__":
    # Initialisation du générateur
    gen = ISOEngineeringDrawingGenerator()
    
    # Nombre d'exemples à générer
    num_samples = 20
    
    print(f"Démarrage de la génération de {num_samples} planches ISO...")
    
    for i in range(num_samples):
        try:
            # Génération de la planche et de son fichier JSON associé
            gen.generate_sheet(i)
            
            # Feedback visuel pour suivre la progression
            if (i + 1) % 5 == 0:
                print(f"Progression : {i + 1}/{num_samples} images générées.")
                
        except Exception as e:
            print(f"Erreur lors de la génération de l'image {i} : {e}")

    print("-" * 30)
    print(f"Terminé ! Les {num_samples} fichiers se trouvent dans : {gen.output_dir}")
    print(f"Chaque image .png a son fichier .json correspondant pour l'entraînement.")