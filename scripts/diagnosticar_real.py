"""Detalle de predicciones del modelo nuevo sobre capturas reales."""

import os
import glob
from collections import Counter

from ultralytics import YOLO

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REAL = os.path.join(ROOT, "dataset_reposicion", "images")
TEST = os.path.join(ROOT, "dataset_final", "images", "test")
NEW = os.path.join(ROOT, "runs", "monedas_final", "weights", "best.pt")

IDS = {
    "1000_pesos": 0, "100_pesos": 1, "100_pesos_nueva": 2,
    "200_pesos": 3, "200_pesos_nueva": 4,
    "500_pesos": 5, "500_pesos_nueva": 6,
    "50_pesos": 7, "50_pesos_nueva": 8,
}
PREFIJOS = ["1000_pesos", "100_pesos_nueva", "100_pesos", "200_pesos_nueva",
            "500_pesos_nueva", "50_pesos_nueva", "50_pesos"]


def clase_de(nombre):
    return next((IDS[p] for p in PREFIJOS if nombre.startswith(p + "_")), None)


def evaluar(model, archivos, titulo):
    aciertos = 0
    confus = Counter()
    print(f"\n=== {titulo} ({len(archivos)} imagenes) ===")
    for ruta, gt in archivos:
        res = model.predict(ruta, conf=0.15, imgsz=416, verbose=False)[0]
        if len(res.boxes) == 0:
            print(f"  {os.path.basename(ruta)[:38]:38} GT={model.names[gt]:16} -> SIN DETECCION")
            continue
        b = max(res.boxes, key=lambda x: float(x.conf[0]))
        pred = int(b.cls[0])
        conf = float(b.conf[0])
        if pred == gt:
            aciertos += 1
        confus[(model.names[gt], model.names[pred])] += 1
        marca = "OK " if pred == gt else "MAL"
        print(f"  {marca} {os.path.basename(ruta)[:34]:34} GT={model.names[gt]:16} -> {model.names[pred]:16} conf={conf:.2f}")
    print(f"Resultado: {aciertos}/{len(archivos)} ({aciertos/len(archivos):.0%})")


def main():
    model = YOLO(NEW)
    print("Clases:", model.names)

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

    evaluar(model, test, "TEST apartado")
    evaluar(model, todas, "TODAS las capturas reales")


if __name__ == "__main__":
    main()
