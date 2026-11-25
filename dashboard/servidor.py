"""Dashboard web: clasificador YOLO + carro oruga, sin dependencias extra.

Sirve index.html y expone:
  GET  /video              -> MJPEG en vivo con detecciones
  GET  /api/estado         -> conteo + telemetría
  POST /api/comando        -> {"comando": "M,1,2" | "A" | "S" | "D" | "T"}
  POST /api/reiniciar      -> reinicia el conteo

Uso:
    python dashboard/servidor.py
    python dashboard/servidor.py --camara 1 --puerto-serial COM3
    python dashboard/servidor.py --simular     # sin ESP32
"""

import os
import sys
import json
import time
import threading
from collections import Counter
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import cv2

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

from ultralytics import YOLO  # noqa: E402
from mapeo_esp32 import codigo_para_clase, ANGULOS  # noqa: E402

PESOS = os.path.join(ROOT, "runs", "monedas_balanceado_v2", "weights", "best.pt")

try:
    import serial
except ImportError:
    serial = None

# ---------------- Config ----------------
IMGSZ = 416
CONF = 0.30
FRAMES_ESTABLES = 3
FRAMES_SIN_MONEDA = 5
NOMBRES_CLASES = [
    "1000_pesos", "100_pesos", "100_pesos_nueva",
    "200_pesos", "200_pesos_nueva", "500_pesos",
    "500_pesos_nueva", "50_pesos", "50_pesos_nueva",
]
EMOJIS = ["🪙", "🟡", "🟡", "🟡", "🟡", "🟡", "🟡", "⚪", "⚪"]

# ---------------- Estado compartido ----------------
estado = {
    "distancia": 999,
    "modo_auto": False,
    "izq": 0,
    "der": 0,
    "conteo": {n: 0 for n in NOMBRES_CLASES},
    "total": 0,
    "ultima": "—",
    "camara": False,
    "serial": False,
    "separador": False,
    "ultimo_codigo": "—",
    "logs": [],
}

ultimo_frame = None
lock = threading.Lock()
puerto_serial = None
puerto_separador = None


def log(mensaje):
    with lock:
        estado["logs"].insert(0, f"{time.strftime('%H:%M:%S')}  {mensaje}")
        estado["logs"] = estado["logs"][:12]


def enviar(comando):
    global puerto_serial
    if puerto_serial is None:
        return False
    try:
        puerto_serial.write(f"{comando}\n".encode())
        return True
    except Exception as error:
        log(f"Error serial: {error}")
        return False


def enviar_separador(codigo):
    """YOLO -> ESP32 del separador (mismo protocolo: 'codigo\\n')."""
    global puerto_separador
    if puerto_separador is None:
        return False
    try:
        puerto_separador.write(f"{codigo}\n".encode())
        angulo = ANGULOS.get(codigo, "?")
        with lock:
            estado["ultimo_codigo"] = f"{codigo} ({angulo}°)"
        log(f"YOLO -> ESP32 separador: codigo {codigo} -> {angulo}°")
        return True
    except Exception as error:
        log(f"Error serial separador: {error}")
        return False


# ---------------- Hilo: lectura de telemetría ----------------
def hilo_serial():
    while True:
        if puerto_serial is None:
            time.sleep(0.5)
            continue
        try:
            linea = puerto_serial.readline().decode(errors="ignore").strip()
        except Exception:
            time.sleep(0.1)
            continue
        if not linea:
            continue
        if linea.startswith("T,"):
            partes = linea.split(",")
            try:
                with lock:
                    estado["distancia"] = int(partes[1])
                    estado["modo_auto"] = bool(int(partes[2]))
                    estado["izq"] = int(partes[3])
                    estado["der"] = int(partes[4])
            except (ValueError, IndexError):
                pass
        elif linea.startswith("D:"):
            try:
                with lock:
                    estado["distancia"] = int(linea[2:])
            except ValueError:
                pass
        elif linea.startswith("E:") or linea.startswith("Modo"):
            log(linea)


