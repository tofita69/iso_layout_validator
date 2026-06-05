from ultralytics import YOLO
import cv2
import numpy as np
import os



ZONE_RULES = {
    "cartouche": {
        "position": "bottom-right",   # x > 60%, y > 60%
        "min_area_ratio": 0.02,
        "max_area_ratio": 0.25,
        "aspect_ratio_range": (1.5, 8.0),  # wider than tall
    },
    "notes": {
        "position": "any-left",        # x < 30%
        "min_area_ratio": 0.01,
        "max_area_ratio": 0.20,
    },
    "revision_table": {
        "position": "top-right",       # x > 60%, y < 40%
        "min_area_ratio": 0.01,
        "max_area_ratio": 0.15,
    },
}

def classify_zone(bbox_xyxy, img_w, img_h):
    """Classify a detected zone based on its position and shape."""
    x1, y1, x2, y2 = bbox_xyxy
    cx = (x1 + x2) / 2 / img_w   # normalized center x
    cy = (y1 + y2) / 2 / img_h   # normalized center y
    w  = (x2 - x1) / img_w
    h  = (y2 - y1) / img_h
    area_ratio = w * h
    aspect = (x2 - x1) / max((y2 - y1), 1)

    if cx > 0.55 and cy > 0.55 and 0.015 < area_ratio < 0.30:
        return "cartouche"
    if cx > 0.55 and cy < 0.45 and area_ratio < 0.15:
        return "revision_table"
    if cx < 0.35 and area_ratio < 0.20:
        return "notes"
    if area_ratio > 0.30:
        return "drawing_area"
    return "unknown"


def extract_zones(image_path, conf_threshold=0.1):
    output_dir = "data/outputs/yolo_zones"
    os.makedirs(output_dir, exist_ok=True)
    filename = os.path.basename(image_path).split('.')[0]

    img = cv2.imread(image_path)
    if img is None:
        print(f"❌ Cannot read image: {image_path}")
        return
    img_h, img_w = img.shape[:2]

    # Load YOLO11n-OBB pretrained on DOTA
    model = YOLO("yolo11n-obb.pt")  # auto-downloads on first run

    results = model.predict(
        source=image_path,
        conf=conf_threshold,   # low threshold = catch more regions
        iou=0.3,
        imgsz=1024,            # technical drawings need higher res
        verbose=False,
    )

    found_zones = {}

    for result in results:
        if result.obb is None:
            print("❌ No OBB detections.")
            continue

        # obb.xyxyxyxy → shape (N, 4, 2) — 4 corners per box
        # obb.xyxy     → axis-aligned bounding box (N, 4)
        boxes_xyxy = result.obb.xyxy.cpu().numpy()   # [x1,y1,x2,y2]
        boxes_conf  = result.obb.conf.cpu().numpy()
        boxes_obb   = result.obb.xyxyxyxy.cpu().numpy()  # rotated corners

        for i, (bbox, conf, obb_corners) in enumerate(zip(boxes_xyxy, boxes_conf, boxes_obb)):
            zone_type = classify_zone(bbox, img_w, img_h)

            print(f"  Detection {i}: conf={conf:.2f}, zone='{zone_type}', bbox={bbox.astype(int).tolist()}")

            # Crop using axis-aligned bbox
            x1, y1, x2, y2 = map(int, bbox)
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(img_w, x2), min(img_h, y2)
            crop = img[y1:y2, x1:x2]

            if crop.size == 0:
                continue

            # Save each zone
            out_path = f"{output_dir}/{filename}_{zone_type}_{i}.jpg"
            cv2.imwrite(out_path, crop)

            # Keep best (largest) per zone type
            area = (x2 - x1) * (y2 - y1)
            if zone_type not in found_zones or area > found_zones[zone_type]['area']:
                found_zones[zone_type] = {
                    'area': area,
                    'bbox': (x1, y1, x2, y2),
                    'crop_path': out_path,
                    'conf': conf,
                }

    # Summary
    print(f"\n=== Zones detected in {filename} ===")
    if not found_zones:
        print("  ❌ Nothing detected — try lowering conf_threshold further")
    for zone, info in found_zones.items():
        print(f"  ✅ {zone}: conf={info['conf']:.2f}, saved → {info['crop_path']}")

    return found_zones


if __name__ == "__main__":
    extract_zones(r"C:\Users\yassine.jaadan\iso_layout_validator\data\raw\R3.png")