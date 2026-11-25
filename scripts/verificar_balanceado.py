"""Compara el modelo equilibrado contra el anterior en capturas reales."""

import os
import glob
from collections import Counter

from ultralytics import YOLO

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEST = os.path.join(ROOT, "dataset_final", "images", "test")
REAL = os.path.join(ROOT, "dataset_reposicion", "images")
ANTERIOR = os.path.join(ROOT, "runs", "monedas_final", "weights", "best.pt")
NUEVO = os.path.join(ROOT, "runs", "monedas_balanceado", "weights", "best.pt")

IDS = {
    "1000_pesos": 0, "100_pesos": 1, "100_pesos_nueva": 2,
    "200_pesos": 3, "200_pesos_nueva": 4,
    "500_pesos": 5, "500_pesos_nueva": 6,
    "50_pesos": 7, "50_pesos_nueva": 8,
}
PREF = ["1000_pesos", "100_pesos_nueva", "100_pesos", "200_pesos_nueva",
        "500_pesos_nueva", "50_pesos_nueva", "50_pesos"]


def clase_de(nombre):
    return next((IDS[p] for p in PREF if nombre.startswith(p + "_")), None)


def evaluar(model, archivos, titulo):
    aciertos = 0
    por_clase = Counter()
    total_clase = Counter()
    confus = Counter()
    for ruta, gt in archivos:
        res = model.predict(ruta, conf=0.15, imgsz=640, verbose=False)[0]
        if len(res.boxes) == 0:
            pred = -1
        else:
            pred = int(max(res.boxes, key=lambda b: float(b.conf[0])).cls[0])
        total_clase[gt] += 1
        if pred == gt:
            aciertos += 1
            por_clase[gt] += 1
        confus[(model.names[gt], model.names[pred] if pred >= 0 else "NA")] += 1
    print(f"\n{titulo}: {aciertos}/{len(archivos)} ({aciertos/len(archivos):.0%})")
    for cid in sorted(total_clase):
        print(f"  {model.names[cid]:18} {por_clase[cid]}/{total_clase[cid]}")
    print("  confusiones:", dict(confus))


def main():
    test = []
    for f in sorted(glob.glob(os.path.join(TEST, "*.jpg"))):
        gt = clase_de(os.path.basename(f))
        if gt is not None:
            test.append((f, gt))

    todas = []
    for carpeta in sorted(os.listdir(REAL)):
        for f in sorted(glob.glob(os.path.join(REAL, carpeta, "*.jpg"))):
            gt = IDS.get(carpeta)
            if gt is not None:
                todas.append((f, gt))

    anterior = YOLO(ANTERIOR)
    evaluar(anterior, test, "ANTERIOR - test apartado")
    evaluar(anterior, todas, "ANTERIOR - todas las reales")

    nuevo = YOLO(NUEVO) if os.path.exists(NUEVO) else None
    if nuevo:
        evaluar(nuevo, test, "NUEVO - test apartado")
        evaluar(nuevo, todas, "NUEVO - todas las reales")
    else:
        print("No existe el modelo nuevo todavia.")


if __name__ == "__main__":
    main()
