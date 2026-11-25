<div align="center">

# 🪙 Sistema Automatizado de Clasificación de Monedas Colombianas

### *Visión artificial · YOLO · Python · ESP32 · Electromecánica · IA conversacional*

**Universidad Militar Nueva Granada — Ingeniería en Mecatrónica**
Quinto semestre · 2026

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge)
![YOLOv8](https://img.shields.io/badge/YOLO-v8n-orange?style=for-the-badge)
![ESP32](https://img.shields.io/badge/ESP32-WROOM-blueviolet?style=for-the-badge)
![OpenCV](https://img.shields.io/badge/OpenCV-4.x-green?style=for-the-badge)
![Estado](https://img.shields.io/badge/Estado-Funcional-brightgreen?style=for-the-badge)

---

*"Percepción → decisión → actuación → explicación"*

</div>

---

## 📑 Tabla de contenidos

1. [Descripción general](#1-descripción-general)
   - [1.1. Contexto y problemática](#11-contexto-y-problemática)
   - [1.2. Justificación](#12-justificación)
   - [1.3. Alcance y limitaciones](#13-alcance-y-limitaciones)
2. [Objetivos e hipótesis](#2-objetivos-e-hipótesis)
3. [Marco teórico](#3-marco-teórico)
   - [3.1. Visión artificial](#31-visión-artificial)
   - [3.2. Detección vs. clasificación](#32-detección-vs-clasificación)
   - [3.3. YOLO y YOLOv8n](#33-yolo-y-yolov8n)
   - [3.4. IoU, NMS y mAP](#34-iou-nms-y-map)
   - [3.5. Comunicación serial](#35-comunicación-serial)
   - [3.6. Motores paso a paso](#36-motores-paso-a-paso)
   - [3.7. Servomotores](#37-servomotores)
   - [3.8. ESP32](#38-esp32)
   - [3.9. Carros oruga y motores de 12 V](#39-carros-oruga-y-motores-de-12-v)
   - [3.10. Asistentes conversacionales de IA](#310-asistentes-conversacionales-de-ia)
4. [Arquitectura del sistema](#4-arquitectura-del-sistema)
5. [Clasificaciones reconocidas](#5-clasificaciones-reconocidas)
6. [Componentes del prototipo](#6-componentes-del-prototipo)
   - [6.1. Lista de materiales](#61-lista-de-materiales)
   - [6.2. ESP32 y actuadores](#62-esp32-y-actuadores)
   - [6.3. Banda transportadora](#63-banda-transportadora)
   - [6.4. Carro oruga con motores de 12 V](#64-carro-oruga-con-motores-de-12-v)
   - [6.5. JArvis: asistente de inteligencia artificial](#65-jarvis-asistente-de-inteligencia-artificial)
7. [Software y estructura del proyecto](#7-software-y-estructura-del-proyecto)
8. [Dataset y entrenamiento](#8-dataset-y-entrenamiento)
9. [Resultados y análisis](#9-resultados-y-análisis)
10. [Instalación y configuración](#10-instalación-y-configuración)
11. [Guía de uso](#11-guía-de-uso)
    - [11.9. Dashboard web](#119-dashboard-web)
12. [Protocolo de integración con el ESP32](#12-protocolo-de-integración-con-el-esp32)
13. [Estructura de carpetas](#13-estructura-de-carpetas)
14. [Solución de problemas y FAQ](#14-solución-de-problemas-y-faq)
15. [Mejoras futuras](#15-mejoras-futuras)
16. [Glosario](#16-glosario)
17. [Referencias](#17-referencias)
18. [Créditos](#18-créditos)

---

## 1. Descripción general

### 1.1. Contexto y problemática

La clasificación manual de monedas es una tarea repetitiva, lenta y propensa a errores, especialmente cuando existen **varias denominaciones con diseños visualmente similares**. En el contexto colombiano conviven monedas de $50, $100, $200, $500 y $1.000, varias de ellas con versiones *antigua* y *nueva* que comparten color, tamaño aproximado y motivos decorativos.

Un sistema automático que identifique la moneda y la dirija a un compartimento permite:

- Reducir el tiempo de conteo y separación.
- Eliminar la fatiga del operador.
- Garantizar trazabilidad de cada moneda procesada.
- Servir como plataforma de enseñanza para integrar visión artificial, electrónica y mecánica.

El reto principal no fue únicamente "detectar una moneda", sino **reconocerla en las condiciones reales del montaje**: ángulo de cámara, sombras, placa metálica de fondo, brazo mecánico y una iluminación distinta a la de un estudio fotográfico.

### 1.2. Justificación

El proyecto integra cuatro áreas que normalmente se abordan por separado:

1. **Visión artificial:** detección de objetos con redes neuronales convolucionales.
2. **Programación:** adquisición de imágenes, lógica de decisión y comunicación.
3. **Electrónica y sistemas embebidos:** ESP32, motores y servomotores.
4. **Mecánica:** banda transportadora, rampa, mecanismo de direccionamiento y plataforma oruga.

Además, se incorpora una capa de interacción mediante **JArvis**, un asistente de inteligencia artificial que comunica verbalmente el funcionamiento del sistema, cerrando el ciclo entre la ejecución física y la explicación del conocimiento.

### 1.3. Alcance y limitaciones

**Dentro del alcance**

- Clasificación de nueve clases de monedas colombianas.
- Detección en tiempo real con cámara USB o de celular.
- Comunicación serial con un ESP32.
- Posicionamiento angular y accionamiento de servo.
- Entrenamiento y ajuste con datos reales del montaje.
- Asistente conversacional que explica el proyecto.

**Fuera del alcance / limitaciones conocidas**

- No se validó el sistema con monedas superpuestas de forma severa.
- El modelo se entrenó sobre una iluminación específica; cambios fuertes de luz pueden degradar el resultado.
- El mecanismo asume que el motor inicia en 0° (sin sensor *home*).
- La comunicación serial no implementa *handshake* de confirmación.
- El carro oruga se trata como plataforma complementaria, no como sistema de navegación autónoma.

---

## 2. Objetivos e hipótesis

### 2.1. Objetivo general

Desarrollar un sistema automatizado para la clasificación de monedas colombianas que integre visión artificial con YOLO, programación en Python y control electromecánico mediante ESP32, distinguiendo denominaciones y diseños para dirigir cada moneda a su compartimento correspondiente.

### 2.2. Objetivos específicos

1. Implementar un modelo de detección de objetos YOLO entrenado para nueve clases de monedas.
2. Desarrollar un programa en Python para capturar, procesar y analizar imágenes con OpenCV.
3. Establecer la correspondencia entre las clases detectadas y las instrucciones del ESP32.
4. Implementar la comunicación serial USB entre computador y microcontrolador.
5. Desarrollar el posicionamiento mediante motor paso a paso y servomotor.
6. Integrar los componentes electrónicos y mecánicos en un prototipo funcional.
7. Generar un dataset propio a partir del montaje real y reentrenar el modelo.
8. Documentar el sistema mediante README técnico y asistente conversacional JArvis.

### 2.3. Hipótesis

> Si se entrena un modelo YOLO con imágenes capturadas en el mismo entorno físico donde operará, entonces la precisión de clasificación mejora significativamente frente a un modelo entrenado únicamente con imágenes de estudio o imágenes sintéticas.

La hipótesis se confirmó experimentalmente: el modelo inicial entrenado con datos sintéticos fallaba por completo en el montaje, mientras que el modelo ajustado con 129 capturas reales alcanzó **98 % de acierto**.

### 2.4. Aportes

- Reproducibilidad: todos los scripts calculan sus rutas automáticamente.
- Trazabilidad: cada etapa del entrenamiento tiene su script y su dataset asociado.
- Robustez: envío serial con una sola instrucción por moneda.
- Documentación viva: JArvis convierte el README en una explicación conversacional.

---

## 3. Marco teórico

### 3.1. Visión artificial

La visión artificial es la rama de la inteligencia artificial que permite a las máquinas interpretar información visual. En este proyecto, la cámara entrega una imagen en formato BGR (OpenCV) y el modelo YOLO produce:

- **Clase:** qué tipo de moneda aparece.
- **Confianza:** qué tão seguro está el modelo.
- **Caja delimitadora:** dónde está la moneda dentro de la imagen.

Un píxel por sí solo no tiene significado; el modelo aprende patrones jerárquicos: bordes → texturas → formas → números y símbolos → moneda completa.

### 3.2. Detección vs. clasificación

| Tarea | Entrada | Salida | Ejemplo |
|---|---|---|---|
| Clasificación | Imagen completa | Una etiqueta | "Esta imagen es un $100" |
| Detección | Imagen completa | Varias cajas + etiquetas | "Hay dos monedas: $100 y $50" |

El proyecto usa **detección** porque la moneda puede aparecer en distintas posiciones dentro del campo de visión. YOLO es un detector de una sola etapa (*one-stage*): en una sola pasada predice cajas y clases, lo que lo hace rápido enough para tiempo real en CPU.

> El plan B planteado durante el desarrollo consistía en recortar la moneda y clasificar solo ese recorte. Se descartó porque el equilibrio del dataset solventó el problema sin cambiar la arquitectura.

### 3.3. YOLO y YOLOv8n

**YOLO** (*You Only Look Once*) divide la imagen en una rejilla y predice, para cada celda, cajas y probabilidades de clase. Sus versiones evolucionaron desde YOLOv1 hasta la familia YOLOv8 de Ultralytics.

**YOLOv8n** es la variante *nano*:

- Menor número de parámetros (~3 M).
- Adecuada para CPU.
- Arquitectura *anchor-free*.
- Entrenamiento sencillo mediante la API `YOLO(...).train(...)`.

Estructura general:

```text
Imagen 640x480
   │
   ▼
Backbone (CSPDarknet)     → extrae características
   │
   ▼
Neck (PAN-FPN)            → fusiona escalas
   │
   ▼
Head (detect)             → cajas + clases
   │
   ▼
Postproceso (NMS)         → cajas finales
```

### 3.4. IoU, NMS y mAP

- **IoU (Intersection over Union):** mide qué tanto se traslapan la caja predicha y la real. `IoU = intersección / unión`.
- **NMS (Non-Maximum Suppression):** elimina cajas duplicadas que apuntan al mismo objeto. En este proyecto se usa además `max_det=1` en la cámara, porque solo se lee una moneda a la vez.
- **mAP (mean Average Precision):** métrica principal de los detectores. `mAP50` usa IoU ≥ 0.50 y `mAP50-95` promedia umbrales de 0.50 a 0.95.

Resultados del modelo final: **mAP50 = 0.899**, **mAP50-95 = 0.854**.

### 3.5. Comunicación serial

La comunicación serial envía bytes uno detrás de otro por un cable USB. Los parámetros deben coincidir en ambos extremos:

| Parámetro | Valor |
|---|---|
| Puerto | COM8 (separador) |
| Velocidad | 115200 baudios |
| Formato | Texto ASCII + salto de línea (`\n`) |
| Timeout | 1 s |

Python envía `f"{codigo}\n".encode()` y el ESP32 usa `Serial.parseInt()` para recuperar el número.

### 3.6. Motores paso a paso

Un motor paso a paso convierte pulsos eléctricos en movimiento angular discreto. El utilizado tiene **2048 pasos por vuelta** (~0.176° por paso).

Ventajas:

- Posicionamiento reproducible sin encoder.
- Par de retención al estar detenido.
- Control abierto sencillo.

La conversión usada en el firmware es:

```text
N = round(Δθ · 2048 / 360)
```

Además se busca el **camino angular más corto**: si la diferencia supera 180°, se ajusta restando o sumando 360°.

### 3.7. Servomotores

Un servomotorRC no gira libremente: recibe un tren de pulsos PWM a **50 Hz**, donde el ancho de pulso define el ángulo.

| Pulso | Ángulo aproximado |
|---|:--:|
| 500 µs | 0° |
| 1500 µs | 90° |
| 2400 µs | 180° |

En el proyecto el servo se conecta al GPIO 12, con `setPeriodHertz(50)` y `attach(PIN_SERVO, 500, 2400)`. La secuencia es: esperar estabilización → girar a 180° → retornar a 0°.

### 3.8. ESP32

El ESP32 es un microcontrolador con WiFi y Bluetooth integrados. En este proyecto cumple tres funciones:

1. Recibir códigos por USB.
2. Interpretarlos en un `switch-case`.
3. Accionar motor paso a paso y servo.

Sus GPIO empleados:

| GPIO | Función |
|---|---|
| 18, 21, 19, 22 | Motor paso a paso |
| 12 | Servomotor |

### 3.9. Carros oruga y motores de 12 V

Un carro oruga sustituye las ruedas por cintas continuas. Frente a un vehículo de ruedas ofrece:

- Mayor contacto con el suelo y mejor tracción.
- Capacidad de sortear irregularidades.
- Giro en el sitio mediante **dirección diferencial**.

**Dirección diferencial:** si la oruga izquierda gira más rápido que la derecha, el vehículo gira hacia la derecha; si ambas giran igual, avanza recto.

**Motores de 12 V con reductora:** entregan mayor par a baja velocidad. Se controlan con un **puente H**, circuito que invierte la polaridad para cambiar el sentido de giro y usa PWM para regular la velocidad.

**Alimentación:** los motores de 12 V requieren una fuente externa separada de la lógica de 3,3 V del ESP32, compartiendo únicamente la masa (GND). Esto evita que los picos de corriente de los motores reinicien el microcontrolador.

En el ecosistema de este proyecto, el carro oruga es la **plataforma móvil complementaria** donde puede montarse el clasificador, aportando movilidad al conjunto.

### 3.10. Asistentes conversacionales de IA

Un asistente conversacional combina:

- **Comprensión de lenguaje natural** para interpretar preguntas.
- **Base de conocimiento** del dominio (en este caso, el proyecto).
- **Generación de lenguaje** para producir respuestas.
- Opcionalmente **voz** (STT para escuchar y TTS para hablar).

**JArvis** aplica estas ideas para explicar el sistema: convierte la documentación técnica en una conversación, de modo que un evaluador pueda preguntar, por ejemplo, *"¿por qué se reentrenó el modelo?"* y recibir una respuesta contextualizada sobre el dataset real y los resultados.

---

## 4. Arquitectura del sistema

```text
        ┌──────────────────────────────────────────────┐
        │              CAPA DE PERCEPCIÓN              │
        │ Banda transportadora → inspección → cámara      │
        └───────────────────┬──────────────────────────┘
                            │ frame BGR
        ┌───────────────────▼──────────────────────────┐
        │              CAPA DE DECISIÓN                │
        │  YOLOv8n (416 px, conf 0.25, max_det=1)      │
        │  → class_id → mapeo_esp32.py → código        │
        │  → lógica de "una instrucción por moneda"    │
        └───────────────────┬──────────────────────────┘
                            │ "N\n" @ 115200 baud
        ┌───────────────────▼──────────────────────────┐
        │              CAPA DE ACTUACIÓN               │
        │  ESP32 → Stepper (GPIO 18/21/19/22)          │
        │        → Servo (GPIO 12) → compartimento     │
        └───────────────────┬──────────────────────────┘
                            │
        ┌───────────────────▼──────────────────────────┐
        │           CAPA DE EXPLICACIÓN                │
        │  JArvis: asistente que describe el proceso   │
        └──────────────────────────────────────────────┘
```

### 4.1. Estados de una moneda

| Estado | Condición | Acción |
|---|---|---|
| Espera | Sin detección | — |
| Candidato | Detección estable < 3 frames | Acumular frames |
| Enviado | 3 frames estables | Enviar código una vez |
| En zona | Misma clase en pantalla | No reenviar |
| Retirada | 5 frames sin detección | Liberar siguiente envío |

Este modelo de estados evita el problema clásico de enviar varias órdenes para una misma moneda.

---

## 5. Clasificaciones reconocidas

El modelo reconoce **9 clases** (denominación + diseño). El orden corresponde al exportado por Roboflow y al archivo `dataset_9clases/data.yaml`.

| ID | Moneda | Diseño | Código ESP32 | Ángulo |
|:--:|---|---|:--:|:--:|
| 0 | $1.000 | Única | 10 | 320° |
| 1 | $100 | Antigua | 2 | 38° |
| 2 | $100 | Nueva | 7 | 182° |
| 3 | $200 | Antigua | 3 | 75° |
| 4 | $200 | Nueva | 8 | 250° |
| 5 | $500 | Antigua | 4 | 110° |
| 6 | $500 | Nueva | 9 | 285° |
| 7 | $50 | Antigua | 1 | 0° |
| 8 | $50 | Nueva | 6 | 215° |

### 5.1. Criterios de distinción

Las monedas antiguas y nuevas de una misma denominación pueden diferir en:

- El **motivo central** (retrato, animal, escudo).
- El **tipo de relieve** y el patrón del borde.
- El **color** y el acabado del metal.
- La **distribución de inscripciones**.

En las fotos del montaje, estas diferencias son sutiles: por ejemplo, la cara del loro en $200 nueva y la cara del oso en $50 nueva. Por eso fue necesario entrenar con imágenes tomadas exactamente desde la cámara de operación.

### 5.2. Correspondencia con el menú del ESP32

El firmware del ESP32 organiza las opciones 1 a 10. El código 5 (148°) queda disponible para una posición adicional, mientras las nueve clases ocupan los códigos restantes. La tabla anterior es la fuente de verdad y está implementada en `scripts/mapeo_esp32.py`.

---

## 6. Componentes del prototipo

### 6.1. Lista de materiales

| Cantidad | Elemento | Función |
|:--:|---|---|
| 1 | ESP32 | Control del sistema |
| 1 | Motor paso a paso 28BYJ-48 (2048 pasos) | Posicionamiento angular |
| 1 | Servomotor 180° | Direccionamiento de la moneda |
| 1 | Cámara USB / celular con DroidCam | Captura de imágenes |
| 1 | PC con Python | Inferencia y decisión |
| 1 | Cable USB | Comunicación serial y alimentación del ESP32 |
| 1 | Banda transportadora | Alimentación de monedas hacia la zona de inspección |
| 2 | Rampa y mecanismo impresos | Guía y selección de monedas |
| 3 | Motores DC 12 V con reductora | Tracción del carro oruga |
| 1 | Puente H | Control de motores de 12 V |
| 1 | Fuente 12 V | Alimentación de motores |
| 1 | Batería / regulador 5 V | Alimentación lógica |

### 6.2. ESP32 y actuadores

| Elemento | Configuración |
|---|---|
| Microcontrolador | ESP32 |
| Comunicación serial | USB, 115200 baudios, `timeout=1` |
| Motor paso a paso | 2048 pasos/vuelta, 10 RPM, GPIO 18, 21, 19, 22 |
| Servomotor | GPIO 12, 50 Hz, pulso 500–2400 µs |
| Posición inicial | Motor asumida en 0°, servo en 0° |
| Posicionamiento | **Absoluto y fijo** (sin módulo ni camino más corto) |
| Ángulos | Configurables y guardados en EEPROM |
| Secuencia | Motor → servo 180° → servo 0° → banda continúa |

**Movimiento absoluto**

La opción 1 siempre vuelve exactamente a **0°**; la opción 2 va a su ángulo fijo, y así sucesivamente. No se usa normalización angular:

```cpp
anguloObjetivo = constrain(anguloObjetivo, 0, 359);
int diferencia = anguloObjetivo - posicionActual;   // directa, sin modulo
long pasos = round((float)diferencia * PASOS_POR_VUELTA / 360.0);
motor.step(pasos);
posicionActual = anguloObjetivo;
accionarServo();
```

**Ajuste manual de ángulos**

Desde el Monitor Serie (115200 baudios) o enviando comandos por Python:

| Comando | Acción |
|---|---|
| `1`–`10` | Casos que envía YOLO → mueve al ángulo fijo de la moneda |
| ángulo `0`–`360` | Mueve el motor a ese ángulo (ej. `180`) |
| `Z` | **Registrar cero**: la posición física actual pasa a ser 0° |
| `Z+` / `Z-` | Ajuste fino del cero, 1° por pulso |
| `ZZ` | Muestra el cero y la posición actual |
| `B` | Enciende/apaga la banda manualmente |
| `P,<angulo>` | Fija la posición inicial **sin mover el motor** (ej. `P,30`) |

Con `P,<angulo>` le dices al ESP32 en qué ángulo está físicamente el eje ahora, sin que se mueva. Desde ahí, los casos del YOLO calculan el giro correcto hacia cada posición fija.

La banda arranca **apagada**. Cuando YOLO envía un caso (1–10), el ESP32:

1. Mueve el **motor paso a paso** al ángulo fijo de la moneda.
2. Mueve el **servo** del mecanismo (90° → 0°).
3. **Enciende la banda de inmediato** y, usando `millis()` sin bloquear el `loop()`, la **apaga automáticamente a los 10 s**.

El comando `B` permite forzar el encendido o apagado manual.
Los ángulos de las monedas son fijos: 1=0°, 2=38°, 3=75°, 4=110°, 5=148°, 6=215°, 7=182°, 8=250°, 9=285°, 10=320°. El movimiento usa el camino más corto sobre 2048 pasos/vuelta y permite giro en ambos sentidos. El ajuste del cero se hace con `Z` / `Z+` / `Z-` y se mantiene mientras el ESP32 esté encendido.

### 6.3. Banda transportadora

El sistema de alimentación de monedas incluye una **banda transportadora** como primer elemento del recorrido. Las monedas se depositan sobre la cinta y son desplazadas hacia la **zona de inspección**, donde se detienen brevemente para permitir la captura de la imagen con la cámara.

**Función en el ciclo de clasificación**

```text
Depósito de monedas → Banda transportadora → Zona de inspección → YOLO → ESP32 → Compartimento
```

| Característica | Descripción |
|---|---|
| Función | Transporte y alimentación individual de monedas |
| Accionamiento | Motor eléctrico de corriente continua |
| Control desde el ESP32 | **Movimiento continuo** en GPIO 13 (`PIN_BANDA`): se enciende en `setup()` y permanece activa |
| Comando manual | Opción 11 del menú (o enviar `11\n`) alterna ON/OFF; opción 0 la apaga |
| Velocidad | Reducida, para que la moneda se detenga en la zona de lectura |
| Sincronía | La captura debe ocurrir con la moneda detenida para evitar desenfoque |
| Relación con el software | El detector usa `max_det=1` porque la banda presenta una moneda a la vez |
| Relación con el carro | Es un subsistema distinto al carro oruga: la banda alimenta el clasificador y el carro aporta movilidad al conjunto |

La banda transportadora resuelve el problema de la **alimentación constante**: mantiene el flujo de monedas hacia la cámara sin intervención manual, mientras el mecanismo de selección dirige cada pieza ya identificada a su compartimento.

### 6.4. Carro oruga con motores de 12 V

Como **plataforma móvil complementaria** del ecosistema del proyecto se desarrolló un carro oruga accionado por motores de 12 V. Su tracción por cintas continuas permite desplazarse sobre superficies irregulares con buena estabilidad y constituye la base mecánica sobre la cual puede montarse el prototipo de clasificación para darle movilidad.

**Características**

- **Tracción:** dos motores de corriente continua de 12 V con reductora, uno por oruga.
- **Control:** accionamiento mediante puente H, compatible con señales digitales y PWM del ESP32.
- **Alimentación:** fuente externa de 12 V independiente de la lógica de 3,3 V.
- **Dirección:** giro diferencial (velocidades distintas entre oruga izquierda y derecha).
- **Chasis:** estructura rígida con soportes para ruedas dentadas y cintas.
- **Integración:** el mismo ESP32 que gestiona los actuadores del clasificador puede comandar la plataforma, reutilizando el protocolo serial.

**Esquema conceptual de control**

```text
   ESP32 GPIO (PWM) ──► Puente H ──► Motor 12 V ──► Oruga izquierda
   ESP32 GPIO (PWM) ──► Puente H ──► Motor 12 V ──► Oruga derecha
                    Fuente 12 V ─────────┘
                    GND compartido con ESP32
```

**Ventajas del enfoque oruga**

1. Mejor tracción en superficies lisas o con polvo.
2. Giro en el sitio sin necesidad de radio de giro amplio.
3. Distribución del peso sobre mayor área.
4. Posibilidad de transportar el mecanismo clasificador completo.

**Código del carro**

El firmware independiente está en `CarroOruga/CarroOruga.ino` y el puente con el mando en `scripts/mando_xbox.py`.

| Elemento | Implementación |
|---|---|
| Puente H | 4 pines de dirección + 2 canales PWM (`ledc`) |
| HC-SR04 | 3 lecturas y filtrado por mediana, cada 60 ms |
| Evasión | Máquina de estados: avanzar → retroceder → girar |
| Manual | Bloqueo de avance si hay obstáculo a < 12 cm |
| Seguridad | *Watchdog*: si no llegan comandos en 1500 ms, se detiene |
| Telemetría | `T,<dist>,<modo>,<izq>,<der>` cada 500 ms |

**Protocolo serial del carro**

| Comando | Significado |
|---|---|
| `M,<izq>,<der>\n` | Velocidades de -255 a 255 |
| `A\n` | Alternar modo automático / manual |
| `S\n` | Detener |
| `D\n` | Consultar distancia del HC-SR04 |
| `T\n` | Consultar estado |

**Controles del mando Xbox 360 (con cable)**

| Control | Acción |
|---|---|
| Stick izquierdo | Avance y giro diferencial |
| A | Activar/desactivar evasión automática |
| B | Detener |
| X | Consultar distancia |
| Y | Consultar estado |
| Ctrl+C | Salir |

> El mando se conecta a la PC, no al ESP32. Python lee XInput con la librería `inputs` y reenvía las órdenes por USB, reutilizando el mismo enlace serial del proyecto.

### 6.5. JArvis: asistente de inteligencia artificial

**JArvis** es una inteligencia artificial conversacional desarrollada por el equipo con el propósito de **explicar el proyecto de forma natural**. Actúa como guía del sistema: describe el problema, el flujo de clasificación, el papel de YOLO y del ESP32, las clases reconocidas y los resultados obtenidos, y responde preguntas sobre cualquier parte del prototipo.

**Objetivos de JArvis**

- Convertir la documentación técnica en una experiencia conversacional.
- Apoyar la demostración y la defensa oral del proyecto.
- Permitir consultas rápidas sobre arquitectura, dataset, resultados y hardware.

**Temas que conoce**

| Tema | Ejemplo de consulta |
|---|---|
| Arquitectura | "¿Cómo funciona el sistema?" |
| Dataset | "¿Cuántas monedas reales se capturaron?" |
| Entrenamiento | "¿Por qué se reentrenó el modelo?" |
| ESP32 | "¿Qué ángulo corresponde al código 8?" |
| Resultados | "¿Cuál fue la precisión final?" |
| Hardware | "¿Qué motores usa el carro oruga?" |

**Valor añadido**

JArvis complementa la interfaz de visión y control, cerrando el ciclo entre *percepción → decisión → actuación → explicación*. Mientras el clasificador actúa físicamente, el asistente comunica qué está ocurriendo y por qué.

---

## 7. Software y estructura del proyecto

### 7.1. Flujo de trabajo completo

```text
   1. Roboflow (126 img)
          │
          ▼
   preparar_dataset_9clases.py
          │
          ▼
   dataset_9clases ──► 02_train.py ──► runs/monedas_9clases
          │
          ▼
   capturar_dataset.py  (cámara real, teclas 1-9)
          │
          ▼
   etiquetar_reposicion.py  (Hough → cajas YOLO)
          │
          ▼
   combinar_datasets.py ──► dataset_final (255 img)
          │
          ▼
   equilibrar_dataset.py ──► dataset_balanceado
          │
          ▼
   05_afinar_real.py ──► runs/monedas_balanceado
          │
          ▼
   06_reentrenar_balanceado.py ──► runs/monedas_balanceado_v2 (FINAL)
          │
          ▼
   integrar_esp32.py ──► serial ──► ESP32 ──► motor + servo
```

### 7.2. Descripción de scripts

| Script | Propósito | Entrada | Salida |
|---|---|---|---|
| `preparar_dataset_9clases.py` | Convierte polígonos a cajas | Roboflow ZIP | `dataset_9clases` |
| `01_generate_synthetic.py` | Genera imágenes sintéticas (histórico) | — | `data/` |
| `02_train.py` | Entrenamiento base | `dataset_9clases` | `runs/monedas_9clases` |
| `capturar_dataset.py` | Captura real etiquetada por tecla | Cámara | `dataset_reposicion/images/<clase>` |
| `etiquetar_reposicion.py` | Cajas automáticas con Hough | Capturas | `dataset_reposicion/labels/<clase>` |
| `combinar_datasets.py` | Une Roboflow + reales | Ambos datasets | `dataset_final` |
| `equilibrar_dataset.py` | Duplica clases minoritarias | `dataset_final` | `dataset_balanceado` |
| `05_afinar_real.py` | Primer ajuste | `dataset_final` | `runs/monedas_balanceado` |
| `06_reentrenar_balanceado.py` | Modelo final | `dataset_balanceado` | `runs/monedas_balanceado_v2` |
| `03_infer.py` | Inferencia con salida textual | Imagen | Consola + resultado guardado |
| `04_demo.py` | Demo visual | Imagen/cámara/URL | Imagen anotada / ventana |
| `probar_camara.py` | Detecta cámaras disponibles | — | Índices y foto de prueba |
| `mapeo_esp32.py` | Tabla de correspondencia | — | Diccionarios Python |
| `integrar_esp32.py` | Integración completa | Cámara + puerto | Códigos por serial |
| `diagnostico_monedas.py` | Exploración con confianza baja | Cámara | Ventana + fotos nuevas |
| `mando_xbox.py` | Control del carro con mando Xbox 360 | Mando + serial | Comandos `M,<izq>,<der>` |
| `verificar_v2.py` | Comparación de modelos | Modelos + fotos | Métricas por clase |

### 7.3. Dependencias

```text
ultralytics   → modelo YOLO y entrenamiento
opencv-python → captura y dibujo de imágenes
pyserial      → comunicación con ESP32
inputs        → lectura del mando Xbox 360 por XInput
pillow        → generación sintética (histórico)
numpy         → operaciones sobre imágenes
```

---

## 8. Dataset y entrenamiento

### 8.1. Origen de los datos

El dataset original proviene de Roboflow (`My First Project.v1i.yolov8`), con **126 imágenes** y **231 polígonos de segmentación** en 9 clases. Las etiquetas de segmentación se convirtieron a cajas delimitadoras calculando el mínimo y máximo de las coordenadas del polígono.

### 8.2. Capturas del montaje real

Se tomó un segundo conjunto con la cámara USB en la posición definitiva:

| Lote | Imágenes | Clases añadidas |
|---|:--:|---|
| Primero | 63 | 7 clases |
| Segundo | 66 | $200 antigua y reforzamiento de $200 nueva, $50 antigua, $50 nueva |
| **Total real** | **129** | 8 clases con capturas propias |

Cada foto se guardó en una carpeta con el nombre de la clase al presionar una tecla, de modo que la etiqueta quedó definida desde el momento de la captura.

### 8.3. Etiquetado automático

Para cada imagen se detectó la moneda mediante **Hough circles** sobre la zona donde aparece en el montaje, y se escribió una caja normalizada:

```text
clase   x_centro   y_centro   ancho   alto     (valores 0–1)
```

Ejemplo real:

```text
1 0.390625 0.502083 0.196875 0.262500
```

Se etiquetaron **129/129 imágenes sin fallos**.

### 8.4. Equilibrado

Las clases con menos ejemplos se duplicaron en `train`:

```python
REPETICIONES = {
    1: 4,  # $100 antigua
    2: 2,  # $100 nueva
}
```

`val` y `test` se mantuvieron intactos para que la evaluación sea honesta.

### 8.5. Hiperparámetros finales

```python
epochs = 30
imgsz = 416
batch = 8
device = "cpu"
optimizer = "AdamW"
lr0 = 0.001
weight_decay = 0.0005
patience = 10
workers = 2
```

### 8.6. Evolución de modelos

| Modelo | Dataset | Resultado en montaje |
|---|---|---|
| `monedas_v1-2` | Sintético 11 clases | Falló: predecía todo como `moneda_1000_nueva` |
| `monedas_9clases` | Roboflow 126 | 3/7 en fotos reales |
| `monedas_final` | 126 + 63 reales | 32/63 |
| `monedas_balanceado` | + equilibrado | 76/129 |
| **`monedas_balanceado_v2`** | **126 + 129 reales + equilibrio** | **127/129 (98 %)** |

---

## 9. Resultados y análisis

### 9.1. Métricas globales

| Métrica | Valor |
|---|:--:|
| mAP50 | 0.899 |
| mAP50-95 | 0.854 |
| Precisión | 0.670 |
| Recall | 0.945 |
| Aciertos en fotos reales | 127/129 (98 %) |

### 9.2. Resultado por clase

| Clase | Aciertos | Modelo anterior | Mejora |
|---|:--:|:--:|:--:|
| $1.000 | 9/9 | 9/9 | — |
| $100 antigua | 7/7 | 7/7 | — |
| $100 nueva | 8/8 | 8/8 | — |
| $200 antigua | 15/15 | 0/15 | ✅ |
| $200 nueva | 35/35 | 19/35 | ✅ |
| $500 nueva | 10/10 | 10/10 | — |
| $50 antigua | 20/21 | 9/21 | ✅ |
| $50 nueva | 23/24 | 14/24 | ✅ |

### 9.3. Análisis de confusiones

Solo persisten dos errores:

- Una foto de $50 antigua se predijo como $50 nueva.
- Una foto de $50 nueva se predijo como $50 antigua.

Es una **confusión cruzada** entre las dos variantes de $50, las más parecidas visualmente. No hay errores entre denominaciones distintas, lo que valida que el sistema es seguro para la separación por valor.

### 9.4. Ejemplos de inferencia

```text
200_pesos_nueva  conf=0.94  → código 8  → 250°
50_pesos_nueva   conf=0.91  → código 6  → 215°
100_pesos        conf=0.98  → código 2  → 38°
50_pesos         conf=0.84  → código 1  → 0°
```

### 9.5. Velocidad

En CPU (Intel Core i5-12450H):

- Preprocesamiento: ~3 ms
- Inferencia: ~160 ms
- Postprocesamiento: ~2 ms

Con `imgsz=416` el sistema es fluido para una moneda a la vez, que es el caso real de operación.

---

## 10. Instalación y configuración

### 10.1. Requisitos

- Python 3.10 o superior (probado con 3.14).
- OpenCV, Ultralytics y PySerial.
- Cámara USB o celular con DroidCam.
- ESP32 con el firmware grabado.
- Windows (para `os.startfile` en el demo de imágenes).

### 10.2. Entorno virtual

```powershell
cd "C:\Users\Cocot\OneDrive\Documentos\1. MATERIAS UNIVERSIDAD MILITAR NUEVA GRANADA\QUINTO SEMESTRE\Micros\PROYECTO-FINAL"
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 10.3. Dependencias

```powershell
pip install ultralytics opencv-python pyserial inputs pillow numpy
```

### 10.4. Verificación rápida

```powershell
python -c "import cv2, ultralytics, serial; print('Dependencias OK')"
python scripts/probar_camara.py
python scripts/03_infer.py "dataset_reposicion/images/100_pesos/100_pesos_1794877163516.jpg"
```

### 10.5. Configuración del ESP32

1. Instalar `ESP32Servo` y `Stepper` en Arduino IDE.
2. Seleccionar placa ESP32 y puerto USB.
3. Verificar que los `#include` estén activos en `SeparadorMonedas.cpp`.
4. Grabar el firmware.
5. Anotar el puerto COM (por ejemplo `COM3`).

### 10.6. Configuración de la cámara del celular

**Recomendado: DroidCam por USB**

1. Instalar DroidCam en el celular y DroidCam Client en Windows.
2. Activar depuración USB en el celular.
3. Conectar por cable y presionar **Start** en el cliente.
4. Obtener el índice de cámara:

```powershell
python scripts/probar_camara.py
```

**Alternativa: IP Webcam por WiFi**

```powershell
python scripts/04_demo.py webcam http://192.168.1.25:8080/video
```

> El video viaja por la red local (LAN), sin internet. Si la red universitaria bloquea la comunicación entre dispositivos, usar el hotspot del celular.

---

## 11. Guía de uso

Todos los comandos se ejecutan desde la raíz del proyecto.

### 11.1. Ver cámara con detecciones

```powershell
python scripts/04_demo.py webcam 1
```

### 11.2. Procesar una imagen

```powershell
python scripts/04_demo.py "dataset_reposicion\images\50_pesos\50_pesos_1794877310239.jpg"
```

### 11.3. Ver datos por texto

```powershell
python scripts/03_infer.py "ruta_de_la_imagen.jpg"
```

### 11.4. Integración con ESP32 (simulación)

```powershell
python scripts/integrar_esp32.py 1 --simular
```

### 11.5. Integración real

```powershell
python scripts/integrar_esp32.py 1 --puerto COM8
```

Modo manual con tecla: YOLO muestra la moneda que está leyendo en pantalla y **solo envía el caso cuando presionas `ESPACIO`** (o `Enter`). Entonces el ESP32 mueve el motor, acciona el servo y enciende la banda 10 s después:

```powershell
python scripts/integrar_esp32.py 1 --puerto COM8
```

Teclas: `ESPACIO` = enviar caso · `q` = salir. Si no hay moneda a la vista, el envío se ignora.

**Modo automático:** al detectar una moneda, espera unos segundos y envía solo:

```powershell
python scripts/integrar_esp32.py 1 --puerto COM8 --auto --espera 3
```

Al detectar la moneda muestra `AUTO: 50_pesos 73% -> envio en 2.4s` y cuando llega a cero envía el caso. Luego espera a que la moneda desaparezca de la cámara para procesar la siguiente (así no envía dos veces la misma).
```

### 11.6. Capturar más datos

```powershell
python scripts/capturar_dataset.py 1
```

| Tecla | Clase |
|:--:|---|
| 1 | $1.000 |
| 2 | $100 antigua |
| 3 | $100 nueva |
| 4 | $200 antigua |
| 5 | $200 nueva |
| 6 | $500 antigua |
| 7 | $500 nueva |
| 8 | $50 antigua |
| 9 | $50 nueva |
| q | Salir |

### 11.7. Reconstruir y reentrenar

```powershell
python scripts/etiquetar_reposicion.py
python scripts/combinar_datasets.py
python scripts/equilibrar_dataset.py
python scripts/06_reentrenar_balanceado.py
python scripts/verificar_v2.py
```

### 11.8. Control del carro oruga

1. Grabar `CarroOruga/CarroOruga.ino` en el ESP32 del carro.
2. Conectar el mando Xbox 360 por cable a la PC.
3. Probar sin hardware:

```powershell
python scripts/mando_xbox.py --simular
```

4. Control real:

```powershell
python scripts/mando_xbox.py --puerto COM3
```

> Si hay dos ESP32 conectados, usa puertos distintos: uno para el clasificador y otro para el carro.

### 11.9. Dashboard web

Se incluye un **dashboard web** que reúne todo el sistema en una sola pantalla:

- **Video en vivo** del YOLO contando monedas por denominación.
- **Contadores** de las 9 clases con total general y botón de reinicio.
- **Control manual** del carro con botones direccionales y regulación de velocidad.
- **Modo automático** de evasión con el HC-SR04.
- **Telemetría**: distancia, velocidades de motores y registro de eventos.

El servidor está hecho con `http.server` de Python, por lo que **no requiere Flask ni dependencias adicionales** (solo las ya instaladas: ultralytics, opencv-python y pyserial).

```powershell
python dashboard/servidor.py
python dashboard/servidor.py --camara 1 --puerto-serial COM3
python dashboard/servidor.py --simular       # sin cámara ni ESP32
```

Luego abre en el navegador:

```text
http://127.0.0.1:8000
```

**API del dashboard**

| Ruta | Método | Función |
|---|---|---|
| `/` | GET | Interfaz web |
| `/video` | GET | Flujo MJPEG con detecciones dibujadas |
| `/api/estado` | GET | Conteo, telemetría y registros |
| `/api/comando` | POST | `{ "comando": "M,150,-150" }`, `A`, `S`, `D`, `T` |
| `/api/reiniciar` | POST | Pone los contadores en cero |

> El conteo usa la misma lógica de "una moneda a la vez": 3 fotogramas estables para registrar y 5 sin detección para permitir la siguiente.

---

## 12. Protocolo de integración con el ESP32

### 12.1. Diagrama de estados

```text
   [SIN MONEDA]
        │ detección
        ▼
   [CANDIDATO] ── 3 frames estables ──► [ENVIADO] ──► write("N\n")
        ▲                                   │
        │                                   │ misma clase en pantalla
        └──── 5 frames sin detección ◄───────┘
                      │
                      ▼
                [SIN MONEDA]
```

### 12.2. Trama enviada

```text
YOLO clase 7 ($50 antigua) → se envía "1\n"  → case 1  → motor a 0°
YOLO clase 0 ($1.000)      → se envía "10\n" → case 10 → motor a 320°
```

El código enviado es **exactamente el número del `case`** en `SeparadorMonedas.cpp`. Por eso cada `case` lleva una anotación con la clase YOLO que lo dispara, y `scripts/mapeo_esp32.py` contiene la misma tabla en Python. Para verla completa:

```powershell
python scripts/mapeo_esp32.py
```

El salto de línea es importante: `Serial.parseInt()` del ESP32 interpreta el número completo y luego limpia el buffer.

### 12.3. Temporización

| Parámetro | Valor | Razón |
|---|---|---|
| `FRAMES_ESTABLES` | 3 | Evita enviar por un falso positivo |
| `FRAMES_SIN_MONEDA` | 5 | Confirma que la moneda salió de la zona |
| `max_det` | 1 | Solo se lee una moneda a la vez |
| `conf` | 0.25 | Umbral validado en las pruebas |
| `imgsz` | 416 | Tamaño usado en el entrenamiento final |

### 12.4. Seguridad

- Si la clase detectada no tiene código, no se envía nada.
- Si falla el puerto serial, el script lo informa y termina limpiamente.
- El modo `--simular` permite validar toda la lógica sin hardware.

---

## 13. Estructura de carpetas

```text
PROYECTO-FINAL/
├── README.md
├── yolov8n.pt
├── SeparadorMonedas.cpp              # Firmware del clasificador
│
├── CarroOruga/
│   └── CarroOruga.ino                # Firmware del carro (H-bridge + HC-SR04)
│
├── dashboard/
│   ├── servidor.py                   # Servidor web + YOLO + serial
│   └── index.html                    # Interfaz del dashboard
│
├── dataset_9clases/                  # Roboflow convertido
│   ├── data.yaml
│   ├── images/{train,val,test}/
│   └── labels/{train,val,test}/
│
├── dataset_reposicion/               # 129 capturas reales
│   └── images/<clase>/*.jpg
│
├── dataset_final/                    # Roboflow + capturas
├── dataset_balanceado/               # Clases minoritarias reforzadas
│
├── runs/
│   ├── monedas_v1/                   # Primeros intentos
│   ├── monedas_v1-2/
│   ├── monedas_9clases/              # Entrenamiento base
│   ├── monedas_real/                 # Prueba de 5 clases
│   ├── monedas_final/                # Ajuste inicial
│   ├── monedas_balanceado/           # Primer equilibrado
│   └── monedas_balanceado_v2/        # MODELO FINAL
│       └── weights/best.pt
│
└── scripts/
    ├── 01_generate_synthetic.py
    ├── 02_train.py
    ├── 03_infer.py
    ├── 04_demo.py
    ├── 05_afinar_real.py
    ├── 06_reentrenar_balanceado.py
    ├── capturar_dataset.py
    ├── etiquetar_reposicion.py
    ├── combinar_datasets.py
    ├── equilibrar_dataset.py
    ├── preparar_dataset.py
    ├── preparar_dataset_9clases.py
    ├── probar_camara.py
    ├── mapeo_esp32.py
    ├── integrar_esp32.py
    ├── mando_xbox.py                 # Mando Xbox -> carro oruga
    ├── diagnostico_monedas.py
    ├── verificar_real.py
    ├── verificar_balanceado.py
    └── verificar_v2.py
```

---

## 14. Solución de problemas y FAQ

### ¿El script dice "No hay pesos entrenados"?

Verifica que exista `runs/monedas_balanceado_v2/weights/best.pt`. Los scripts priorizan ese archivo; si falta, buscan el más reciente.

### ¿La cámara no abre?

- Prueba `python scripts/probar_camara.py`.
- Cierra Teams, Zoom u otras apps que usen la cámara.
- Si DroidCam está en otro índice, usa `python scripts/04_demo.py webcam 2`.

### ¿Detecta pero se mueve varias veces la misma moneda?

Usa `integrar_esp32.py`, que implementa "una instrucción por moneda". El demo simple no envía serial.

### ¿El modelo confunde $50 antigua con $50 nueva?

Es la única confusión residual. Captura más fotos de ambas con las teclas `8` y `9` y reconstruye el dataset.

### ¿Puedo usar WiFi en vez de USB?

Sí, con la URL de IP Webcam. Pero el cable USB es más estable y evita latencia.

### ¿Es necesario volver a entrenar cada vez?

No. Solo si capturas nuevas imágenes o cambias las clases.

### ¿El carro oruga interactúa con el clasificador?

El clasificador y el carro comparten el ecosistema electrónico (ESP32 y motores). El carro aporta movilidad como plataforma complementaria y tiene su propio firmware en `CarroOruga/CarroOruga.ino`, con evasión automática por HC-SR04 y control por mando Xbox 360 mediante `scripts/mando_xbox.py`.

### ¿JArvis reemplaza al README?

No, lo complementa: el README es la referencia escrita y JArvis la explicación conversacional.

---

## 15. Mejoras futuras

### Fase 1 — Precisión

- Capturar más muestras de $50 antigua y $50 nueva.
- Probar iluminación uniforme y fondo de alto contraste en la zona de lectura.
- Validar con monedas giradas y parcialmente superpuestas.

### Fase 2 — Electrónica

- Sensor *home* para calibrar la posición inicial del motor.
- *Handshake* ESP32 → PC confirmando cada movimiento.
- Driver de motor más rápido (A4988/DRV8825) para reducir tiempos.

### Fase 3 — Software

- Interfaz gráfica con contador por denominación.
- Registro de clasificaciones a CSV.
- Detector de moneda detenida antes de capturar.

### Fase 4 — Interacción y movilidad

- Integrar la voz de JArvis con los eventos de clasificación en tiempo real.
- Añadir sensores ultrasónicos al carro oruga para navegación semiautónoma.
- Control remoto del carro desde el mismo script de integración.

### Fase 5 — Despliegue

- Conversión del modelo a ONNX / TFLite para ejecutar en hardware embebido.
- Alimentación independiente y estanca para el prototipo completo.

---

## 16. Glosario

| Término | Definición |
|---|---|
| **BGR** | Orden de canales de color usado por OpenCV (azul, verde, rojo). |
| **IoU** | Métrica de traslape entre dos cajas. |
| **mAP** | Precisión promedio media, métrica principal de detección. |
| **NMS** | Supresión de cajas duplicadas. |
| **YOLO** | *You Only Look Once*, detector de una sola etapa. |
| **Hough** | Técnica de detección de formas geométricas, usada aquí para círculos. |
| **PWM** | Modulación por ancho de pulso, usada para servos y motores. |
| **Puente H** | Circuito que invierte la polaridad de un motor DC. |
| **Oruga** | Cinta continua de tracción usada en terrenos irregulares. |
| **ESP32** | Microcontrolador con WiFi y Bluetooth. |
| **Serial** | Comunicación byte a byte por USB. |
| **Fine-tuning** | Ajuste de un modelo preentrenado con nuevos datos. |
| **JArvis** | Asistente de IA que explica el proyecto. |

---

## 17. Referencias

1. Redmon, J. et al. *You Only Look Once: Unified, Real-Time Object Detection*. CVPR, 2016.
2. Ultralytics. *YOLOv8 Documentation*. https://docs.ultralytics.com
3. OpenCV. *Camera capture and image processing*. https://opencv.org
4. EsPressif. *ESP32 Technical Reference Manual*. https://www.espressif.com
5. Roboflow. *Dataset export format YOLOv8*. https://roboflow.com
6. Bradski, G. *The OpenCV Library*. Dr. Dobb's Journal, 2000.
7. OpenCV. *HoughCircles — Image Processing*. https://docs.opencv.org
8. PySerial documentation. https://pyserial.readthedocs.io

---

## 18. Créditos

**Institución:** Universidad Militar Nueva Granada (UMNG)
**Programa:** Ingeniería en Mecatrónica
**Semestre:** Quinto — 2026
**Áreas:** Visión artificial · Inteligencia artificial · Sistemas embebidos · Electrónica · Mecánica · Automatización

**Componentes desarrollados**

- Modelo YOLO y pipeline de entrenamiento.
- Firmware del ESP32 para motor paso a paso y servo.
- Scripts de captura, etiquetado y validación.
- Integración serial con una instrucción por moneda.
- JArvis, asistente conversacional del proyecto.
- Dashboard web con conteo YOLO, control manual/automático y telemetría.
- Banda transportadora para la alimentación de monedas hacia la zona de inspección.
- Carro oruga con motores de 12 V como plataforma móvil complementaria.

---

<div align="center">

**Sistema Automatizado de Clasificación de Monedas Colombianas**

*Percepción → decisión → actuación → explicación.*

</div>
