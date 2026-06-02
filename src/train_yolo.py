from ultralytics import YOLO

def train_model():
    model = YOLO("yolo11n.pt") 

    print("Starting YOLOv11 Training on GPU...")
    print("Configuration:")
    print("  - Epochs: 150")
    print("  - Batch Size: 4")
    print("  - Image Size: 1024")
    print("  - Augmentation: Enabled (mosaic, mixup, flip, HSV, rotate)")
    print("  - Device: GPU (cuda:0)")
    print("  - Patience: 20 (early stopping)")
    
    results = model.train(
        data="dataset.yaml", 
        epochs=150,              # Increased from 50 for better convergence
        imgsz=1024,             # Image size
        batch=4,                # Batch size (adjust for your RAM)
        device=0,               # Use first CUDA GPU (cuda:0)
        name="yolov11_iso_cartouche_enhanced", 
        patience=20,            # Early stopping patience
        save=True,              # Save best model
        plots=True,             # Generate training plots
        
        # Data Augmentation Parameters
        mosaic=1.0,             # Mosaic augmentation
        mixup=0.1,              # Mixup augmentation (0.0-1.0)
        flipud=0.5,             # Flip upside-down probability
        fliplr=0.5,             # Flip left-right probability
        hsv_h=0.015,            # HSV-Hue augmentation
        hsv_s=0.7,              # HSV-Saturation augmentation
        hsv_v=0.4,              # HSV-Value augmentation
        degrees=10,             # Rotation degrees
        translate=0.1,          # Translation
        scale=0.5,              # Scale (zoom)
        perspective=0.0,        # Perspective augmentation
        shear=0.0,              # Shear augmentation
        
        verbose=True
    )
    
    print("\n✅ Training completed!")
    print(f"Results saved to: runs/detect/yolov11_iso_cartouche_enhanced/")

if __name__ == "__main__":
    train_model()