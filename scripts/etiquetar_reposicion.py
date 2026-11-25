"""Etiqueta automaticamente las capturas del montaje real.

Para cada imagen en dataset_reposicion/images/<clase>/ detecta la moneda
(Hough circles) y escribe su caja en formato YOLO en
dataset_reposicion/labels/<clase>/.
"""

import os
import glob
import cv2
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG_DIR = os.path.join(ROOT, "dataset_reposicion", "images")
LBL_DIR = os.path.join(ROOT, "dataset_reposicion", "labels")
DEBUG_DIR = os.path.join(ROOT, "runs", "etiquetado")

CLASES = {
    "1000_pesos": 0,
    "100_pesos": 1,
    "100_pesos_nueva": 2,
    "200_pesos": 3,
    "200_pesos_nueva": 4,
    "500_pesos": 5,
    "500_pesos_nueva": 6,
    "50_pesos": 7,
    "50_pesos_nueva": 8,
}

os.makedirs(DEBUG_DIR, exist_ok=True)


def detectar_moneda(img):
    """Devuelve (cx, cy, r) de la moneda o None."""
    gray = cv2.GaussianBlur(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), (9, 9), 2)
    circles = cv2.HoughCircles(
        gray, cv2.HOUGH_GRADIENT, dp=1.2, minDist=80,
        param1=100, param2=28, minRadius=45, maxRadius=115
    )
    if circles is None:
        return None
    candidatos = [
        c for c in np.round(circles[0]).astype(int)
        if 100 < c[0] < 420 and 190 < c[1] < 420
    ]
    if not candidatos:
        return None
    return max(candidatos, key=lambda c: c[2])


def main():
    total = 0
    fallos = []

    for nombre_clase, class_id in CLASES.items():
        patron = os.path.join(IMG_DIR, nombre_clase, "*.jpg")
        archivos = sorted(glob.glob(patron))
        if not archivos:
            continue

        out_clase = os.path.join(LBL_DIR, nombre_clase)
        os.makedirs(out_clase, exist_ok=True)

        for i, ruta in enumerate(archivos):
            img = cv2.imread(ruta)
            if img is None:
                fallos.append(ruta)
                continue

            h, w = img.shape[:2]
            moneda = detectar_moneda(img)
            if moneda is None:
                fallos.append(ruta)
                continue

            cx, cy, r = moneda
            r = int(r * 1.05)
            x1 = max(0, cx - r)
            y1 = max(0, cy - r)
            x2 = min(w, cx + r)
            y2 = min(h, cy + r)

            xc = (x1 + x2) / 2.0 / w
            yc = (y1 + y2) / 2.0 / h
            bw = (x2 - x1) / w
            bh = (y2 - y1) / h

            etiqueta = os.path.join(out_clase, os.path.basename(ruta).replace(".jpg", ".txt"))
            with open(etiqueta, "w", encoding="utf-8") as f:
                f.write(f"{class_id} {xc:.6f} {yc:.6f} {bw:.6f} {bh:.6f}\n")

            if i < 2:
                debug = img.copy()
                cv2.rectangle(debug, (x1, y1), (x2, y2), (0, 0, 255), 2)
                cv2.imwrite(
                    os.path.join(DEBUG_DIR, f"{nombre_clase}_{i}.jpg"), debug
                )

            total += 1

    print(f"Etiquetas escritas: {total}")
    print(f"Fallos: {len(fallos)}")
    for f in fallos[:10]:
        print("  ", f)


if __name__ == "__main__":
    main()
