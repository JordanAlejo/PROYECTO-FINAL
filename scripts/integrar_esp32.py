"""YOLO -> ESP32 del separador (modo manual o automatico).

  Manual:   ESPACIO envia la clase que se esta leyendo.
  Auto:     al detectar una moneda espera --espera segundos y envia sola.

Teclas: ESPACIO=enviar (manual) | q=salir

Uso:
    python scripts/integrar_esp32.py 1 --puerto COM8
    python scripts/integrar_esp32.py 1 --puerto COM8 --auto --espera 3
    python scripts/integrar_esp32.py 1 --simular --auto
"""

import os
import sys
import time
import argparse

import cv2

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

from ultralytics import YOLO  # noqa: E402
from mapeo_esp32 import codigo_para_clase, ANGULOS  # noqa: E402

PESOS = os.path.join(ROOT, "runs", "monedas_balanceado_v2", "weights", "best.pt")
CONF = 0.30
IMGSZ = 416
FRAMES_RESET = 5


def abrir_serial(puerto, baudrate, simular):
    if simular:
        class SerialSimulado:
            def write(self, datos):
                print(f"  [SIMULACION] TX -> {datos.decode().strip()}")
            def close(self):
                pass
        return SerialSimulado()
    import serial
    try:
        return serial.Serial(port=puerto, baudrate=baudrate, timeout=1)
    except PermissionError:
        print(f"ERROR: El puerto {puerto} esta OCUPADO.")
        print("Cierra el Monitor Serie de Arduino IDE u otra app que lo use.")
        sys.exit(1)
    except Exception as error:
        print(f"ERROR al abrir {puerto}: {error}")
        sys.exit(1)


def enviar(esp32, cls, modelo):
    codigo = codigo_para_clase(cls)
    if codigo is None:
        print("Esa clase no tiene codigo ESP32.")
        return False
    esp32.write(f"{codigo}\n".encode())
    angulo = ANGULOS.get(codigo, "?")
    print(f"[{time.strftime('%H:%M:%S')}] ENVIADO caso {codigo} -> "
          f"{modelo.names[cls]} ({angulo}°)")
    return True


def main():
    parser = argparse.ArgumentParser(description="YOLO -> ESP32")
    parser.add_argument("camara", nargs="?", default="1")
    parser.add_argument("--puerto", default="COM8")
    parser.add_argument("--baud", type=int, default=115200)
    parser.add_argument("--simular", action="store_true")
    parser.add_argument("--auto", action="store_true", help="Envio automatico")
    parser.add_argument("--espera", type=float, default=3.0,
                        help="Segundos a esperar en modo automatico")
    args = parser.parse_args()

    if not os.path.exists(PESOS):
        print("No existe el modelo:", PESOS)
        sys.exit(1)

    esp32 = abrir_serial(args.puerto, args.baud, args.simular)

    print("Cargando modelo...")
    modelo = YOLO(PESOS)

    fuente = int(args.camara) if args.camara.isdigit() else args.camara
    cap = cv2.VideoCapture(fuente)
    if not cap.isOpened():
        print("No se pudo abrir la camara:", fuente)
        sys.exit(1)

    modo = "AUTO" if args.auto else "MANUAL"
    print(f"Modo {modo} | camara {fuente} | conf={CONF}")
    if args.auto:
        print(f"Al detectar una moneda espera {args.espera} s y envia sola.")
    else:
        print("ESPACIO = enviar | q = salir")

    clase_actual = None
    enviada = False
    inicio = 0.0
    frames_vacio = 0
    enviados = 0

    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                print("Se perdio la camara.")
                break

            res = modelo.predict(
                frame, conf=CONF, imgsz=IMGSZ, verbose=False
            )[0]

            vis = res.plot()
            ahora = time.time()

            if len(res.boxes) > 0:
                mejor = max(res.boxes, key=lambda b: float(b.conf[0]))
                cls = int(mejor.cls[0])
                conf = float(mejor.conf[0])
                frames_vacio = 0

                if cls != clase_actual:
                    clase_actual = cls
                    enviada = False
                    inicio = ahora

                nombre = modelo.names[cls]
                codigo = codigo_para_clase(cls)
                angulo = ANGULOS.get(codigo, "?")

                if args.auto:
                    restante = args.espera - (ahora - inicio)
                    if restante > 0:
                        estado = f"AUTO: {nombre} {conf:.0%} -> envio en {restante:.1f}s"
                        color = (0, 255, 255)
                    else:
                        estado = f"AUTO: {nombre} -> ENVIANDO caso {codigo}"
                        color = (0, 255, 0)
                else:
                    estado = f"LEYENDO: {nombre} {conf:.0%} -> caso {codigo} ({angulo}°)"
                    color = (0, 255, 0)

                if args.auto and not enviada and (ahora - inicio) >= args.espera:
                    if enviar(esp32, cls, modelo):
                        enviados += 1
                    enviada = True
            else:
                frames_vacio += 1
                if frames_vacio >= FRAMES_RESET:
                    if clase_actual is not None:
                        print("Moneda retirada. Listo para la siguiente.")
                    clase_actual = None
                    enviada = False
                    frames_vacio = 0
                estado = "Sin moneda a la vista"
                color = (0, 255, 255)

            cv2.rectangle(vis, (0, 0), (640, 40), (20, 20, 20), -1)
            cv2.putText(vis, estado, (10, 28), cv2.FONT_HERSHEY_SIMPLEX,
                        0.65, color, 2)
            cv2.putText(vis, f"Modo {modo} | enviados: {enviados} | q=salir",
                        (10, vis.shape[0] - 12), cv2.FONT_HERSHEY_SIMPLEX,
                        0.6, (255, 255, 255), 2)
            cv2.imshow("YOLO -> ESP32", vis)

            tecla = cv2.waitKey(1) & 0xFF
            if tecla == ord("q"):
                break
            if not args.auto and (tecla == 32 or tecla == 13):
                if clase_actual is None:
                    print("No hay moneda detectada para enviar.")
                else:
                    if enviar(esp32, clase_actual, modelo):
                        enviados += 1

    finally:
        cap.release()
        cv2.destroyAllWindows()
        esp32.close()
        print("Fin. Casos enviados:", enviados)


if __name__ == "__main__":
    main()
