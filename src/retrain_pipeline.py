"""
Enhanced Training Pipeline for ISO Cartouche Detection
Generates 150 new ISO sheets, augments them, prepares dataset, and trains YOLO with more epochs
"""

import os
import sys
import subprocess
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from data_engine_v2 import ISOEngineeringDrawingGenerator


def step_1_generate_sheets():
    """Step 1: Generate 150 new ISO technical sheets"""
    print("\n" + "="*80)
    print("STEP 1: Generating 150 new ISO technical sheets...")
    print("="*80)
    
    gen = ISOEngineeringDrawingGenerator(output_dir="iso_technical_sheets")
    num_samples = 150
    
    try:
        for i in range(num_samples):
            gen.generate_sheet(i)
            
            if (i + 1) % 10 == 0:
                print(f"✓ Progress: {i + 1}/{num_samples} sheets generated")
        
        print(f"\n✅ Successfully generated {num_samples} new ISO sheets")
        print(f"   Location: {gen.output_dir}/")
        return True
    
    except Exception as e:
        print(f"\n❌ Error during sheet generation: {e}")
        return False


def step_2_augment_data():
    """Step 2: Augment the generated sheets"""
    print("\n" + "="*80)
    print("STEP 2: Augmenting generated sheets (2 copies per sheet)...")
    print("="*80)
    
    try:
        # Run augment_data.py with 2 augmented copies per image
        cmd = [
            sys.executable, 
            "src/augment_data.py",
            "--input-dir", "iso_technical_sheets",
            "--output-dir", "iso_technical_sheets_augmented",
            "--preview-dir", "iso_technical_sheets_augmented_previews",
            "--copies", "2",
            "--no-annotations"  # Keep annotations
        ]
        
        print(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, cwd=str(Path(__file__).parent.parent), check=True)
        
        print("\n✅ Data augmentation completed successfully")
        print("   Output: iso_technical_sheets_augmented/")
        return True
    
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error during augmentation: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return False


def step_3_prepare_dataset():
    """Step 3: Prepare YOLO dataset structure"""
    print("\n" + "="*80)
    print("STEP 3: Preparing YOLO dataset structure...")
    print("="*80)
    
    try:
        # Run prepare_dataset.py
        cmd = [sys.executable, "src/prepare_dataset.py"]
        
        print(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, cwd=str(Path(__file__).parent.parent), check=True)
        
        print("\n✅ Dataset preparation completed successfully")
        print("   Output: data/yolo_dataset/")
        return True
    
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error during dataset preparation: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return False


def step_4_train_model():
    """Step 4: Train YOLO model with enhanced parameters"""
    print("\n" + "="*80)
    print("STEP 4: Training YOLO model with enhanced parameters...")
    print("="*80)
    print("\nTraining Configuration:")
    print("  - Epochs: 150 (enhanced from 50)")
    print("  - Batch Size: 4")
    print("  - Image Size: 1024")
    print("  - Patience: 20 (early stopping)")
    print("  - Device: CPU")
    print("  - Data: dataset.yaml")
    
    try:
        from ultralytics import YOLO
        import yaml
        
        # Ensure dataset.yaml exists
        dataset_yaml_path = Path(__file__).parent.parent / "dataset.yaml"
        
        if not dataset_yaml_path.exists():
            print(f"\n⚠️  Warning: dataset.yaml not found at {dataset_yaml_path}")
            print("   Make sure dataset.yaml exists before training.")
            return False
        
        # Load and display dataset config
        with open(dataset_yaml_path, 'r') as f:
            dataset_config = yaml.safe_load(f)
            print(f"\n  Dataset Configuration loaded:")
            print(f"    - Classes: {dataset_config.get('names', {})}")
        
        # Initialize model
        print("\n  Loading YOLOv11 nano model...")
        model = YOLO("yolo11n.pt")
        
        # Enhanced training parameters
        print("  Starting training...")
        results = model.train(
            data="dataset.yaml",
            epochs=150,              # Increased from 50
            imgsz=1024,             # Keep image size
            batch=4,                # Batch size for CPU
            device="cpu",           # CPU training
            name="yolov11_iso_cartouche_v2",
            patience=20,            # Early stopping patience
            save=True,              # Save checkpoints
            plots=True,             # Generate training plots
            mosaic=1.0,             # Enable mosaic augmentation
            mixup=0.1,              # Enable mixup augmentation
            flipud=0.5,             # Flip images upside-down
            fliplr=0.5,             # Flip images left-right
            hsv_h=0.015,            # HSV-Hue augmentation
            hsv_s=0.7,              # HSV-Saturation augmentation
            hsv_v=0.4,              # HSV-Value augmentation
            degrees=10,             # Rotation
            translate=0.1,          # Translation
            scale=0.5,              # Scaling
            perspective=0.0,        # Perspective
            shear=0.0,              # Shear
            verbose=True
        )
        
        print("\n✅ Model training completed successfully!")
        print(f"   Results saved to: runs/detect/yolov11_iso_cartouche_v2/")
        
        # Copy best weights to project root
        best_weights = Path(__file__).parent.parent / "runs" / "detect" / "yolov11_iso_cartouche_v2" / "weights" / "best.pt"
        if best_weights.exists():
            import shutil
            new_model_path = Path(__file__).parent.parent / "yolo11n_v2_enhanced.pt"
            shutil.copy(best_weights, new_model_path)
            print(f"   Best model saved to: {new_model_path}")
        
        return True
    
    except Exception as e:
        print(f"\n❌ Error during model training: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Execute the complete retraining pipeline"""
    print("\n" + "🚀 "*40)
    print("ISO CARTOUCHE DETECTION - ENHANCED RETRAINING PIPELINE")
    print("🚀 "*40)
    
    steps = [
        ("Sheet Generation", step_1_generate_sheets),
        ("Data Augmentation", step_2_augment_data),
        ("Dataset Preparation", step_3_prepare_dataset),
        ("Model Training", step_4_train_model),
    ]
    
    results = []
    
    for step_name, step_func in steps:
        success = step_func()
        results.append((step_name, success))
        
        if not success:
            print(f"\n⚠️  Pipeline stopped at: {step_name}")
            break
    
    # Print summary
    print("\n" + "="*80)
    print("PIPELINE SUMMARY")
    print("="*80)
    
    for step_name, success in results:
        status = "✅ COMPLETED" if success else "❌ FAILED"
        print(f"{step_name:.<40} {status}")
    
    all_success = all(success for _, success in results)
    
    if all_success:
        print("\n" + "🎉 "*40)
        print("✅ ENHANCED TRAINING PIPELINE COMPLETED SUCCESSFULLY!")
        print("🎉 "*40)
        print("\nYour new model is ready for testing in demo_01.py")
        print("Update the model path in demo_01.py to use: yolo11n_v2_enhanced.pt")
    else:
        print("\n❌ Pipeline encountered errors. Please review the output above.")
    
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
