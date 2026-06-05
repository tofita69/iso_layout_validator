import cv2
import numpy as np
from PIL import Image, ImageDraw
from pathlib import Path
from ultralytics import YOLO
import easyocr
import re

# ==========================================
# 1. MODEL INITIALIZATION
# ==========================================
def load_yolo_model():
    """Load the enhanced YOLO model with smart path resolution."""
    
    # 1. Start from the current file's directory
    current_dir = Path(__file__).resolve().parent
    
    # 2. Search upwards until we find the root 'iso_layout_validator' folder
    while current_dir.name != 'iso_layout_validator' and current_dir.parent != current_dir:
        current_dir = current_dir.parent
        
    # 3. Construct the exact path to your custom weights
    custom_model_path = current_dir / "runs" / "detect" / "yolov11_iso_cartouche_enhanced" / "weights" / "best.pt"
    
    print("\n" + "="*50)
    print(f"🔍 Searching for custom model at:\n{custom_model_path}")
    
    if custom_model_path.exists():
        print("✅ SUCCESS: Custom Enhanced Model Found!")
        print("="*50 + "\n")
        return YOLO(str(custom_model_path))
    else:
        print("❌ WARNING: Custom model NOT found!")
        print("Falling back to default YOLO (This will NOT detect cartouches!).")
        print("="*50 + "\n")
        # Fallback
        fallback_path = current_dir / "yolo11n.pt"
        return YOLO(str(fallback_path))

def load_ocr_model():
    """Initialize EasyOCR."""
    return easyocr.Reader(['en'], gpu=False)

# ==========================================
# 2. PIPELINE UTILITIES
# ==========================================
def run_yolo_inference(image, model, min_confidence=0.77):
    """Run YOLO inference safely."""
    try:
        image_array = np.array(image.convert("RGB"))
        return model(image_array, conf=min_confidence)
    except Exception as e:
        print(f"Inference Error: {e}")
        return None

def extract_all_detections_from_yolo(results, image_size, model):
    """Extract standard bbox data from YOLO predictions."""
    detections = []
    if not results or len(results) == 0 or results[0].boxes is None:
        return detections

    result = results[0]
    class_names = model.names if hasattr(model, "names") else {}
    
    for idx, box in enumerate(result.boxes):
        cls_id = int(box.cls)
        conf = float(box.conf)
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        class_name = class_names.get(cls_id, f"class_{cls_id}")
        
        detections.append({
            "id": idx,
            "class_id": cls_id,
            "class_name": class_name,
            "confidence": conf,
            "bbox": [x1, y1, x2, y2]
        })
    return detections

def draw_all_detection_boxes(image, detections):
    """Draw all detected classes with color-coded bounding boxes."""
    if not detections:
        return image

    class_colors = {
        "title_block": "lime",
        "notes": "yellow",
        "gdt_feature": "cyan",
    }

    image_copy = image.copy()
    draw = ImageDraw.Draw(image_copy)
    for det in detections:
        bbox = det["bbox"]
        class_name = det["class_name"]
        color = class_colors.get(class_name, "orange")
        label = f"{class_name} ({det['confidence']:.2f})"
        draw.rectangle(bbox, outline=color, width=3)
        draw.text((bbox[0] + 4, max(0, bbox[1] - 18)), label, fill=color)
    return image_copy

def extract_text(ocr_model, img_array):
    """Runs EasyOCR on a numpy array."""
    extracted_text = []
    try:
        results = ocr_model.readtext(img_array)
        for (bbox, text, prob) in results:
            if text:
                extracted_text.append(str(text))
    except Exception as e:
        print(f"OCR Error: {e}")
        
    return " ".join(extracted_text)


# ==========================================
# 3. GEOMETRIC UTILITIES FOR OBB
# ==========================================
def order_points(pts):
    """Orders 4 points: top-left, top-right, bottom-right, bottom-left"""
    rect = np.zeros((4, 2), dtype="float32")
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]
    return rect

def four_point_transform(image, pts):
    """Applies a perspective transform to flatten the oriented bounding box"""
    rect = order_points(pts)
    (tl, tr, br, bl) = rect

    widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
    maxWidth = max(int(widthA), int(widthB))

    heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
    heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
    maxHeight = max(int(heightA), int(heightB))

    dst = np.array([
        [0, 0],
        [maxWidth - 1, 0],
        [maxWidth - 1, maxHeight - 1],
        [0, maxHeight - 1]], dtype="float32")

    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))
    return warped


def draw_cartouche_box(image, cartouche_info):
    """Draw cartouche bounding box on the image"""
    if not cartouche_info["detected"] or cartouche_info["bbox"] is None:
        return image

    image_copy = image.copy()
    draw = ImageDraw.Draw(image_copy)
    bbox = cartouche_info["bbox"]
    draw.rectangle(bbox, outline="lime", width=4)
    label = f"Cartouche (conf: {cartouche_info['confidence']:.2f})"
    draw.text((bbox[0] + 5, bbox[1] - 20), label, fill="lime")
    return image_copy

# ==========================================
# 4. COMPLIANCE ENGINE
# ==========================================
def verify_cartouche_compliance(extracted_text: str):
    """Cross-references text against the 076-A CSV Cartouche checklist."""
    text_upper = extracted_text.upper()
    
    # Enhanced Regex rules based on standard ISO fields and your specific cartouche
    rules = {
        "Reference_Module": r"\bV[0-9]+\b",                  # Strictly matches module versions like V1, V2
        "Nom_Dessinateur": r"(LABOUREAU|CAMPOCASSO)",        
        "Echelle": r"\b\d+\s?:\s?\d+\b",                     # Strictly matches ratios like 1:3, ignores the word "ECH"
        "Format": r"\bA[0-4]\b",                             
        "Matiere_Materiel": r"(EN-GJL\s?\d+|ACIER|ALU|BRONZE)",
        "Date_Creation": r"\b\d{2}[/-]\d{2}[/-]?\s?\d{4}\b"  # NEW: Enforces a date format like 12/03 2018
    }
    
    report = {}
    passed_count = 0
    
    for criterion, pattern in rules.items():
        match = re.search(pattern, text_upper)
        if match:
            report[criterion] = {"status": "PASS", "found_indicator": match.group(0)}
            passed_count += 1
        else:
            report[criterion] = {"status": "FAIL", "found_indicator": None}
            
    is_compliant = passed_count == len(rules)
    
    return {
        "overall_status": "COMPLIANT" if is_compliant else "NON-COMPLIANT",
        "score": f"{passed_count}/{len(rules)}",
        "details": report
    }