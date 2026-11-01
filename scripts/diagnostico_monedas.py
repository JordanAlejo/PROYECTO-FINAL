
import os
import sys
import glob
import time
import cv2
from ultralytics import YOLO

# ==========================================
# CONFIGURACION
# ==========================================

ROOT = r"C:\Users\Cocot\Desktop\yolo_monedas_colombia - copia"

# Buscar el modelo entrenado más reciente
candidates = glob.glob(
    os.path.join(ROOT, "runs", "*", "weights", "best.pt")
)

if not candidates:
    candidates = glob.glob(
        os.path.join(ROOT, "runs", "*", "weights", "last.pt")
    )

if not candidates:
    print("ERROR: No se encontraron pesos en la carpeta runs.")
    print("Busca tu archivo best.pt y revisa la ruta ROOT.")
    sys.exit(1)

WEIGHTS = max(candidates, key=os.path.getmtime)

print("=" * 45)
print("DIAGNOSTICO YOLO - MONEDAS COLOMBIANAS")
print("=" * 45)
print("Modelo:", WEIGHTS)

# Cargar modelo
model = YOLO(WEIGHTS)

print("\nClases aprendidas por YOLO:")
for class_id, class_name in model.names.items():
    print(f"ID {class_id}: {class_name}")

# Carpeta para recopilar nuevas imagenes
SAVE_DIR = os.path.join(ROOT, "dataset_nuevo", "images", "sin_etiquetar")
os.makedirs(SAVE_DIR, exist_ok=True)

print("\nImagenes nuevas se guardaran en:")
print(SAVE_DIR)

# ==========================================
# WEBCAM
# ==========================================

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("ERROR: No se pudo abrir la webcam.")
    sys.exit(1)

# Solicitar una resolucion de webcam habitual
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

print("\nControles:")
print("S = guardar una foto para mejorar el dataset")
print("Q = salir")

frame_count = 0
start_time = time.time()

while True:
    ok, frame = cap.read()

    if not ok:
        print("No se pudo leer el frame.")
        break

    # Inferencia: umbral bajo para diagnosticar
    result = model.predict(
        source=frame,
        conf=0.10,
        imgsz=640,
        verbose=False
    )[0]

    # Dibujar detecciones
    annotated = result.plot()

    # Mostrar confianza y clase de cada deteccion
    detections = []

    for box in result.boxes:
        class_id = int(box.cls[0].item())
        confidence = float(box.conf[0].item())
        class_name = model.names[class_id]

        detections.append(
            f"{class_name}: {confidence:.1%}"
        )

    if detections:
        print(" | ".join(detections))

    # FPS aproximados del procesamiento
    frame_count += 1
    elapsed = time.time() - start_time
    fps = frame_count / elapsed if elapsed > 0 else 0

    cv2.putText(
        annotated,
        f"FPS: {fps:.1f} | Conf: 0.10 | Img: 640",
        (15, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 255, 0),
        2
    )

    cv2.imshow("Diagnostico YOLO - Monedas", annotated)

    key = cv2.waitKey(1) & 0xFF

    # Guardar frame original para etiquetarlo despues
    if key == ord("s"):
        filename = f"moneda_{int(time.time() * 1000)}.jpg"
        path = os.path.join(SAVE_DIR, filename)

        if cv2.imwrite(path, frame):
            print("Foto guardada:", path)
        else:
            print("No se pudo guardar la foto.")

    elif key == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()

print("\nDiagnostico finalizado.")
