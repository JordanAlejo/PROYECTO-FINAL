# Sistema Automatizado de Clasificación de Monedas Colombianas mediante Visión Artificial

**Integración de YOLO, Python, ESP32 y control electromecánico**

---

## 1. Descripción general

El presente proyecto consiste en el diseño e implementación de un sistema automatizado para la identificación y clasificación de monedas colombianas de diferentes denominaciones y diseños, mediante técnicas de visión artificial y control electromecánico.

El sistema utiliza un modelo de detección de objetos YOLO, desarrollado e implementado en Python mediante el entorno de programación Visual Studio Code. Su funcionamiento integra procesamiento digital de imágenes, comunicación serial, sistemas embebidos y mecanismos de posicionamiento.

El proceso comienza con la alimentación individual de las monedas mediante una rampa diseñada para facilitar su desplazamiento por gravedad. Posteriormente, cada moneda llega a una zona de inspección, donde se detiene temporalmente para permitir la captura de su imagen mediante una cámara.

La imagen obtenida es procesada por el modelo YOLO, encargado de identificar la denominación y el diseño de la moneda. Una vez determinada la clase, el programa establece una correspondencia entre el resultado de la detección y el código de control asociado al destino de clasificación.

La información se transmite mediante comunicación serial USB hacia un microcontrolador ESP32, encargado de controlar dos actuadores:

- **Motor paso a paso:** posiciona el mecanismo de selección en el ángulo correspondiente a la moneda identificada.
- **Servomotor:** acciona el mecanismo de direccionamiento para permitir el desplazamiento de la moneda hacia el compartimento asignado.

Finalmente, la moneda continúa su recorrido por la estructura mecánica hasta llegar al almacén correspondiente.

## 2. Objetivos

### 2.1. Objetivo general

Desarrollar un sistema automatizado para la clasificación de monedas colombianas mediante la integración de visión artificial con YOLO, programación en Python y control electromecánico mediante un microcontrolador ESP32, con el propósito de identificar diferentes denominaciones y diseños y dirigir cada moneda hacia su respectivo compartimento de almacenamiento.

### 2.2. Objetivos específicos

- Implementar un modelo de detección de objetos YOLO entrenado para reconocer diferentes diseños de monedas colombianas.
- Desarrollar un programa en Python para capturar, procesar y analizar imágenes mediante OpenCV.
- Establecer una correspondencia entre las clases detectadas por el modelo y las instrucciones de clasificación.
- Implementar la comunicación serial USB entre el computador y el microcontrolador ESP32.
- Desarrollar un sistema de posicionamiento mediante un motor paso a paso y un servomotor.
- Integrar los componentes electrónicos y mecánicos para realizar la clasificación física de las monedas.

## 3. Funcionamiento del sistema

El funcionamiento general del prototipo se desarrolla mediante las siguientes etapas:

### 3.1. Alimentación de monedas

Las monedas ingresan individualmente al sistema mediante una rampa diseñada para facilitar su desplazamiento por gravedad.

### 3.2. Posicionamiento e inspección

Cada moneda llega a una zona de inspección, donde se detiene temporalmente para evitar movimientos durante la captura de la imagen.

### 3.3. Captura y procesamiento de imágenes

Una cámara conectada al computador captura la imagen de la moneda. Posteriormente, Python procesa la información visual utilizando un modelo YOLO previamente entrenado con imágenes de las monedas seleccionadas.

### 3.4. Identificación y clasificación

El modelo YOLO analiza la imagen y determina la clase a la que pertenece la moneda. Para aceptar una detección, se establece un umbral mínimo de confianza del 25 %, configurado mediante el parámetro `conf=0.25`.

### 3.5. Selección del destino

Python obtiene el identificador de la clase detectada y consulta una tabla de correspondencias que relaciona cada tipo de moneda con una instrucción numérica para el ESP32.

### 3.6. Comunicación con el microcontrolador

Una vez determinada la clasificación, el programa transmite el código correspondiente mediante comunicación serial USB hacia el ESP32.

