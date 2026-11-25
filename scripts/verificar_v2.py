"""Compara el modelo equilibrado v1 contra el v2 sobre todas las capturas reales."""

import os
import glob
from collections import Counter

from ultralytics import YOLO

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REAL = os.path.join(ROOT, "dataset_reposicion", "images")
V1 = os.path.join(ROOT, "runs", "monedas_balanceado", "weights", "best.pt")
V2 = os.path.join(ROOT, "runs", "monedas_balanceado_v2", "weights", "best.pt")

IDS = {
    "1000_pesos": 0, "100_pesos": 1, "100_pesos_nueva": 2,
    "200_pesos": 3, "200_pesos_nueva": 4,
    "500_pesos": 5, "500_pesos_nueva": 6,
    "50_pesos": 7, "50_pesos_nueva": 8,
}


def evaluar(model, archivos, titulo):
    ok = Counter()
    tot = Counter()
    confus = Counter()
    for ruta, gt in archivos:
        res = model.predict(ruta, conf=0.15, imgsz=416, verbose=False)[0]
        pred = int(max(res.boxes, key=lambda b: float(b.conf[0])).cls[0]) if len(res.boxes) else -1
        tot[gt] += 1
        if pred == gt:
            ok[gt] += 1
        confus[(model.names[gt], model.names[pred] if pred >= 0 else "NA")] += 1

    print(f"\n=== {titulo}: {sum(ok.values())}/{len(archivos)} ({sum(ok.values())/len(archivos):.0%}) ===")
    for cid in sorted(tot):
        print(f"  {model.names[cid]:18} {ok[cid]:2}/{tot[cid]:2}")
    malas = {k: v for k, v in confus.items() if k[0] != k[1]}
    print("  confusiones:", malas if malas else "ninguna")


def main():
    archivos = []
    for carpeta, cid in IDS.items():
        for f in sorted(glob.glob(os.path.join(REAL, carpeta, "*.jpg"))):
            archivos.append((f, cid))
    print("Capturas reales:", len(archivos))

    if os.path.exists(V1):
        evaluar(YOLO(V1), archivos, "V1 (modelo anterior)")
    else:
        print("No existe V1")
    if os.path.exists(V2):
        evaluar(YOLO(V2), archivos, "V2 (modelo nuevo)")
    else:
        print("No existe V2")


if __name__ == "__main__":
    main()
