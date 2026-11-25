"""Entrena YOLO con el dataset ORIGINAL de Roboflow (9 clases).

Rutas calculadas automaticamente a partir de la ubicacion del script,
para que el proyecto siga funcionando aunque se mueva de carpeta.
"""

from pathlib import Path

from ultralytics import YOLO

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "dataset_9clases" / "data.yaml"

# Usa los pesos base locales si estan descargados; si no, Ultralytics los baja.
LOCAL_WEIGHTS = ROOT / "yolov8n.pt"
MODEL = str(LOCAL_WEIGHTS) if LOCAL_WEIGHTS.exists() else "yolov8n.pt"

if not DATA.exists():
    raise FileNotFoundError(f"No se encontro el archivo de datos: {DATA}")

print("ROOT:", ROOT)
print("DATA:", DATA)
print("MODELO BASE:", MODEL)

model = YOLO(MODEL)

results = model.train(
    data=str(DATA),
    epochs=60,
    imgsz=320,
    batch=8,
    device="cpu",
    project=str(ROOT / "runs"),
    name="monedas_9clases",
    exist_ok=True,
    patience=15,
    workers=2,
)

print("Entrenamiento finalizado.")
print(results)