### 3.7. Accionamiento electromecánico

El microcontrolador interpreta la instrucción recibida y ejecuta la secuencia de movimiento:

1. El motor paso a paso gira hasta alcanzar el ángulo establecido para la clasificación.
2. El servomotor gira hasta 180°, acciona el mecanismo de direccionamiento y posteriormente regresa a su posición inicial de 0°.

### 3.8. Clasificación y almacenamiento

El mecanismo permite que la moneda continúe su desplazamiento por la rampa hasta llegar al compartimento asignado.

Una vez finalizado el proceso, el sistema queda preparado para procesar la siguiente moneda.

## 4. Clasificaciones reconocidas

El modelo de visión artificial fue entrenado para reconocer nueve clases correspondientes a diferentes denominaciones y diseños de monedas colombianas.

| Identificador | Denominación | Diseño |
|:---:|:---:|:---:|
| 0 | $50 | Antigua |
| 1 | $50 | Nueva |
| 2 | $100 | Antigua |
| 3 | $100 | Nueva |
| 4 | $200 | Antigua |
| 5 | $200 | Nueva |
| 6 | $500 | Antigua |
| 7 | $500 | Nueva |
| 8 | $1.000 | Única |

Cada clase representa una característica física diferenciada y tiene asociado un destino de clasificación.

La selección de las clases se estableció a partir de las versiones físicas de las monedas utilizadas durante el desarrollo del proyecto.

## 5. Herramientas y tecnologías

| Tecnología o componente | Aplicación |
|---|---|
| Python | Procesamiento de imágenes y lógica de clasificación. |
| YOLO | Detección e identificación de monedas. |
| Ultralytics | Implementación y ejecución del modelo YOLO. |
| OpenCV | Captura y procesamiento de imágenes. |
| Visual Studio Code | Entorno de desarrollo y depuración. |
| ESP32 | Control del sistema electromecánico. |
| Arduino IDE | Programación del microcontrolador. |
| ESP32Servo | Control del servomotor. |
| Stepper | Control del motor paso a paso. |
| PySerial | Comunicación serial entre Python y ESP32. |
| Cámara | Captura de imágenes de las monedas. |
| Motor paso a paso | Posicionamiento angular del mecanismo. |
| Servomotor | Accionamiento del mecanismo de direccionamiento. |

---

# 6. Desarrollo e implementación del software

La arquitectura de programación se divide en dos módulos principales:

1. **Módulo de visión artificial:** desarrollado en Python, encargado de capturar imágenes, realizar detecciones mediante YOLO e identificar la clase correspondiente.
2. **Módulo de control electromecánico:** desarrollado para el ESP32, encargado de interpretar las instrucciones recibidas y controlar los actuadores.

## 6.1. Módulo de visión artificial mediante YOLO

El módulo de visión artificial constituye la etapa de reconocimiento del sistema. Su función es detectar las monedas presentes en una imagen, identificar su denominación y diseño y determinar la clase a la que pertenece cada objeto.

Para esta implementación se utilizó YOLO (You Only Look Once), un modelo de detección de objetos entrenado con imágenes de monedas colombianas.

El programa utiliza las bibliotecas Ultralytics YOLO y OpenCV.

### 6.1.1. Importación de bibliotecas

```python
import os
import sys
import glob
import cv2
from ultralytics import YOLO
```

**Descripción de las bibliotecas:**

- `os`: permite gestionar directorios, rutas y archivos del sistema operativo.
- `sys`: permite recibir argumentos desde la terminal y controlar la ejecución del programa.
- `glob`: permite buscar archivos que coincidan con determinados patrones.
- `cv2`: corresponde a OpenCV, utilizada para capturar, procesar y visualizar imágenes.
- `YOLO`: permite cargar el modelo entrenado y ejecutar las predicciones de detección.

### 6.1.2. Configuración de la ruta del proyecto

```python
ROOT = r"C:\Users\Cocot\Desktop\yolo_monedas_colombia - copia"
```

