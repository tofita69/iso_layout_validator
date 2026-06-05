"""
Demo 01: ISO Cartouche Extraction
First phase of the project - Extract and display cartouche information
from technical drawings using YOLO inference on PNG images
"""

import streamlit as st
import json
import os
from pathlib import Path
from PIL import Image, ImageDraw
import numpy as np
from ultralytics import YOLO
import cv2

# Minimum confidence accepted for detections shown in UI/cache
MIN_CONFIDENCE = 0.77

# Page configuration
st.set_page_config(
    page_title="ISO Cartouche Extractor - Phase 1",
    page_icon="📋",
    layout="wide"
)

st.title("📋 ISO Cartouche Extraction - Phase 1 Demo")
st.markdown("Extract and display cartouche information from technical drawings using YOLO inference")

# ============================================================================
# SIDEBAR - Data Source Selection
# ============================================================================
st.sidebar.header("📁 Data Source")
data_source = st.sidebar.radio(
    "Select data source:",
    options=["Image Inference (YOLO)", "Upload JSON", "Browse Synthetic Data"],
    help="Choose between YOLO inference on images or JSON data"
)

st.sidebar.header("🤖 Model Selection")
model_choice = st.sidebar.radio(
    "Select YOLO Model:",
    options=["yolo11n.pt (Original)", "yolo11n_v2_enhanced.pt (Enhanced)"],
    help="Choose between original or enhanced trained model"
)

# ============================================================================
# MODEL LOADING (Cached for performance)
# ============================================================================

@st.cache_resource
def load_yolo_model(model_name):
    """Load the selected YOLO model"""
    model_mapping = {
        "yolo11n.pt (Original)": "yolo11n.pt",
        # Replace the old enhanced weights with the newly trained best checkpoint
        "yolo11n_v2_enhanced.pt (Enhanced)": "runs/detect/yolov11_iso_cartouche_enhanced/weights/best.pt"
    }
    
    model_filename = model_mapping.get(model_name, "yolo11n.pt")
    # Allow mapping values to be either a filename (relative to project root)
    # or a relative path (e.g. runs/.../weights/best.pt).
    model_path = (Path(__file__).parent.parent / model_filename).resolve()
    
    if not model_path.exists():
        st.error(f"YOLO model not found at {model_path}")
        return None
    
    try:
        st.info(f"Loading model: {model_filename}")
        model = YOLO(str(model_path))
        return model
    except Exception as e:
        st.error(f"Error loading YOLO model: {e}")
        return None

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def run_yolo_inference(image, model):
    """Run YOLO inference on an image and return results"""
    try:
        # YOLO expects 3-channel input. Screenshots may be RGBA (4 channels),
        # so normalize to RGB before converting to numpy.
        image_rgb = image.convert("RGB")
        image_array = np.array(image_rgb)
        
        # Run inference
        results = model(image_array, conf=MIN_CONFIDENCE)
        
        return results
    except Exception as e:
        st.error(f"Error running inference: {e}")
        return None


def extract_cartouche_from_yolo(results, image_size):
    """
    Extract cartouche (title block) information from YOLO predictions
    Looks specifically for class 0 (cartouche/title block)
    """
    cartouche_info = {
        "detected": False,
        "confidence": 0,
        "bbox": None,
        "bbox_normalized": None,
    }
    
    if not results or len(results) == 0:
        return cartouche_info
    
    result = results[0]
    
    if result.boxes is None or len(result.boxes) == 0:
        return cartouche_info
    
    # Find cartouche detections (class 0 only)
    boxes = result.boxes
    
    # Look for class 0 (cartouche) detections
    for box in boxes:
        cls = int(box.cls)
        conf = float(box.conf)
        
        # Only process class 0 (cartouche)
        if cls != 0:
            continue
        
        # Get bounding box coordinates
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        
        # Store the cartouche detection with highest confidence
        if conf > cartouche_info["confidence"]:
            cartouche_info["detected"] = True
            cartouche_info["confidence"] = conf
            cartouche_info["bbox"] = [x1, y1, x2, y2]
            cartouche_info["bbox_normalized"] = [
                x1 / image_size[0],
                y1 / image_size[1],
                x2 / image_size[0],
                y2 / image_size[1]
            ]
            cartouche_info["class"] = cls
    
    return cartouche_info


