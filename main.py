import io
import base64
import json
import numpy as np
from PIL import Image
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from ml_pipeline import (
    load_yolo_model, 
    load_ocr_model, 
    run_yolo_inference, 
    extract_all_detections_from_yolo, 
    extract_text,
    verify_cartouche_compliance,
    draw_all_detection_boxes
)

app = FastAPI(title="ECM ISO Layout Validator API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

print("Loading YOLO and OCR Models into memory...")
yolo_model = load_yolo_model()
ocr_model = load_ocr_model()
print("Models loaded successfully!")

class VerifyRequest(BaseModel):
    extracted_text: str

def encode_image_to_base64(pil_image):
    buffered = io.BytesIO()
    pil_image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")


# ==========================================
# STAGE 1: YOLO LOCALIZATION ONLY
# ==========================================
@app.post("/api/v1/localize")
async def localize_api(file: UploadFile = File(...)):
    contents = await file.read()
    image = Image.open(io.BytesIO(contents)).convert("RGB")
    
    results = run_yolo_inference(image, yolo_model)
    if not results:
        return {"status": "error", "message": "YOLO inference failed."}
        
    detections = extract_all_detections_from_yolo(results, image.size, yolo_model)
    
    # Draw boxes on the full image
    annotated_pil = draw_all_detection_boxes(image, detections)
    annotated_b64 = encode_image_to_base64(annotated_pil)

    final_detections = {}

    for i, det in enumerate(detections):
        x1, y1, x2, y2 = det["bbox"]
        
        # Crop the image and convert to Base64 (NO OCR yet)
        crop_pil = image.crop((x1, y1, x2, y2))
        crop_b64 = encode_image_to_base64(crop_pil) 
        
        dict_key = f"{det['class_name']}_{i}"
        final_detections[dict_key] = {
            "class": det["class_name"],
            "confidence": round(det["confidence"], 2),
            "bbox": [x1, y1, x2, y2],
            "image_base64": crop_b64 
        }

    return {
        "status": "success", 
        "data": final_detections, 
        "annotated_image": annotated_b64 
    }


# ==========================================
# STAGE 2: EASYOCR TEXT EXTRACTION ONLY
# ==========================================
@app.post("/api/v1/ocr")
async def ocr_api(file: UploadFile = File(...), detections: str = Form(...)):
    """Receives the original image and the JSON coordinates from Stage 1."""
    contents = await file.read()
    image = Image.open(io.BytesIO(contents)).convert("RGB")
    img_array = np.array(image)
    
    # Parse the YOLO coordinates sent from React
    boxes_data = json.loads(detections)
    ocr_results = {}

    for key, det in boxes_data.items():
        x1, y1, x2, y2 = det["bbox"]
        crop_array = img_array[y1:y2, x1:x2]
        
        # Run EasyOCR only on the requested bounding boxes
        extracted_text = extract_text(ocr_model, crop_array)
        
        ocr_results[key] = {
            "class": det["class"],
            "confidence": det["confidence"],
            "bbox": det["bbox"],
            "extracted_text": extracted_text
        }

    return {"status": "success", "data": ocr_results}


# ==========================================
# STAGE 4: COMPLIANCE
# ==========================================
@app.post("/api/v1/verify")
async def verify_compliance_api(request: VerifyRequest):
    report = verify_cartouche_compliance(request.extracted_text)
    return report