Esta variable almacena la ubicación principal del proyecto. A partir de ella se construyen las rutas necesarias para localizar los pesos del modelo, las imágenes de prueba y los resultados generados.

La ruta debe ajustarse a la ubicación del proyecto en el equipo donde se ejecute el programa.

### 6.1.3. Búsqueda y carga del modelo entrenado

```python
candidates = (
    glob.glob(
        os.path.join(ROOT, "runs", "*", "weights", "best.pt")
    )
    or
    glob.glob(
        os.path.join(ROOT, "runs", "*", "weights", "last.pt")
    )
)

if not candidates:
    print("No hay pesos entrenados.")
    sys.exit(1)

WEIGHTS = max(candidates, key=os.path.getmtime)

model = YOLO(WEIGHTS)
```

Esta sección permite localizar automáticamente los pesos del modelo YOLO.

Durante el entrenamiento se generan archivos que contienen los parámetros aprendidos por la red neuronal:

- `best.pt`: almacena los pesos correspondientes al mejor rendimiento obtenido durante el entrenamiento.
- `last.pt`: almacena los pesos guardados al finalizar la última época de entrenamiento.

El programa busca inicialmente los archivos `best.pt`. Si no encuentra ninguno, intenta localizar los archivos `last.pt`.

Cuando existen varios modelos disponibles, selecciona el archivo modificado más recientemente mediante `os.path.getmtime()`.

Finalmente, se utiliza `YOLO(WEIGHTS)` para cargar el modelo y prepararlo para realizar las detecciones.

### 6.1.4. Detección mediante imágenes almacenadas

```python
def show_image(path):

    img = cv2.imread(path)

    if img is None:
        print("No se pudo leer", path)
        return

    res = model.predict(
        img,
        conf=0.25,
        imgsz=320,
        verbose=False
    )[0]

    annotated = res.plot()

    out_dir = os.path.join(ROOT, "runs", "demo")
    os.makedirs(out_dir, exist_ok=True)

    out_path = os.path.join(out_dir, "resultado.jpg")

    cv2.imwrite(out_path, annotated)

    print("Guardado:", out_path)

    os.startfile(out_path)

    return out_path
```

Esta función permite evaluar una imagen utilizando el modelo YOLO.

Su funcionamiento se desarrolla mediante las siguientes operaciones:

1. `cv2.imread(path)` carga la imagen desde la ubicación indicada.
2. Se verifica que la imagen haya sido leída correctamente.
3. `model.predict()` ejecuta la detección utilizando el modelo entrenado.
4. `conf=0.25` establece un umbral mínimo de confianza del 25 %.
5. `imgsz=320` establece el tamaño de entrada utilizado para la predicción.
6. `res.plot()` genera una imagen con las detecciones y sus etiquetas.
7. `cv2.imwrite()` guarda el resultado en la carpeta `runs/demo`.
8. `os.startfile()` abre automáticamente la imagen generada en Windows.

El resultado permite visualizar las monedas detectadas, sus respectivas clases y los niveles de confianza.

### 6.1.5. Detección mediante cámara web

```python
def webcam():

    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("No se pudo abrir la webcam.")
        return

    print("Presiona 'q' para salir.")

    while True:

        ok, frame = cap.read()

        if not ok:
            break

        res = model.predict(
            frame,
            conf=0.25,
            imgsz=320,
            verbose=False
        )[0]

        cv2.imshow(
            "Webcam - monedas (q para salir)",
            res.plot()
        )

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
```

Esta función permite realizar detecciones en tiempo real utilizando una cámara conectada al computador.

El procedimiento inicia con la apertura del dispositivo mediante `cv2.VideoCapture(0)`. Posteriormente, se capturan continuamente fotogramas utilizando `cap.read()`.

Cada imagen capturada es procesada por YOLO y el resultado se presenta en una ventana de OpenCV mediante `cv2.imshow()`.

El proceso continúa hasta que el usuario presiona la tecla `q`. Finalmente, se libera la cámara y se cierran las ventanas.

### 6.1.6. Control de ejecución principal