def extract_all_detections_from_yolo(results, image_size, model):
    """Extract all detections (title_block, notes, gdt_feature) from YOLO predictions."""
    detections = []
    if not results or len(results) == 0:
        return detections

    result = results[0]
    if result.boxes is None or len(result.boxes) == 0:
        return detections

    class_names = model.names if hasattr(model, "names") else {}
    boxes = result.boxes
    for idx, box in enumerate(boxes):
        cls_id = int(box.cls)
        conf = float(box.conf)
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        class_name = class_names.get(cls_id, f"class_{cls_id}")
        detections.append(
            {
                "id": idx,
                "class_id": cls_id,
                "class_name": class_name,
                "confidence": conf,
                "bbox": [x1, y1, x2, y2],
                "bbox_normalized": [
                    x1 / image_size[0],
                    y1 / image_size[1],
                    x2 / image_size[0],
                    y2 / image_size[1],
                ],
            }
        )
    return detections


def draw_cartouche_box(image, cartouche_info):
    """Draw cartouche bounding box on the image"""
    if not cartouche_info["detected"] or cartouche_info["bbox"] is None:
        return image
    
    image_copy = image.copy()
    draw = ImageDraw.Draw(image_copy)
    
    bbox = cartouche_info["bbox"]
    # Draw rectangle with green color and thick border
    draw.rectangle(bbox, outline="lime", width=4)
    
    # Add label
    label = f"Cartouche (conf: {cartouche_info['confidence']:.2f})"
    draw.text((bbox[0] + 5, bbox[1] - 20), label, fill="lime")
    
    return image_copy


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


def cache_detection_crops(image, detections, source_key):
    """Store cropped detections in session cache for quick review in sidebar."""
    if "detection_cache" not in st.session_state:
        st.session_state["detection_cache"] = {}

    cache_items = []
    for det in detections:
        x1, y1, x2, y2 = det["bbox"]
        crop = image.crop((x1, y1, x2, y2))
        cache_items.append(
            {
                "class_name": det["class_name"],
                "class_id": det["class_id"],
                "confidence": det["confidence"],
                "crop": crop,
                "bbox": det["bbox"],
            }
        )

    st.session_state["detection_cache"][source_key] = cache_items


def display_detection_cache_sidebar():
    """Render cached detection crops in the sidebar."""
    st.sidebar.header("🗂️ Detection Cache")
    cache = st.session_state.get("detection_cache", {})
    if not cache:
        st.sidebar.caption("No cached detections yet.")
        return

    latest_key = list(cache.keys())[-1]
    items = cache[latest_key]
    st.sidebar.caption(f"Latest: {latest_key}")
    st.sidebar.caption(f"Cached crops: {len(items)}")

    class_order = ["title_block", "notes", "gdt_feature"]
    for cls in class_order:
        class_items = [item for item in items if item["class_name"] == cls]
        with st.sidebar.expander(f"{cls} ({len(class_items)})", expanded=False):
            if not class_items:
                st.caption("No detections.")
                continue
            for i, item in enumerate(class_items, start=1):
                st.image(item["crop"], use_container_width=True)
                st.caption(f"#{i} conf={item['confidence']:.2f} bbox={item['bbox']}")


def display_yolo_results(cartouche_info, col):
    """Display YOLO inference results"""
    with col:
        st.subheader("🎯 YOLO Detection Results")
        
        if not cartouche_info["detected"]:
            st.warning("No cartouche detected in the image")
            return
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Detection", "✓ Found")
        with col2:
            st.metric("Confidence", f"{cartouche_info['confidence']:.2%}")
        with col3:
            st.metric("Class ID", cartouche_info.get("class", "N/A"))
        
        st.markdown("**Bounding Box Coordinates (pixels):**")
        bbox = cartouche_info["bbox"]
        st.markdown(f"""
        - **Top-Left:** ({bbox[0]}, {bbox[1]})
        - **Bottom-Right:** ({bbox[2]}, {bbox[3]})
        - **Width:** {bbox[2] - bbox[0]} px
        - **Height:** {bbox[3] - bbox[1]} px
        - **Area:** {(bbox[2] - bbox[0]) * (bbox[3] - bbox[1])} px²
        """)


