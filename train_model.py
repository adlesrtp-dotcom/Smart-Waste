from ultralytics import YOLO

if __name__ == '__main__':
    # 1. Load Pretrained Classification Model
    model = YOLO('yolov8n-cls.pt')

    # 2. Jalankan Training dengan Data Augmentation
    model.train(
        data='dataset',       # Folder dataset kamu
        epochs=50,            # Jumlah iterasi training
        imgsz=224,            # Ukuran gambar masukan
        batch=8,
        workers=2,
        patience=15,          # Early stopping jika loss stabil
        
        # Hyperparameter Augmentasi Gambar (Mencegah Overfitting & Salah Klasifikasi)
        degrees=15.0,         # Rotasi acak hingga 15 derajat
        fliplr=0.5,           # Flip horizontal acak (50% peluang)
        erasing=0.4,          # Menutup sebagian objek secara acak
        hsv_s=0.7,            # Variasi saturasi warna
        hsv_v=0.4             # Variasi kecerahan warna
    )