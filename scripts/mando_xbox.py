"""Control del carro oruga con mando Xbox 360 cableado.

El mando se conecta por USB a la PC. Python lee los ejes mediante XInput
(biblioteca `inputs`, puro Python) y envía órdenes al ESP32 por serial,
usando el protocolo definido en CarroOruga/CarroOruga.ino.

Controles:
  Stick izquierdo  -> avance / giro diferencial
  A                -> alternar modo automático (evasión con HC-SR04)
  B                -> detener
  X                -> consultar distancia
  Y                -> consultar estado
  Ctrl+C           -> salir

Uso:
    python scripts/mando_xbox.py --puerto COM3
    python scripts/mando_xbox.py --simular
"""

import argparse
import sys
import time

try:
    import inputs
except ImportError:
    print("Falta la librería 'inputs'. Instálala con: pip install inputs")
    sys.exit(1)

try:
    import serial
except ImportError:
    serial = None

BAUD = 115200
ZONA_MUERTA = 0.15
PERIODO_ENVIO = 0.05   # s
MAX_EJE = 32768.0


def clamp(valor, minimo=-255, maximo=255):
    return max(minimo, min(maximo, valor))


def aplicar_zona_muerta(valor, zona=ZONA_MUERTA):
    if abs(valor) < zona:
        return 0.0
    return (valor - zona * (1 if valor > 0 else -1)) / (1 - zona)


class SerialSimulado:
    """Reemplazo de pyserial para probar sin hardware."""

    def __init__(self):
        self.buffer = []

    def write(self, datos):
        print(f"  [SIM] TX -> {datos.decode().strip()}")

    def readline(self):
        if self.buffer:
            return self.buffer.pop(0).encode()
        return b""

    @property
    def in_waiting(self):
        return len(self.buffer)

    def close(self):
        pass


def abrir_puerto(puerto, simular):
    if simular:
        return SerialSimulado()
    if serial is None:
        print("Falta pyserial: pip install pyserial")
        sys.exit(1)
    esp = serial.Serial(port=puerto, baudrate=BAUD, timeout=0.05)
    time.sleep(2)
    return esp


def nombre_boton(codigo):
    """Normaliza nombres de botones entre versiones del driver."""
    alias = {
        "BTN_TRIGGER": "A",
        "BTN_THUMB": "B",
        "BTN_THUMB2": "B",
        "BTN_TOP": "X",
        "BTN_TOP2": "Y",
    }
    if codigo and codigo.startswith("BTN_"):
        return alias.get(codigo, codigo[4:])
    return codigo


def main():
    parser = argparse.ArgumentParser(description="Mando Xbox -> Carro oruga")
    parser.add_argument("--puerto", default="COM3")
    parser.add_argument("--baud", type=int, default=BAUD)
    parser.add_argument("--simular", action="store_true")
    args = parser.parse_args()

    # ---------- Mando ----------
    gamepads = inputs.devices.gamepads
    if not gamepads:
        print("No se detectó ningún mando conectado.")
        print("Conecta el mando Xbox 360 por cable e inténtalo de nuevo.")
        sys.exit(1)

    mando = gamepads[0]
    print("Mando detectado. Presiona los botones para ver los códigos si hace falta.")
    print("Controles: stick izq, A=auto, B=stop, X=distancia, Y=estado, Ctrl+C=salir")

    esp = abrir_puerto(args.puerto, args.simular)
    print("Serial listo.", "[SIMULACIÓN]" if args.simular else args.puerto)

    estado = {}
    ultimo_envio = 0.0
    anatomia_anterior = None

    try:
        while True:
            ahora = time.time()

            # 1. Leer eventos del mando
            try:
                eventos = inputs.get_gamepad()
            except inputs.InputError:
                time.sleep(0.2)
                continue

            for evento in eventos:
                codigo = evento.code
                if evento.ev_type == "Absolute":
                    estado[codigo] = evento.state
                elif evento.ev_type == "Key":
                    anterior = estado.get(codigo, 0)
                    estado[codigo] = evento.state
                    if evento.state == 1 and anterior == 0:
                        boton = nombre_boton(codigo)
                        if boton == "A":
                            esp.write(b"A\n")
                            print(">> Alternar modo automático")
                        elif boton == "B":
                            esp.write(b"S\n")
                            print(">> Detener")
                        elif boton == "X":
                            esp.write(b"D\n")
                            print(">> Consultar distancia")
                        elif boton == "Y":
                            esp.write(b"T\n")
                            print(">> Consultar estado")

            # 2. Ejes del stick izquierdo (ABS_X / ABS_Y)
            eje_x = estado.get("ABS_X", 0) / MAX_EJE
            eje_y = estado.get("ABS_Y", 0) / MAX_EJE
            eje_x = aplicar_zona_muerta(eje_x)
            eje_y = aplicar_zona_muerta(eje_y)

            avance = -eje_y           # stick arriba => avanzar
            giro = eje_x              # stick derecha => girar

            izq = clamp(int((avance + giro) * 255))
            der = clamp(int((avance - giro) * 255))

            estado_motores = (izq, der)
            if ahora - ultimo_envio >= PERIODO_ENVIO or estado_motores != anatomia_anterior:
                esp.write(f"M,{izq},{der}\n".encode())
                anatomia_anterior = estado_motores
                ultimo_envio = ahora

            # 3. Telemetría del ESP32
            if getattr(esp, "in_waiting", 0) > 0:
                try:
                    linea = esp.readline().decode(errors="ignore").strip()
                    if linea.startswith(("T,", "D:", "E:", "Modo", "Detenido", "E:")):
                        print("  ESP32:", linea)
                except Exception:
                    pass

            time.sleep(0.01)

    except KeyboardInterrupt:
        print("\nInterrumpido por el usuario.")
    finally:
        esp.write(b"S\n")
        if hasattr(esp, "close"):
            esp.close()
        print("Fin del control.")


if __name__ == "__main__":
    main()
