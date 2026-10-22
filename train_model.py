
from ultralytics import YOLO

# Memuat model YOLOv8 untuk klasifikasi gambar
model = YOLO("yolov8n-cls.pt")

# Melatih model dengan dataset SmartWaste
results = model.train(
    data="dataset_split",
    epochs=30,
    imgsz=224,
    batch=16,
    project="runs/smartwaste",
    name="klasifikasi_sampah",
)

print("Pelatihan model SmartWaste selesai!")
