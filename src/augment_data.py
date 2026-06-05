import argparse
import json
import math
import random
from copy import deepcopy
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageEnhance

SUPPORTED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff"}


def load_image(path: Path) -> np.ndarray:
    image = cv2.imread(str(path), cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError(f"Cannot load image: {path}")
    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)


def save_image(path: Path, image: np.ndarray) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(path), cv2.cvtColor(image, cv2.COLOR_RGB2BGR))


def load_annotations(json_path: Path):
    if not json_path.exists():
        return None
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_annotations(json_path: Path, annotation_data):
    json_path.parent.mkdir(parents=True, exist_ok=True)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(annotation_data, f, indent=4)


def clamp_box(box, width, height):
    x1, y1, x2, y2 = box
    x1 = int(max(0, min(x1, width - 1)))
    y1 = int(max(0, min(y1, height - 1)))
    x2 = int(max(0, min(x2, width - 1)))
    y2 = int(max(0, min(y2, height - 1)))
    return [min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2)]


def transform_box(box, matrix):
    pts = np.array([
        [box[0], box[1]],
        [box[2], box[1]],
        [box[2], box[3]],
        [box[0], box[3]],
    ], dtype=np.float32)
    pts = np.array([pts])
    transformed = cv2.perspectiveTransform(pts, matrix)[0]
    x_min, y_min = transformed.min(axis=0)
    x_max, y_max = transformed.max(axis=0)
    return [x_min, y_min, x_max, y_max]


def update_annotation_boxes(annotation_data, transform_fn):
    if annotation_data is None:
        return None
    data = deepcopy(annotation_data)
    comps = data.get("components", {})

    if "title_block" in comps:
        comps["title_block"] = transform_fn(comps["title_block"])
    if "notes" in comps:
        comps["notes"] = transform_fn(comps["notes"])
    if "gdt_features" in comps:
        for feature in comps["gdt_features"]:
            if "bbox_pixels" in feature:
                feature["bbox_pixels"] = transform_fn(feature["bbox_pixels"])
    return data


def rotate_image(image: np.ndarray, angle: float) -> (np.ndarray, np.ndarray):
    height, width = image.shape[:2]
    center = (width / 2.0, height / 2.0)
    matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(image, matrix, (width, height), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
    rotation_matrix = np.vstack([matrix, [0.0, 0.0, 1.0]])
    return rotated, rotation_matrix


def flip_image(image: np.ndarray, mode: str) -> (np.ndarray, np.ndarray):
    height, width = image.shape[:2]
    if mode == "horizontal":
        flipped = cv2.flip(image, 1)
        matrix = np.array([[-1.0, 0.0, width - 1], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]], dtype=np.float32)
    else:
        flipped = cv2.flip(image, 0)
        matrix = np.array([[1.0, 0.0, 0.0], [0.0, -1.0, height - 1], [0.0, 0.0, 1.0]], dtype=np.float32)
    return flipped, matrix


