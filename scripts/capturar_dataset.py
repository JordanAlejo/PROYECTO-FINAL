"""Captura fotogramas crudos desde la camara para crear un dataset del montaje real.

Uso:
    python scripts/capturar_dataset.py            # camara USB indice 0
    python scripts/capturar_dataset.py 1          # otro indice
    python scripts/capturar_dataset.py http://... # camara IP

Mientras se muestra la ventana, presiona la tecla correspondiente a la
moneda que esta en pantalla. El fotograma CRUDO (sin anotaciones) se guarda
en dataset_reposicion/images/<clase>/ con el nombre de clase ya asignado.
Presiona 'q' o ESC para salir.
"""

import os
import sys
import time
import cv2

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "dataset_reposicion", "images")

# Tecla -> clase del modelo (mismo orden que dataset_9clases/data.yaml)
CLASES = {
    "1": "1000_pesos",
    "2": "100_pesos",
    "3": "100_pesos_nueva",
    "4": "200_pesos",
    "5": "200_pesos_nueva",
    "6": "500_pesos",
    "7": "500_pesos_nueva",
    "8": "50_pesos",
    "9": "50_pesos_nueva",
}

if __name__ == "__main__":
    source = 0
    if len(sys.argv) > 1:
        value = sys.argv[1]
        source = int(value) if value.isdigit() else value

    cap = cv2.VideoCapture(source)
    if not cap.isOpened():
        print("No se pudo abrir la camara:", source)
        print("Prueba antes: python scripts/probar_camara.py")
        sys.exit(1)

    print("Camara abierta:", source)
    print("Teclas: 1=1000  2=100  3=100nueva  4=200  5=200nueva")
    print("        6=500  7=500nueva  8=50  9=50nueva   |   q=salir")
    print("Guardando en:", OUT_DIR)

    guardadas = 0
    while True:
        ok, frame = cap.read()
        if not ok:
            print("Se perdio la conexion con la camara.")
            break

        vis = frame.copy()
        cv2.putText(
            vis,
            "1=1000 2=100 3=100n 4=200 5=200n 6=500 7=500n 8=50 9=50n | q=salir",
            (10, 28),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (0, 255, 0),
            2,
        )
        cv2.putText(
            vis,
            f"Guardadas: {guardadas}",
            (10, vis.shape[0] - 15),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 255, 255),
            2,
        )
        cv2.imshow("Captura de dataset - montaje real", vis)

        key = cv2.waitKey(1) & 0xFF
        if key == ord("q") or key == 27:
            break

        clase = CLASES.get(chr(key)) if 0 < key < 128 else None
        if clase:
            carpeta = os.path.join(OUT_DIR, clase)
            os.makedirs(carpeta, exist_ok=True)
            nombre = f"{clase}_{int(time.time() * 1000)}.jpg"
            ruta = os.path.join(carpeta, nombre)
            if cv2.imwrite(ruta, frame):
                guardadas += 1
                print(f"Guardada [{clase}]: {nombre}")
            else:
                print("No se pudo guardar.")

    cap.release()
    cv2.destroyAllWindows()
    print("Total guardadas:", guardadas)
