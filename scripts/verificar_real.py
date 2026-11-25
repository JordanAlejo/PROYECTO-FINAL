"""Compara el modelo anterior vs el ajustado sobre capturas reales apartadas.

Las imagenes reales se reconocen porque su nombre empieza con el nombre
de la clase (ej. 50_pesos_nueva_1794....jpg).
"""

import os
import glob
from collections import Counter

from ultralytics import YOLO

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEST_DIR = os.path.join(ROOT, "dataset_final", "images", "test")
OLD = os.path.join(ROOT, "runs", "monedas_9clases", "weights", "best.pt")
NEW = os.path.join(ROOT, "runs", "monedas_final", "weights", "best.pt")

# Ordenados para que "nueva" se compruebe antes que su denominacion base.
NOMBRES = [
    "1000_pesos", "100_pesos_nueva", "100_pesos",
    "200_pesos_nueva", "500_pesos_nueva", "50_pesos_nueva", "50_pesos",
]

IDS = {
    "1000_pesos": 0, "100_pesos": 1, "100_pesos_nueva": 2,
    "200_pesos": 3, "200_pesos_nueva": 4,
    "500_pesos": 5, "500_pesos_nueva": 6,
    "50_pesos": 7, "50_pesos_nueva": 8,
}


def main():
    archivos = []
    for f in sorted(glob.glob(os.path.join(TEST_DIR, "*.jpg"))):
        base = os.path.basename(f)
        clase = next((n for n in NOMBRES if base.startswith(n + "_")), None)
        if clase:
            archivos.append((f, IDS[clase]))

    print(f"Imagenes reales de prueba: {len(archivos)}")
    if not archivos:
        return

    modelos = {
        "ANTERIOR": YOLO(OLD) if os.path.exists(OLD) else None,
        "NUEVO": YOLO(NEW) if os.path.exists(NEW) else None,
    }

    for nombre, model in modelos.items():
        if model is None:
            print(f"{nombre}: no existe el modelo")
            continue
        aciertos = 0
        sin_deteccion = 0
        detalle = Counter()
        for ruta, gt in archivos:
            res = model.predict(ruta, conf=0.25, imgsz=416, verbose=False)[0]
            if len(res.boxes) == 0:
                sin_deteccion += 1
                continue
            pred = int(res.boxes[0].cls[0])
            if pred == gt:
                aciertos += 1
            detalle[model.names[gt]] += (1 if pred == gt else 0)
        total = len(archivos)
        print(f"\n{nombre}: {aciertos}/{total} correctas ({aciertos/total:.0%})")
        print(f"  sin deteccion: {sin_deteccion}")
        for nombre_clase, n_ok in detalle.items():
            n_tot = sum(1 for _, gt in archivos if model.names[gt] == nombre_clase)
            print(f"    {nombre_clase}: {n_ok}/{n_tot}")


if __name__ == "__main__":
    main()
