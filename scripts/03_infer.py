import sys, os, glob
from ultralytics import YOLO

ROOT = r"D:\Documents\Proyecto predeterminado\yolo_monedas_colombia"
# pick the most recent best.pt under runs/
candidates = glob.glob(os.path.join(ROOT, "runs", "*", "weights", "best.pt"))
if not candidates:
    candidates = glob.glob(os.path.join(ROOT, "runs", "*", "weights", "last.pt"))
WEIGHTS = max(candidates, key=os.path.getmtime) if candidates else None

def main():
    if WEIGHTS is None or not os.path.exists(WEIGHTS):
        print("No se encontraron pesos entrenados en runs/*/weights/best.pt")
        return
    if len(sys.argv) < 2:
        print("Uso: python 03_infer.py <imagen_o_carpeta>")
        return
    src = sys.argv[1]
    model = YOLO(WEIGHTS)
    results = model.predict(source=src, conf=0.25, imgsz=320, save=True,
                            project=os.path.join(ROOT,"runs","infer"), name="pred")
    for r in results:
        print(r.path)
        for b in r.boxes:
            cls = int(b.cls[0]); conf = float(b.conf[0])
            print(f"  {model.names[cls]}  conf={conf:.2f}  box={b.xyxy[0].tolist()}")

if __name__ == "__main__":
    main()