```python
if __name__ == "__main__":

    if len(sys.argv) > 1 and sys.argv[1].lower() == "webcam":

        webcam()

    else:

        if len(sys.argv) > 1:
            src = sys.argv[1]

        else:
            vals = glob.glob(
                os.path.join(ROOT, "data", "images", "val", "*.jpg")
            )

            src = vals[0] if vals else None

        if src is None:

            print("Pasa una imagen o usa 'webcam'.")

        else:

            show_image(src)
```

Este bloque determina el modo de ejecución del programa.

Se establecieron dos modalidades:

**Detección mediante cámara web:** cuando se ejecuta el programa con el argumento `webcam`, se activa la función encargada de capturar y procesar imágenes en tiempo real.

**Detección mediante imagen:** cuando se proporciona una ruta de imagen, el programa procesa directamente el archivo indicado. Si no se proporciona una ruta, busca automáticamente una imagen dentro del conjunto de validación.

---

## 6.2. Identificación de clases y selección de casos

Una vez que YOLO detecta una moneda, el programa puede obtener la información correspondiente mediante el objeto de resultados de la predicción.

Cada detección contiene información como el identificador de clase, el nivel de confianza y las coordenadas del objeto detectado.

### 6.2.1. Obtención de la clase detectada

```python
for box in res.boxes:

    clase_id = int(box.cls[0])

    confianza = float(box.conf[0])

    nombre_clase = model.names[clase_id]

    print("Clase:", clase_id)
    print("Moneda:", nombre_clase)
    print("Confianza:", confianza)
```

**Descripción de los elementos:**

- `res.boxes`: contiene las detecciones realizadas por YOLO.
- `box.cls[0]`: obtiene el identificador numérico de la clase detectada.
- `box.conf[0]`: obtiene el nivel de confianza de la detección.
- `model.names`: permite consultar el nombre asociado a la clase.

Mediante esta información, el programa puede determinar si la moneda corresponde a una denominación de $50, $100, $200, $500 o $1.000, distinguiendo los diferentes diseños.

### 6.2.2. Correspondencia entre las clases YOLO y el ESP32

Para realizar la clasificación electromecánica, cada clase detectada debe asociarse con una instrucción numérica que el ESP32 pueda interpretar.

La siguiente tabla representa la correspondencia propuesta entre las nueve clases del modelo y las opciones del menú del microcontrolador.

| ID YOLO | Moneda identificada | Código ESP32 | Ángulo |
|:---:|---|:---:|:---:|
| 0 | $50 antigua | 1 | 0° |
| 1 | $50 nueva | 6 | 215° |
| 2 | $100 antigua | 2 | 38° |
| 3 | $100 nueva | 7 | 182° |
| 4 | $200 antigua | 3 | 75° |
| 5 | $200 nueva | 8 | 250° |
| 6 | $500 antigua | 4 | 110° |
| 7 | $500 nueva | 9 | 285° |
| 8 | $1.000 | 10 | 320° |

La correspondencia se debe verificar con los nombres y el orden reales de las clases definidos en el archivo `data.yaml`, así como con la distribución física de los compartimentos.

### 6.2.3. Diccionario de clasificación

```python
clasificacion = {
    0: 1,   # Moneda de $50 antigua
    1: 6,   # Moneda de $50 nueva
    2: 2,   # Moneda de $100 antigua
    3: 7,   # Moneda de $100 nueva
    4: 3,   # Moneda de $200 antigua
    5: 8,   # Moneda de $200 nueva
    6: 4,   # Moneda de $500 antigua
    7: 9,   # Moneda de $500 nueva
    8: 10   # Moneda de $1.000
}
```

Este diccionario relaciona los identificadores de las clases YOLO con las opciones del menú del ESP32.

Cuando se detecta una moneda, el programa consulta su identificador y obtiene el código que debe transmitirse al microcontrolador.

### 6.2.4. Selección automática del caso correspondiente

