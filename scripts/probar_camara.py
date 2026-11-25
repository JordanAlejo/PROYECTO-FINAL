"""Prueba rapida de camaras disponibles (USB o IP del celular).

Uso:
    python scripts/probar_camara.py                    # prueba indices 0 a 4
    python scripts/probar_camara.py http://IP:8080/video
    python scripts/probar_camara.py 1
"""

import os
import sys
import cv2

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "runs", "demo")
os.makedirs(OUT_DIR, exist_ok=True)


def probar(source, nombre):
    cap = cv2.VideoCapture(source)
    try:
        cap.set(cv2.CAP_PROP_OPEN_TIMEOUT_MSEC, 5000)
    except Exception:
        pass

    if not cap.isOpened():
        print(f"[X] {nombre}: no se pudo abrir")
        cap.release()
        return False

    ok, frame = cap.read()
    if not ok or frame is None:
        print(f"[X] {nombre}: se abrio pero no entrega imagen")
        cap.release()
        return False

    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    out = os.path.join(OUT_DIR, f"camara_{nombre}.jpg")
    cv2.imwrite(out, frame)
    print(f"[OK] {nombre}: {w}x{h} -> guardada en {out}")
    cap.release()
    return True


if __name__ == "__main__":
    if len(sys.argv) > 1:
        value = sys.argv[1]
        source = int(value) if value.isdigit() else value
        probar(source, str(source).replace(":", "_").replace("/", "_"))
    else:
        encontradas = 0
        for i in range(5):
            if probar(i, str(i)):
                encontradas += 1
        print(f"\nCamaras USB encontradas: {encontradas}")
