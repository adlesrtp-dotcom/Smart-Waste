
import random
import shutil
from pathlib import Path

# Lokasi dataset asli
SOURCE_DIR = Path("dataset")

# Lokasi hasil pembagian dataset
OUTPUT_DIR = Path("dataset_split")

# Pembagian data
TRAIN_RATIO = 0.70
VAL_RATIO = 0.20
TEST_RATIO = 0.10

random.seed(42)

categories = [
    "cardboard",
    "glass",
    "metal",
    "paper",
    "plastic",
]

for category in categories:
    source_folder = SOURCE_DIR / category

    if not source_folder.exists():
        raise FileNotFoundError(
            f"Folder kategori tidak ditemukan: {source_folder}"
        )

    images = [
        file for file in source_folder.iterdir()
        if file.suffix.lower() in {
            ".jpg", ".jpeg", ".png", ".webp"
        }
    ]

    random.shuffle(images)

    total = len(images)
    train_end = int(total * TRAIN_RATIO)
    val_end = train_end + int(total * VAL_RATIO)

    splits = {
        "train": images[:train_end],
        "val": images[train_end:val_end],
        "test": images[val_end:],
    }

    for split_name, split_images in splits.items():
        destination = OUTPUT_DIR / split_name / category
        destination.mkdir(parents=True, exist_ok=True)

        for image in split_images:
            shutil.copy2(image, destination / image.name)

    print(
        f"{category}: {len(splits['train'])} training, "
        f"{len(splits['val'])} validation, "
        f"{len(splits['test'])} testing"
    )

print("\nPembagian dataset selesai!")
print(f"Hasil tersimpan di: {OUTPUT_DIR.resolve()}")