```python
for box in res.boxes:

    clase_id = int(box.cls[0])
    confianza = float(box.conf[0])

    if confianza >= 0.25:

        if clase_id in clasificacion:

            opcion = clasificacion[clase_id]

            print("Moneda identificada:", model.names[clase_id])
            print("Codigo seleccionado:", opcion)

        else:

            print("Clase no reconocida.")
```

Este fragmento permite seleccionar automáticamente el caso correspondiente a la moneda identificada.

Primero se obtiene el identificador de clase y se verifica que la confianza sea igual o superior al 25 %.

Posteriormente, se consulta el diccionario de clasificación para obtener el código que representa el destino de la moneda.

Si la clase no se encuentra dentro del diccionario, se informa que no fue reconocida.

---

## 6.3. Comunicación serial entre Python y ESP32

La comunicación entre el computador y el microcontrolador se realiza mediante un puerto serial USB.

Python transmite un código numérico que representa la clasificación realizada por YOLO. El ESP32 recibe esta instrucción y ejecuta la secuencia de movimiento correspondiente.

### 6.3.1. Configuración de la comunicación

```python
import serial
import time

esp32 = serial.Serial(
    port='COM3',
    baudrate=115200,
    timeout=1
)

time.sleep(2)
```

**Descripción de los parámetros:**

- `serial.Serial()`: establece la conexión con el ESP32.
- `COM3`: representa el puerto USB asignado al microcontrolador y debe reemplazarse por el correspondiente.
- `baudrate=115200`: establece la velocidad de transmisión.
- `timeout=1`: establece el tiempo máximo de espera para las operaciones de lectura.
- `time.sleep(2)`: permite que el ESP32 termine de inicializarse.

### 6.3.2. Función de transmisión de instrucciones

```python
def enviar_moneda(esp32, opcion):

    comando = f"{opcion}\n"

    esp32.write(comando.encode())

    print("Comando enviado al ESP32:", opcion)
```

Esta función recibe el objeto de conexión serial y el código seleccionado.

Posteriormente, convierte el número en una cadena de texto, lo codifica y lo transmite al microcontrolador.

El ESP32 recibe el número y ejecuta el movimiento correspondiente del motor paso a paso y el servomotor.

### 6.3.3. Secuencia de comunicación

La integración entre los módulos se desarrolla mediante la siguiente secuencia:

1. YOLO detecta una moneda.
2. Python obtiene el identificador de la clase.
3. Se consulta el diccionario de clasificación.
4. Se determina el código asociado a la moneda.
5. Python transmite el código al ESP32.
6. El ESP32 interpreta la instrucción.
7. El motor paso a paso selecciona la posición correspondiente.
8. El servomotor acciona el mecanismo de direccionamiento.

**Consideración de implementación:** la transmisión debe realizarse una sola vez por cada moneda procesada. En una aplicación con cámara en tiempo real es necesario evitar que la misma moneda genere múltiples instrucciones mientras permanece dentro del campo de visión.

---

## 6.4. Módulo de control electromecánico mediante ESP32

Este módulo se encarga de controlar el posicionamiento del mecanismo de selección y el movimiento del servomotor.

Su funcionamiento se basa en recibir una opción numérica, determinar el ángulo correspondiente y ejecutar la secuencia de movimiento.

### 6.4.1. Librerías utilizadas

```cpp
#include <ESP32Servo.h>
#include <Stepper.h>
#include <math.h>
```

**Descripción:**

- `ESP32Servo.h`: permite controlar el servomotor conectado al ESP32.
- `Stepper.h`: proporciona las funciones necesarias para controlar el motor paso a paso.
- `math.h`: permite utilizar funciones matemáticas, como `round()`, para redondear el número de pasos calculado.

### 6.4.2. Configuración de los actuadores

```cpp
const int PASOS_POR_VUELTA = 2048;

Stepper motor(PASOS_POR_VUELTA, 18, 21, 19, 22);

Servo miServo;
const int PIN_SERVO = 12;
```

Se establece una resolución de 2048 pasos por revolución para el motor paso a paso.

Los pines utilizados para su control son:

