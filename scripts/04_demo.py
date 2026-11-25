"""Demo de deteccion de monedas con webcam, camara IP del celular o imagen.

Uso:
    python scripts/04_demo.py webcam                       # camara USB (indice 0)
    python scripts/04_demo.py webcam 1                      # otra camara USB
    python scripts/04_demo.py webcam http://IP:8080/video   # camara del celular (IP Webcam)
    python scripts/04_demo.py "ruta/imagen.jpg"             # una imagen
"""

import os, sys, glob
import cv2
from ultralytics import YOLO

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PREFERRED = os.path.join(ROOT, "runs", "monedas_balanceado_v2", "weights", "best.pt")
candidates = glob.glob(os.path.join(ROOT, "runs", "*", "weights", "best.pt")) or glob.glob(os.path.join(ROOT, "runs", "*", "weights", "last.pt"))
if not candidates and not os.path.exists(PREFERRED):
    print("No hay pesos entrenados.")
    sys.exit(1)
WEIGHTS = PREFERRED if os.path.exists(PREFERRED) else max(candidates, key=os.path.getmtime)
model = YOLO(WEIGHTS)

# El modelo final fue entrenado a 416: es el tamano que da mejor precision.
# Si va lento, bajalo a 320; si quieres mas detalle, proba 640.
IMGSZ = 416
CONF = 0.25
# En la camara solo se lee una moneda a la vez: conservar solo la mejor caja.
MAX_DET_WEBCAM = 1


def show_image(path, imgsz=IMGSZ):
    img = cv2.imread(path)
    if img is None:
        print("No se pudo leer", path); return
    res = model.predict(img, conf=CONF, imgsz=imgsz, verbose=False)[0]
    annotated = res.plot()
    out_dir = os.path.join(ROOT, "runs", "demo")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "resultado.jpg")
    cv2.imwrite(out_path, annotated)
    print("Guardado:", out_path)
    os.startfile(out_path)
    return out_path


def webcam(source=0, imgsz=IMGSZ):
    cap = cv2.VideoCapture(source)
    if not cap.isOpened():
        print("No se pudo abrir la camara:", source)
        print("Prueba: python scripts/probar_camara.py")
        return

    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(f"Camara abierta: {source}  ({w}x{h})  imgsz={imgsz}")
    print("Presiona 'q' para salir.")

    while True:
        ok, frame = cap.read()
        if not ok:
            print("Se perdio la conexion con la camara.")
            break

        res = model.predict(
            frame, conf=CONF, imgsz=imgsz, max_det=MAX_DET_WEBCAM, verbose=False
        )[0]
        cv2.imshow("Monedas - camara (q para salir)", res.plot())

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    args = sys.argv[1:]

    if args and args[0].lower() == "webcam":
        # Fuente opcional: indice (0, 1, 2...) o URL (http://IP:8080/video)
        # Tercer argumento opcional: tamano de inferencia (640, 416, 320...)
        source = 0
        if len(args) > 1:
            value = args[1]
            source = int(value) if value.isdigit() else value
        size = int(args[2]) if len(args) > 2 and args[2].isdigit() else IMGSZ
        webcam(source, size)
    else:
        if args:
            src = args[0]
        else:
            vals = glob.glob(os.path.join(ROOT, "dataset_9clases", "images", "val", "*.jpg"))
            src = vals[0] if vals else None
        if src is None:
            print("Pasa una imagen o usa 'webcam'.")
        else:
            size = int(args[1]) if len(args) > 1 and args[1].isdigit() else IMGSZ
            show_image(src, size)