def perspective_transform(image: np.ndarray, max_warp=0.05) -> (np.ndarray, np.ndarray):
    height, width = image.shape[:2]
    margin_x = int(width * max_warp)
    margin_y = int(height * max_warp)

    src = np.float32([[0, 0], [width - 1, 0], [width - 1, height - 1], [0, height - 1]])
    dst = np.float32([
        [random.randint(0, margin_x), random.randint(0, margin_y)],
        [width - 1 - random.randint(0, margin_x), random.randint(0, margin_y)],
        [width - 1 - random.randint(0, margin_x), height - 1 - random.randint(0, margin_y)],
        [random.randint(0, margin_x), height - 1 - random.randint(0, margin_y)],
    ])

    matrix = cv2.getPerspectiveTransform(src, dst)
    warped = cv2.warpPerspective(image, matrix, (width, height), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
    return warped, matrix


def apply_gaussian_noise(image: np.ndarray, sigma=15) -> np.ndarray:
    noise = np.random.normal(0, sigma, image.shape).astype(np.float32)
    noisy = np.clip(image.astype(np.float32) + noise, 0, 255).astype(np.uint8)
    return noisy


def apply_salt_pepper_noise(image: np.ndarray, amount=0.007) -> np.ndarray:
    noisy = image.copy()
    h, w = noisy.shape[:2]
    num_pixels = int(h * w * amount)
    for _ in range(num_pixels):
        y = random.randrange(h)
        x = random.randrange(w)
        noisy[y, x] = [255, 255, 255] if random.random() < 0.5 else [0, 0, 0]
    return noisy


def adjust_color_jitter(image: np.ndarray) -> np.ndarray:
    pil = Image.fromarray(image)
    for enhancer_class, strength in [
        (ImageEnhance.Color, 0.7),
        (ImageEnhance.Brightness, 0.8),
        (ImageEnhance.Contrast, 0.8),
        (ImageEnhance.Sharpness, 0.7),
    ]:
        if random.random() < 0.9:
            factor = random.uniform(1.0 - strength, 1.0 + strength)
            pil = enhancer_class(pil).enhance(factor)
    return np.array(pil)


def shift_rgb_channels(image: np.ndarray, max_shift=30) -> np.ndarray:
    rgb = image.copy().astype(np.int16)
    for channel in range(3):
        shift = random.randint(-max_shift, max_shift)
        rgb[..., channel] = np.clip(rgb[..., channel] + shift, 0, 255)
    return rgb.astype(np.uint8)


def apply_random_blur(image: np.ndarray) -> np.ndarray:
    if random.random() < 0.5:
        ksize = random.choice([3, 5])
        return cv2.GaussianBlur(image, (ksize, ksize), 0)
    return image


def apply_random_shadow(image: np.ndarray) -> np.ndarray:
    overlay = image.copy().astype(np.float32)
    h, w = image.shape[:2]
    x1, y1 = random.randint(0, w), 0
    x2, y2 = random.randint(0, w), h
    poly = np.array([[x1, y1], [x2, y2], [w, h], [0, h]], np.int32)
    mask = np.zeros((h, w), dtype=np.uint8)
    cv2.fillPoly(mask, [poly], 255)
    shadow_intensity = random.uniform(0.4, 0.75)
    overlay[mask == 255] *= shadow_intensity
    return np.clip(overlay, 0, 255).astype(np.uint8)


def augment_image(image: np.ndarray, annotation_data, operations):
    augmented = image.copy()
    transformed_annotations = deepcopy(annotation_data)

    for operation in operations:
        if operation == "rotate":
            angle = random.uniform(-15.0, 15.0)
            augmented, matrix = rotate_image(augmented, angle)
            if transformed_annotations is not None:
                transformed_annotations = update_annotation_boxes(
                    transformed_annotations,
                    lambda box: clamp_box(transform_box(box, matrix), augmented.shape[1], augmented.shape[0]),
                )

        elif operation == "flip":
            mode = random.choice(["horizontal", "vertical"])
            augmented, matrix = flip_image(augmented, mode)
            if transformed_annotations is not None:
                transformed_annotations = update_annotation_boxes(
                    transformed_annotations,
                    lambda box: clamp_box(transform_box(box, matrix), augmented.shape[1], augmented.shape[0]),
                )

        elif operation == "perspective":
            augmented, matrix = perspective_transform(augmented, max_warp=0.04)
            if transformed_annotations is not None:
                transformed_annotations = update_annotation_boxes(
                    transformed_annotations,
                    lambda box: clamp_box(transform_box(box, matrix), augmented.shape[1], augmented.shape[0]),
                )

        elif operation == "noise":
            if random.random() < 0.6:
                augmented = apply_gaussian_noise(augmented, sigma=random.randint(8, 24))
            else:
                augmented = apply_salt_pepper_noise(augmented, amount=random.uniform(0.003, 0.01))

        elif operation == "color":
            augmented = adjust_color_jitter(augmented)

        elif operation == "rgb_shift":
            augmented = shift_rgb_channels(augmented, max_shift=20)

        elif operation == "blur":
            augmented = apply_random_blur(augmented)

        elif operation == "shadow":
            augmented = apply_random_shadow(augmented)

    return augmented, transformed_annotations


def get_image_paths(input_dir: Path, max_images=None):
    all_images = [p for p in sorted(input_dir.iterdir()) if p.suffix.lower() in SUPPORTED_EXTENSIONS]
    if max_images is not None:
        all_images = all_images[:max_images]
    return all_images


def build_preview(image: np.ndarray, annotation_data, preview_path: Path) -> None:
    if annotation_data is None:
        save_image(preview_path, image)
        return

    pil_image = Image.fromarray(image)
    overlay = Image.new("RGBA", pil_image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    colors = {
        "title_block": (255, 0, 0, 80),
        "notes": (0, 128, 255, 80),
        "gdt_feature": (0, 255, 128, 80),
    }

    comps = annotation_data.get("components", {})
    if "title_block" in comps:
        draw.rectangle(comps["title_block"], outline=(255, 0, 0), width=4)
        draw.rectangle(comps["title_block"], fill=colors["title_block"])
    if "notes" in comps:
        draw.rectangle(comps["notes"], outline=(0, 128, 255), width=4)
        draw.rectangle(comps["notes"], fill=colors["notes"])
    if "gdt_features" in comps:
        for feature in comps["gdt_features"]:
            bbox = feature.get("bbox_pixels")
            if bbox is None:
                continue
            draw.rectangle(bbox, outline=(0, 255, 128), width=3)
            draw.rectangle(bbox, fill=colors["gdt_feature"])

    result = Image.alpha_composite(pil_image.convert("RGBA"), overlay)
    result = result.convert("RGB")
    result.save(preview_path)


def choose_augmentations():
    operations = ["rotate", "flip", "perspective", "noise", "color", "rgb_shift", "blur", "shadow"]
    selected = random.sample(operations, k=random.randint(2, 5))
    if "rotate" in selected and random.random() < 0.3:
        selected.append("noise")
    return selected


def generate_augmented_dataset(
    input_dir: Path,
    output_dir: Path,
    preview_dir: Path,
    num_copies: int,
    max_images: int | None,
    seed: int | None,
    keep_annotations: bool,
    overwrite: bool,
):
    random.seed(seed)
    np.random.seed(seed if seed is not None else 0)

    output_dir.mkdir(parents=True, exist_ok=True)
    preview_dir.mkdir(parents=True, exist_ok=True)

    images = get_image_paths(input_dir, max_images=max_images)
    if not images:
        raise FileNotFoundError(f"No images found in '{input_dir}'")

    print(f"Found {len(images)} source images. Generating {num_copies} augmentations each.")
    total = 0

    for src_image_path in images:
        annotation_data = None
        if keep_annotations:
            json_path = src_image_path.with_suffix(".json")
            annotation_data = load_annotations(json_path)

        original = load_image(src_image_path)

        for index in range(num_copies):
            operations = choose_augmentations()
            augmented, transformed_annotations = augment_image(original, annotation_data, operations)

            base_name = src_image_path.stem
            aug_name = f"{base_name}_aug{index:02d}"
            aug_image_path = output_dir / f"{aug_name}.png"
            aug_json_path = output_dir / f"{aug_name}.json"
            preview_path = preview_dir / f"{aug_name}_preview.png"

            if aug_image_path.exists() and not overwrite:
                print(f"Skipping existing: {aug_image_path}")
                continue

            save_image(aug_image_path, augmented)

            if keep_annotations and transformed_annotations is not None:
                transformed_annotations["filename"] = aug_image_path.name
                save_annotations(aug_json_path, transformed_annotations)

            build_preview(augmented,
                          transformed_annotations if keep_annotations else None,
                          preview_path)
            total += 1

    print(f"Completed augmentation: {total} images written to {output_dir}")
    print(f"Preview overlays written to {preview_dir}")


def parse_args():
    parser = argparse.ArgumentParser(description="Augment ISO technical sheet images and save annotated previews.")
    parser.add_argument("--input-dir", type=Path, default=Path("iso_technical_sheets"), help="Folder with source ISO sheet images.")
    parser.add_argument("--output-dir", type=Path, default=Path("iso_technical_sheets_augmented"), help="Folder where augmented images will be saved.")
    parser.add_argument("--preview-dir", type=Path, default=Path("iso_technical_sheets_augmented_previews"), help="Folder where overlay preview images will be saved.")
    parser.add_argument("--copies", type=int, default=2, help="Number of augmented copies to generate per source image.")
    parser.add_argument("--max-images", type=int, default=None, help="Limit the number of input images to process.")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducible augmentation.")
    parser.add_argument("--no-annotations", action="store_true", help="Do not preserve or transform JSON annotations.")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing augmented files if they exist.")
    return parser.parse_args()


def main():
    args = parse_args()
    generate_augmented_dataset(
        input_dir=args.input_dir,
        output_dir=args.output_dir,
        preview_dir=args.preview_dir,
        num_copies=args.copies,
        max_images=args.max_images,
        seed=args.seed,
        keep_annotations=not args.no_annotations,
        overwrite=args.overwrite,
    )


if __name__ == "__main__":
    main()