- GPIO 18.
- GPIO 21.
- GPIO 19.
- GPIO 22.

El servomotor se conecta al GPIO 12.

### 6.4.3. Variables de control

```cpp
int opcion = -1;
int posicionActual = 0;
```

- `opcion`: almacena el código numérico recibido mediante comunicación serial.
- `posicionActual`: registra el ángulo en el que se encuentra el mecanismo de selección.

La posición inicial se establece en 0 grados.

### 6.4.4. Función de accionamiento del servomotor

```cpp
void accionarServo() {

  delay(2000);

  Serial.println("Servo girando a 180 grados");

  miServo.write(180);
  delay(700);

  Serial.println("Servo regresando a 0 grados");

  miServo.write(0);
  delay(700);
}
```

Esta función controla el movimiento del servomotor.

Su funcionamiento es el siguiente:

1. Espera dos segundos para permitir que el mecanismo se estabilice.
2. Envía una posición de 180 grados al servomotor.
3. Espera 700 milisegundos.
4. Regresa el servomotor a 0 grados.
5. Espera nuevamente 700 milisegundos.

De esta manera, el servomotor realiza el movimiento necesario para accionar el mecanismo de direccionamiento.

### 6.4.5. Función de posicionamiento del motor paso a paso

```cpp
void moverAlAngulo(int anguloObjetivo) {

  // Normalizar el angulo objetivo entre 0 y 359
  anguloObjetivo = ((anguloObjetivo % 360) + 360) % 360;

  // Normalizar la posicion actual
  int posicionNormalizada =
      ((posicionActual % 360) + 360) % 360;

  // Calcular diferencia angular
  int diferencia = anguloObjetivo - posicionNormalizada;

  // Buscar el camino mas corto
  if (diferencia > 180) {
    diferencia -= 360;
  }

  if (diferencia < -180) {
    diferencia += 360;
  }

  // Convertir grados a pasos
  long pasos = round(
      (float)diferencia * PASOS_POR_VUELTA / 360.0
  );

  Serial.println("\n--- MOVIMIENTO DEL MOTOR ---");

  Serial.print("Posicion actual: ");
  Serial.println(posicionActual);

  Serial.print("Angulo objetivo: ");
  Serial.println(anguloObjetivo);

  Serial.print("Giro necesario: ");
  Serial.println(diferencia);

  Serial.print("Pasos: ");
  Serial.println(pasos);

  // Ejecutar movimiento
  motor.step(pasos);

  // Actualizar posicion
  posicionActual = anguloObjetivo;

  Serial.println("Motor en posicion.");

  // Accionar el servo
  accionarServo();

  Serial.println("Proceso terminado.");
}
```

Esta función permite posicionar el mecanismo de selección según la moneda identificada.

Su funcionamiento se divide en cinco operaciones:

1. **Normalización angular:** garantiza que el ángulo objetivo se encuentre entre 0° y 359°.
2. **Cálculo de diferencia:** determina cuántos grados debe girar el motor desde su posición actual.
3. **Selección del recorrido:** calcula el desplazamiento angular más corto, evitando giros innecesarios.
4. **Conversión a pasos:** transforma la diferencia angular en el número de pasos que debe ejecutar el motor.
5. **Accionamiento:** mueve el motor paso a paso y, cuando termina, ejecuta la función del servomotor.

La conversión matemática utilizada es:

\[
N=\frac{\Delta\theta \cdot P}{360}
\]

Donde:

- \(N\): cantidad de pasos requeridos.
- \(\Delta\theta\): diferencia angular.
- \(P\): pasos por revolución del motor.

### 6.4.6. Menú de clasificación

