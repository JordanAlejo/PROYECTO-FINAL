import os, sys, glob
import cv2
from ultralytics import YOLO

ROOT = r"C:\Users\Cocot\Desktop\yolo_monedas_colombia - copia"
candidates = glob.glob(os.path.join(ROOT, "runs", "*", "weights", "best.pt")) or glob.glob(os.path.join(ROOT, "runs", "*", "weights", "last.pt"))
if not candidates:
    print("No hay pesos entrenados.")
    sys.exit(1)
WEIGHTS = max(candidates, key=os.path.getmtime)
model = YOLO(WEIGHTS)

def show_image(path):
    img = cv2.imread(path)
    if img is None:
        print("No se pudo leer", path); return
    res = model.predict(img, conf=0.25, imgsz=320, verbose=False)[0]
    annotated = res.plot()
    out_dir = os.path.join(ROOT, "runs", "demo")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "resultado.jpg")
    cv2.imwrite(out_path, annotated)
    print("Guardado:", out_path)
    os.startfile(out_path)
    return out_path

def webcam():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("No se pudo abrir la webcam."); return
    print("Presiona 'q' para salir.")
    while True:
        ok, frame = cap.read()
        if not ok: break
        res = model.predict(frame, conf=0.25, imgsz=320, verbose=False)[0]
        cv2.imshow("Webcam - monedas (q para salir)", res.plot())
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1].lower() == "webcam":
        webcam()
    else:
        # si no pasan imagen, usa la primera de val
        if len(sys.argv) > 1:
            src = sys.argv[1]
        else:
            vals = glob.glob(os.path.join(ROOT, "data", "images", "val", "*.jpg"))
            src = vals[0] if vals else None
        if src is None:
            print("Pasa una imagen o usa 'webcam'.")
        else:
            show_image(src)
