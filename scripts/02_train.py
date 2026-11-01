from ultralytics import YOLO
import os

ROOT = r"D:\Documents\Proyecto predeterminado\yolo_monedas_colombia"
DATA = os.path.join(ROOT, "data.yaml")
MODEL = "yolov8n.pt"

model = YOLO(MODEL)
results = model.train(
    data=DATA,
    epochs=15,
    imgsz=320,
    batch=8,
    device="cpu",
    project=os.path.join(ROOT, "runs"),
    name="monedas_v1",
    patience=5,
    workers=2,
)
print("Training finished")
print(results)