```cpp
void mostrarMenu() {

  Serial.println("\n===== MENU DE MONEDAS =====");

  Serial.println("1. Moneda de 50 pesos  - 0 grados");
  Serial.println("2. Moneda de 100 pesos - 38 grados");
  Serial.println("3. Moneda de 200 pesos - 75 grados");
  Serial.println("4. Moneda de 500 pesos - 110 grados");
  Serial.println("5. Moneda de 1000 pesos - 148 grados");
  Serial.println("6. Moneda de 50 pesos  - 215 grados");
  Serial.println("7. Moneda de 100 pesos - 182 grados");
  Serial.println("8. Moneda de 200 pesos - 250 grados");
  Serial.println("9. Moneda de 500 pesos - 285 grados");
  Serial.println("10. Moneda de 1000 pesos - 320 grados");

  Serial.println("0. Salir");
  Serial.println("Selecciona una opcion:");
}
```

Esta función muestra las opciones disponibles para seleccionar las posiciones del mecanismo.

Cada opción tiene asociado un ángulo específico que determina el destino de clasificación.

### 6.4.7. Configuración inicial: setup()

```cpp
void setup() {

  Serial.begin(115200);

  // Configurar velocidad del motor
  motor.setSpeed(10);

  // Configurar servo
  miServo.setPeriodHertz(50);
  miServo.attach(PIN_SERVO, 500, 2400);

  // Posicion inicial del servo
  miServo.write(0);
  delay(500);

  Serial.println("Sistema de clasificacion de monedas iniciado.");

  Serial.println("Posicion inicial del motor asumida: 0 grados.");

  mostrarMenu();
}
```

En esta sección se configuran los componentes del sistema:

- Se inicia la comunicación serial a 115200 baudios.
- Se establece una velocidad de 10 RPM para el motor paso a paso.
- Se configura la frecuencia del servomotor en 50 Hz.
- Se establece el rango de pulsos de control del servomotor.
- Se posiciona inicialmente el servomotor en 0 grados.
- Se muestra el menú de selección.

### 6.4.8. Bucle principal: loop()

```cpp
void loop() {

  // Esperar una opcion del usuario
  while (Serial.available() == 0) {
    // Esperando entrada
  }

  opcion = Serial.parseInt();

  // Limpiar caracteres pendientes
  while (Serial.available() > 0) {
    Serial.read();
  }

  // Seleccionar la moneda
  switch (opcion) {

    case 1:
      moverAlAngulo(0);
      break;

    case 2:
      moverAlAngulo(38);
      break;

    case 3:
      moverAlAngulo(75);
      break;

    case 4:
      moverAlAngulo(110);
      break;

    case 5:
      moverAlAngulo(148);
      break;

    case 6:
      moverAlAngulo(215);
      break;

    case 7:
      moverAlAngulo(182);
      break;

    case 8:
      moverAlAngulo(250);
      break;

    case 9:
      moverAlAngulo(285);
      break;

    case 10:
      moverAlAngulo(320);
      break;

    case 0:
      Serial.println("Programa finalizado.");

      miServo.detach();

      while (true) {
        // Sistema detenido
      }

      break;

    default:
      Serial.println("Opcion no valida.");
      break;
  }

  mostrarMenu();
}
```

El bucle principal mantiene el sistema esperando instrucciones.

Cuando recibe un dato mediante el puerto serial, utiliza `Serial.parseInt()` para convertirlo en un número entero.

Posteriormente, el bloque `switch-case` identifica la opción recibida y ejecuta la función `moverAlAngulo()` con el ángulo correspondiente.

Si se recibe una opción inválida, el programa informa el error y vuelve a mostrar el menú.

La opción 0 detiene el funcionamiento del programa y desactiva la señal del servomotor.

---

## 7. Estructura del proyecto

La siguiente estructura representa una organización recomendada para los archivos del repositorio:

```text
Clasificador-Monedas-Colombianas/
│
├── Python/
│   ├── main.py
│   ├── detector.py
│   ├── comunicacion_serial.py
│   └── configuracion.py
│
├── ESP32/
│   └── clasificador_monedas.ino
│
├── modelo/
│   └── best.pt
│
├── dataset/
│   ├── images/
│   └── labels/
│
├── evidencias/
│   ├── prototipo.jpg
│   ├── sistema_mecanico.jpg
│   └── pruebas.jpg
│
├── README.md
└── requirements.txt
```