def load_iso_technical_sheet(json_path):
    """Load ISO technical sheet JSON file"""
    try:
        with open(json_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Error loading file: {e}")
        return None


def extract_cartouche_info(sheet_data):
    """Extract cartouche (title block) information from sheet data"""
    cartouche = {}
    
    if "components" in sheet_data:
        components = sheet_data["components"]
        
        # Extract title block bbox
        if "title_block" in components:
            cartouche["title_block_bbox"] = components["title_block"]
        
        # Extract other relevant cartouche components
        if "notes" in components:
            cartouche["notes_bbox"] = components["notes"]
        
        # Store GDT features count
        if "gdt_features" in components:
            cartouche["gdt_features_count"] = len(components["gdt_features"])
            cartouche["gdt_features"] = components["gdt_features"]
    
    # Add filename
    if "filename" in sheet_data:
        cartouche["filename"] = sheet_data["filename"]
    
    return cartouche


def display_cartouche_info(cartouche, col):
    """Display cartouche information in a clean format"""
    with col:
        st.subheader("📋 Cartouche Information")
        
        if "filename" in cartouche:
            st.markdown(f"**Drawing File:** `{cartouche['filename']}`")
        
        if "title_block_bbox" in cartouche:
            bbox = cartouche["title_block_bbox"]
            st.markdown(f"""
            **Title Block (Cartouche) Bounding Box:**
            - X: {bbox[0]} - {bbox[2]} px (width: {bbox[2]-bbox[0]} px)
            - Y: {bbox[1]} - {bbox[3]} px (height: {bbox[3]-bbox[1]} px)
            """)
        
        if "notes_bbox" in cartouche:
            bbox = cartouche["notes_bbox"]
            st.markdown(f"""
            **Notes Section Bounding Box:**
            - X: {bbox[0]} - {bbox[2]} px (width: {bbox[2]-bbox[0]} px)
            - Y: {bbox[1]} - {bbox[3]} px (height: {bbox[3]-bbox[1]} px)
            """)
        
        if "gdt_features_count" in cartouche:
            st.markdown(f"**GDT Features Found:** {cartouche['gdt_features_count']}")


def display_gdt_features(cartouche, col):
    """Display GDT features found in the drawing"""
    with col:
        st.subheader("🔧 GDT Features Detected")
        
        if "gdt_features" not in cartouche or not cartouche["gdt_features"]:
            st.info("No GDT features found in this drawing")
            return
        
        features = cartouche["gdt_features"]
        
        # Summary
        st.metric("Total Features", len(features))
        
        # Create feature table
        feature_data = []
        for idx, feature in enumerate(features, 1):
            feature_data.append({
                "#": idx,
                "Symbol": feature.get("symbol", "N/A"),
                "Tolerance": feature.get("tolerance", "N/A"),
                "Datums": ", ".join(feature.get("datums", [])),
            })
        
        st.dataframe(feature_data, use_container_width=True)
        
        # Expandable detailed view
        with st.expander("📊 Detailed Feature Information"):
            for idx, feature in enumerate(features, 1):
                st.markdown(f"**Feature {idx}: {feature.get('symbol', 'Unknown')}**")
                col_detail1, col_detail2 = st.columns(2)
                with col_detail1:
                    st.markdown(f"- **Tolerance:** {feature.get('tolerance', 'N/A')}")
                    st.markdown(f"- **Datums:** {', '.join(feature.get('datums', []))}")
                with col_detail2:
                    bbox = feature.get("bbox_pixels", [])
                    if bbox:
                        st.markdown(f"- **BBox X:** {bbox[0]}-{bbox[2]}")
                        st.markdown(f"- **BBox Y:** {bbox[1]}-{bbox[3]}")


# ============================================================================
# MAIN CONTENT
# ============================================================================

# ============================================================================
# MAIN CONTENT
# ============================================================================

if data_source == "Image Inference (YOLO)":
    st.markdown("### 📸 YOLO Cartouche Detection from PNG Images")
    
    # Load YOLO model based on selection
    model = load_yolo_model(model_choice)
    
    if model is None:
        st.error("Failed to load YOLO model. Please ensure the model file exists in the project root.")
    else:
        # Image upload
        uploaded_image = st.file_uploader(
            "Upload a PNG image of an ISO technical sheet",
            type=["png", "jpg", "jpeg"],
            help="Select an ISO sheet image to analyze with YOLO"
        )
        
        if uploaded_image is not None:
            # Load and display original image
            image = Image.open(uploaded_image)
            
            # Run inference
            with st.spinner("🔍 Running YOLO inference..."):
                results = run_yolo_inference(image, model)
            
            if results:
                # Extract cartouche information
                cartouche_info = extract_cartouche_from_yolo(results, image.size)
                detections = extract_all_detections_from_yolo(results, image.size, model)

                # Draw all detection boxes and cache crops for quick inspection
                image_with_box = draw_all_detection_boxes(image, detections)
                cache_detection_crops(image, detections, uploaded_image.name)
                
                # Display results in two columns
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("📷 Original Image")
                    st.image(image, use_container_width=True)
                with col2:
                    st.subheader("🎨 Annotated Image")
                    st.image(image_with_box, use_container_width=True)
                
                # Detection summary
                st.subheader("🎯 Detection Summary")
                if not detections:
                    st.warning("No objects detected.")
                else:
                    count_title = sum(1 for d in detections if d["class_name"] == "title_block")
                    count_notes = sum(1 for d in detections if d["class_name"] == "notes")
                    count_gdt = sum(1 for d in detections if d["class_name"] == "gdt_feature")
                    m1, m2, m3 = st.columns(3)
                    m1.metric("Title Blocks", count_title)
                    m2.metric("Notes", count_notes)
                    m3.metric("GDT Features", count_gdt)

                    for det in detections:
                        st.markdown(
                            f"- **{det['class_name']}** | conf: `{det['confidence']:.2f}` | bbox: `{det['bbox']}`"
                        )

                # Keep existing cartouche-focused panel for backward compatibility
                display_yolo_results(cartouche_info, st.container())

elif data_source == "Upload JSON":
    st.markdown("### 📤 Upload Technical Drawing Data")
    
    uploaded_file = st.file_uploader(
        "Upload a JSON file containing ISO technical sheet data",
        type=["json"],
        help="Select a JSON file from your synthetic data"
    )
    
    if uploaded_file is not None:
        # Parse uploaded JSON
        try:
            sheet_data = json.loads(uploaded_file.read().decode("utf-8"))
            
            # Extract cartouche information
            cartouche = extract_cartouche_info(sheet_data)
            
            if not cartouche:
                st.error("Could not extract cartouche information from the provided file")
            else:
                # Display results in two columns
                col1, col2 = st.columns(2)
                
                display_cartouche_info(cartouche, col1)
                display_gdt_features(cartouche, col2)
                
                # Display raw JSON for reference
                with st.expander("📄 Raw Data (JSON)"):
                    st.json(sheet_data)
        
        except json.JSONDecodeError as e:
            st.error(f"Invalid JSON file: {e}")
        except Exception as e:
            st.error(f"Error processing file: {e}")

else:  # Browse Synthetic Data
    st.markdown("### 📂 Browse Pre-loaded Synthetic Data")
    
    # Look for iso_technical_sheets directory
    base_path = Path(__file__).parent.parent  # Go up from src/ to project root
    iso_sheets_dir = base_path / "iso_technical_sheets"
    
    if not iso_sheets_dir.exists():
        st.error(f"Could not find iso_technical_sheets directory at {iso_sheets_dir}")
    else:
        # Get list of JSON files
        json_files = sorted([f for f in iso_sheets_dir.glob("*.json")])
        
        if not json_files:
            st.warning(f"No JSON files found in {iso_sheets_dir}")
        else:
            st.info(f"Found {len(json_files)} technical sheets")
            
            # File selector
            selected_file = st.selectbox(
                "Select a technical sheet:",
                options=json_files,
                format_func=lambda x: x.name,
                help="Choose a synthetic ISO technical sheet to analyze"
            )
            
            if selected_file:
                # Load and process the selected file
                sheet_data = load_iso_technical_sheet(selected_file)
                
                if sheet_data:
                    # Extract cartouche information
                    cartouche = extract_cartouche_info(sheet_data)
                    
                    if not cartouche:
                        st.error("Could not extract cartouche information")
                    else:
                        # Display results in two columns
                        col1, col2 = st.columns(2)
                        
                        display_cartouche_info(cartouche, col1)
                        display_gdt_features(cartouche, col2)
                        
                        # Display raw JSON for reference
                        with st.expander("📄 Raw Data (JSON)"):
                            st.json(sheet_data)

# Render detection cache panel in sidebar for all modes
display_detection_cache_sidebar()

# ============================================================================
# FOOTER
# ============================================================================
st.markdown("---")
st.markdown("""
### 📝 Phase 1 - Cartouche Extraction (YOLO-based)
**Current Capabilities:**
- ✅ YOLO inference on PNG images to detect cartouche/title block
- ✅ Bounding box visualization with confidence scores
- ✅ Pixel coordinate extraction from detections
- ✅ Model selection (Original vs Enhanced v2)
- ✅ Extract title block (cartouche) bounding boxes from JSON
- ✅ Extract notes section information from JSON
- ✅ Display GDT features with symbols, tolerances, and datums
- ✅ Support for both uploaded and pre-loaded synthetic data

**Enhanced v2 Model Features:**
- 🚀 Trained on 150 new ISO sheets (300 augmented)
- 🚀 150 epochs training with advanced augmentation
- 🚀 Better detection accuracy and reliability
- 🚀 Improved handling of various cartouche sizes and positions

**Phase 2 (Coming Soon):**
- 🔄 Enhanced notes extraction and parsing from images
- 🔄 GDT detailed analysis from detections
- 🔄 OCR-based text extraction from cartouche region
""")
