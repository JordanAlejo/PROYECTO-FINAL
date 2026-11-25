"""Reentrena desde el modelo de 9 clases usando el dataset balanceado.

Las clases minoritarias (100 antigua, 50 antigua) tienen mas peso en train.
"""

from pathlib import Path

from ultralytics import YOLO

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "dataset_balanceado" / "data.yaml"
BASE = ROOT / "runs" / "monedas_9clases" / "weights" / "best.pt"

print("BASE:", BASE)
print("DATA:", DATA)

model = YOLO(str(BASE))

results = model.train(
    data=str(DATA),
    epochs=30,
    imgsz=416,
    batch=8,
    device="cpu",
    optimizer="AdamW",
    lr0=0.001,
    weight_decay=0.0005,
    project=str(ROOT / "runs"),
    name="monedas_balanceado_v2",
    exist_ok=True,
    patience=10,
    workers=2,
)

print("Reentrenamiento finalizado.")
print(results)