Los nombres de los archivos pueden ajustarse a la organización real del repositorio.

## 8. Instalación y configuración

### 8.1. Requisitos del sistema

Para ejecutar el módulo de visión artificial se requiere:

- Python.
- Visual Studio Code.
- Cámara conectada al computador.
- Modelo YOLO entrenado.
- Microcontrolador ESP32.
- Arduino IDE.

### 8.2. Creación del entorno virtual

Se recomienda crear un entorno virtual para administrar las dependencias del proyecto.

```powershell
python -m venv venv
```

Activación del entorno virtual en Windows:

```powershell
.\venv\Scripts\Activate.ps1
```

### 8.3. Instalación de dependencias

```powershell
pip install ultralytics opencv-python pyserial
```

Estas bibliotecas permiten ejecutar el modelo YOLO, procesar imágenes y establecer la comunicación serial.

### 8.4. Configuración del ESP32

Para programar el microcontrolador se deben instalar las bibliotecas correspondientes desde el administrador de bibliotecas de Arduino IDE:

- ESP32Servo.
- Stepper.

Posteriormente, se debe seleccionar la placa ESP32 correspondiente y configurar el puerto de comunicación USB.

## 9. Ejecución del sistema

### 9.1. Detección mediante cámara web

Desde la terminal de Visual Studio Code, ejecutar:

```powershell
python main.py webcam
```

Este comando inicia la cámara y permite visualizar las detecciones realizadas por YOLO en tiempo real.

Para cerrar la ventana se debe presionar la tecla `q`.

### 9.2. Detección mediante una imagen

```powershell
python main.py "ruta_de_la_imagen.jpg"
```

Este comando procesa una imagen específica y guarda el resultado de la detección en la carpeta correspondiente.

### 9.3. Comunicación con el ESP32

Una vez establecida la conexión serial, Python transmite el código de clasificación correspondiente a la moneda identificada.

El microcontrolador interpreta la instrucción y ejecuta los movimientos necesarios para realizar la clasificación física.

---

## 10. Resultados obtenidos

Se obtuvo un prototipo funcional capaz de procesar monedas individualmente mediante visión artificial, identificar su denominación y diseño, transmitir la clasificación al microcontrolador y accionar los mecanismos electromecánicos para dirigir cada moneda hacia su compartimento correspondiente.

La integración entre Python, YOLO y ESP32 permitió desarrollar un proceso de clasificación automatizado, reduciendo la intervención manual y demostrando la aplicación de técnicas de inteligencia artificial y control electromecánico en un sistema físico.

El desarrollo permitió integrar conocimientos de programación, procesamiento digital de imágenes, sistemas embebidos, electrónica y diseño mecánico en una aplicación de automatización.

## 11. Posibles mejoras

Como líneas de desarrollo futuro se plantean las siguientes mejoras:

- Optimizar el modelo YOLO para incrementar la precisión de clasificación.
- Implementar mecanismos de detección de monedas superpuestas o mal posicionadas.
- Incorporar sensores para verificar el desplazamiento de cada moneda.
- Implementar retroalimentación de posición del mecanismo.
- Desarrollar un contador automático de monedas por denominación.
- Incorporar una interfaz gráfica para visualizar los resultados de clasificación.
- Optimizar los tiempos de respuesta entre la identificación y el accionamiento mecánico.
- Implementar un sistema de calibración automática de la posición inicial del motor.

## 12. Información del proyecto

**Institución:** Universidad Militar Nueva Granada (UMNG).

**Programa académico:** Ingeniería en Mecatrónica.

**Área de desarrollo:**

- Visión artificial e inteligencia artificial.
- Detección de objetos mediante YOLO.
- Procesamiento digital de imágenes.
- Programación en Python.
- Sistemas embebidos.
- Control electromecánico.
- Automatización.

---

**Sistema Automatizado de Clasificación de Monedas Colombianas**

*Integración de visión artificial, electrónica y mecánica para la automatización de procesos de clasificación.*