# ---------------- Hilo: cámara + YOLO + conteo ----------------
def hilo_video(camara):
    global ultimo_frame

    if not os.path.exists(PESOS):
        log("No existe el modelo final")
        return

    log("Cargando modelo YOLO...")
    model = YOLO(PESOS)
    log("Modelo cargado")

    cap = cv2.VideoCapture(camara)
    if not cap.isOpened():
        log(f"No se pudo abrir la cámara {camara}")
        return
    with lock:
        estado["camara"] = True
    log(f"Cámara {camara} abierta")

    candidato = None
    frames_ok = 0
    frames_vacio = 0

    while True:
        ok, frame = cap.read()
        if not ok:
            time.sleep(0.1)
            continue

        res = model.predict(
            frame, conf=CONF, imgsz=IMGSZ, max_det=1, verbose=False
        )[0]

        if len(res.boxes) > 0:
            cls = int(res.boxes[0].cls[0])
            conf = float(res.boxes[0].conf[0])
            frames_vacio = 0
            if cls == candidato:
                frames_ok += 1
                if frames_ok == FRAMES_ESTABLES:
                    nombre = model.names[cls]
                    with lock:
                        estado["conteo"][nombre] += 1
                        estado["total"] += 1
                        estado["ultima"] = f"{nombre} ({conf:.0%})"
                    log(f"Moneda contada: {nombre}")
                    # Enviar el caso al ESP32 del separador
                    codigo = codigo_para_clase(cls)
                    if codigo is not None:
                        enviar_separador(codigo)
                    else:
                        log(f"{nombre}: sin codigo ESP32")
            else:
                candidato = cls
                frames_ok = 1
        else:
            frames_vacio += 1
            if frames_vacio >= FRAMES_SIN_MONEDA:
                candidato = None
                frames_ok = 0
                frames_vacio = 0

        vis = res.plot()
        with lock:
            total = estado["total"]
            ultima = estado["ultima"]
        cv2.rectangle(vis, (0, 0), (430, 74), (20, 20, 20), -1)
        cv2.putText(vis, f"MONEDAS CONTADAS: {total}", (12, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        cv2.putText(vis, f"Ultima: {ultima}", (12, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

        ret, jpg = cv2.imencode(".jpg", vis, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
        if ret:
            ultimo_frame = jpg.tobytes()

        time.sleep(0.01)


# ---------------- Servidor HTTP ----------------
class Handler(BaseHTTPRequestHandler):
    def log_message(self, *_args):
        pass

    def _json(self, datos, codigo=200):
        cuerpo = json.dumps(datos).encode()
        self.send_response(codigo)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(cuerpo)))
        self.end_headers()
        self.wfile.write(cuerpo)

    def _archivo(self, nombre, tipo):
        ruta = os.path.join(os.path.dirname(os.path.abspath(__file__)), nombre)
        if not os.path.exists(ruta):
            self.send_error(404)
            return
        with open(ruta, "rb") as f:
            cuerpo = f.read()
        self.send_response(200)
        self.send_header("Content-Type", tipo)
        self.send_header("Content-Length", str(len(cuerpo)))
        self.end_headers()
        self.wfile.write(cuerpo)

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            return self._archivo("index.html", "text/html; charset=utf-8")
        if self.path == "/api/estado":
            with lock:
                copia = {
                    "distancia": estado["distancia"],
                    "modo_auto": estado["modo_auto"],
                    "izq": estado["izq"],
                    "der": estado["der"],
                    "conteo": dict(estado["conteo"]),
                    "total": estado["total"],
                    "ultima": estado["ultima"],
                    "camara": estado["camara"],
                    "serial": estado["serial"],
                    "logs": list(estado["logs"]),
                }
            return self._json(copia)
        if self.path == "/video":
            self.send_response(200)
            self.send_header("Content-Type",
                             "multipart/x-mixed-replace; boundary=frame")
            self.end_headers()
            while True:
                global ultimo_frame
                if ultimo_frame:
                    try:
                        self.wfile.write(b"--frame\r\n")
                        self.wfile.write(b"Content-Type: image/jpeg\r\n")
                        self.wfile.write(
                            b"Content-Length: " + str(len(ultimo_frame)).encode() + b"\r\n\r\n"
                        )
                        self.wfile.write(ultimo_frame)
                        self.wfile.write(b"\r\n")
                        self.wfile.flush()
                    except (BrokenPipeError, ConnectionResetError):
                        break
                time.sleep(0.05)
            return

        self.send_error(404)

    def do_POST(self):
        longitud = int(self.headers.get("Content-Length", 0))
        cuerpo = self.rfile.read(longitud).decode(errors="ignore")

        if self.path == "/api/comando":
            try:
                datos = json.loads(cuerpo)
                comando = str(datos.get("comando", "")).strip()
            except Exception:
                return self._json({"ok": False, "error": "JSON inválido"}, 400)

            partes = comando.split(",")
            valido = (
                comando in ("A", "S", "D", "T")
                or (len(partes) == 3 and partes[0] == "M"
                    and all(p.lstrip("-").isdigit() for p in partes[1:])
                    and all(-255 <= int(p) <= 255 for p in partes[1:]))
            )
            if not valido:
                return self._json({"ok": False, "error": "Comando no válido"}, 400)

            enviado = enviar(comando)
            if comando.startswith("M"):
                with lock:
                    estado["izq"] = int(partes[1])
                    estado["der"] = int(partes[2])
            elif comando == "S":
                with lock:
                    estado["izq"] = 0
                    estado["der"] = 0
            elif comando == "A":
                with lock:
                    estado["modo_auto"] = not estado["modo_auto"]
            log(f"Comando: {comando}")
            return self._json({"ok": True, "enviado": enviado})

        if self.path == "/api/reiniciar":
            with lock:
                estado["conteo"] = {n: 0 for n in NOMBRES_CLASES}
                estado["total"] = 0
                estado["ultima"] = "—"
            log("Conteo reiniciado")
            return self._json({"ok": True})

        self.send_error(404)


def main():
    global puerto_serial, puerto_separador

    import argparse
    parser = argparse.ArgumentParser(description="Dashboard web del proyecto")
    parser.add_argument("--camara", default="1")
    parser.add_argument("--puerto-serial", default="COM3",
                        help="Puerto del carro oruga")
    parser.add_argument("--puerto-separador", default=None,
                        help="Puerto del ESP32 del separador de monedas")
    parser.add_argument("--baud", type=int, default=115200)
    parser.add_argument("--simular", action="store_true",
                        help="No abre serial (para probar la interfaz)")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--web", type=int, default=8000)
    args = parser.parse_args()

    camara = int(args.camara) if args.camara.isdigit() else args.camara

    if not args.simular:
        if serial is None:
            print("Falta pyserial. Usa --simular o instala pyserial.")
            sys.exit(1)
        try:
            puerto_serial = serial.Serial(
                port=args.puerto_serial, baudrate=args.baud, timeout=0.1
            )
            time.sleep(2)
            with lock:
                estado["serial"] = True
            print("Serial conectado:", args.puerto_serial)
        except Exception as error:
            print("No se pudo abrir serial:", error)
            print("Continúo en modo simulación.")
    else:
        print("Modo simulación: sin ESP32")

    # Segundo puerto: ESP32 del separador (YOLO -> caso)
    if args.puerto_separador and serial is not None:
        try:
            puerto_separador = serial.Serial(
                port=args.puerto_separador, baudrate=args.baud, timeout=0.1
            )
            time.sleep(2)
            with lock:
                estado["separador"] = True
            print("Separador conectado:", args.puerto_separador)
        except Exception as error:
            print("No se pudo abrir separador:", error)
    elif args.puerto_separador:
        print("Sin pyserial: el separador no enviará códigos.")

    threading.Thread(target=hilo_serial, daemon=True).start()
    threading.Thread(target=hilo_video, args=(camara,), daemon=True).start()

    servidor = ThreadingHTTPServer((args.host, args.web), Handler)
    print(f"\nDashboard: http://{args.host}:{args.web}")
    print("Ctrl+C para salir.\n")
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("\nCerrando dashboard...")
    finally:
        if puerto_serial:
            puerto_serial.close()
        if puerto_separador:
            puerto_separador.close()
        servidor.server_close()


if __name__ == "__main__":
    main()
