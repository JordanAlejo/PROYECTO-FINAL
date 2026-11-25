"""Ajusta finamente el modelo con las capturas del montaje real.

Parte del modelo de 9 clases ya entrenado y usa dataset_final
(Roboflow + capturas reales), con learning rate bajo.
"""

from pathlib import Path

from ultralytics import YOLO

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "dataset_final" / "data.yaml"
BASE = ROOT / "runs" / "monedas_9clases" / "weights" / "best.pt"

if not DATA.exists():
    raise FileNotFoundError(f"No existe {DATA}")
if not BASE.exists():
    raise FileNotFoundError(f"No existe el modelo base {BASE}")

print("BASE:", BASE)
print("DATA:", DATA)

model = YOLO(str(BASE))

results = model.train(
    data=str(DATA),
    epochs=40,
    imgsz=416,
    batch=8,
    device="cpu",
    optimizer="AdamW",
    lr0=0.0005,
    weight_decay=0.0005,
    project=str(ROOT / "runs"),
    name="monedas_final",
    exist_ok=True,
    patience=12,
    workers=2,
)

print("Ajuste finalizado.")
print(results)
