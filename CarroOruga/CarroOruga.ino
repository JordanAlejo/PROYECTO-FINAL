/*
  CarroOruga.ino - ESP32
  ---------------------------------------------------------------
  Carro con tracción por orugas, puente H, sensor HC-SR04 y control
  por mando Xbox 360 cableado (a través de Python por serial).

  Protocolo serial (115200 baudios):
    M,<izq>,<der>\n   Motor: izq/der en -255..255
    A\n               Alternar modo automático (evasión de obstáculos)
    S\n               Detener
    D\n               Consultar distancia
    T\n               Consultar estado

  Respuestas:
    D:<cm>\n
    T,<dist>,<modo>,<izq>,<der>\n

  Seguridad: si no llega un comando en 1500 ms en modo manual, se detiene.
*/

#include <Arduino.h>

// ---------------- PINES (modificar según cableado) ----------------
// Puente H (por ejemplo L298N o módulo similar)
const int IN1 = 25;   // Motor izquierdo
const int IN2 = 26;
const int ENA = 27;   // PWM izquierdo

const int IN3 = 14;   // Motor derecho
const int IN4 = 4;
const int ENB = 16;   // PWM derecho

// Sensor ultrasónico HC-SR04
const int TRIG = 32;
const int ECHO = 33;

// ---------------- CONFIGURACIÓN ----------------
const int UMBRAL_EVASION = 25;    // cm: distancia para empezar a esquivar
const int UMBRAL_CRITICO  = 12;   // cm: bloquear avance manual
const unsigned long TIMEOUT_COMANDO = 1500;  // ms
const unsigned long PERIODO_TELEMETRIA = 500;// ms

const int PWM_FREQ = 1000;
const int PWM_RES  = 8;           // 0..255
const int PWM_CANAL_IZQ = 0;
const int PWM_CANAL_DER = 1;

// ---------------- ESTADO ----------------
int velIzq = 0;
int velDer = 0;
bool modoAuto = false;
unsigned long ultimoComando = 0;
unsigned long ultimaTelemetria = 0;

// Máquina de estados de evasión
enum EstadoEvasion { AVAZAR, RETROCEDER, GIRAR };
EstadoEvasion estadoEvasion = AVAZAR;
unsigned long inicioEstado = 0;
unsigned long ultimaLectura = 0;
int distancia = 999;

// ---------------- PROTOTIPOS ----------------
int leerDistancia();
void mover(int izq, int der);
void detener();
void aplicarEvasion(int dist);
void enviarTelemetria();
void procesarComando(String cmd);

// ---------------- SETUP ----------------
void setup() {
  Serial.begin(115200);

  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);
  pinMode(TRIG, OUTPUT);
  pinMode(ECHO, INPUT);

  ledcAttachChannel(ENA, PWM_FREQ, PWM_RES, PWM_CANAL_IZQ);
  ledcAttachChannel(ENB, PWM_FREQ, PWM_RES, PWM_CANAL_DER);

  digitalWrite(TRIG, LOW);
  detener();

  Serial.println("Carro oruga listo. M,<izq>,<der> | A | S | D | T");
}

// ---------------- LOOP ----------------
void loop() {
  // 1. Leer comandos seriales
  if (Serial.available() > 0) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();
    procesarComando(cmd);
    ultimoComando = millis();
  }

  // 2. Leer distancia cada 60 ms (filtrada)
  if (millis() - ultimaLectura >= 60) {
    distancia = leerDistancia();
    ultimaLectura = millis();
  }

  // 3. Watchdog: sin comandos en manual -> detener
  if (!modoAuto && (millis() - ultimoComando > TIMEOUT_COMANDO)) {
    if (velIzq != 0 || velDer != 0) {
      detener();
      Serial.println("W: watchdog, motores detenidos");
    }
  }

  // 4. Modo automático: evasión de obstáculos
  if (modoAuto) {
    aplicarEvasion(distancia);
  }

  // 5. Telemetría periódica
  if (millis() - ultimaTelemetria >= PERIODO_TELEMETRIA) {
    enviarTelemetria();
    ultimaTelemetria = millis();
  }
}

// ---------------- SENSOR ----------------
int leerDistancia() {
  long duraciones[3];
  int validas = 0;

  for (int i = 0; i < 3; i++) {
    digitalWrite(TRIG, LOW);
    delayMicroseconds(2);
    digitalWrite(TRIG, HIGH);
    delayMicroseconds(10);
    digitalWrite(TRIG, LOW);

    long d = pulseIn(ECHO, HIGH, 30000);  // 30 ms de timeout
    if (d > 0) {
      duraciones[validas++] = d;
    }
    delay(15);
  }

  if (validas == 0) return 999;

  // Mediana de las lecturas válidas
  for (int i = 0; i < validas - 1; i++) {
    for (int j = 0; j < validas - i - 1; j++) {
      if (duraciones[j] > duraciones[j + 1]) {
        long t = duraciones[j];
        duraciones[j] = duraciones[j + 1];
        duraciones[j + 1] = t;
      }
    }
  }
  long d = duraciones[validas / 2];
  return (int)(d * 0.0343 / 2.0);  // cm
}

// ---------------- MOTORES ----------------
void mover(int izq, int der) {
  izq = constrain(izq, -255, 255);
  der = constrain(der, -255, 255);

  // Izquierdo
  digitalWrite(IN1, izq > 0 ? HIGH : LOW);
  digitalWrite(IN2, izq < 0 ? HIGH : LOW);
  ledcWriteChannel(PWM_CANAL_IZQ, abs(izq));

  // Derecho
  digitalWrite(IN3, der > 0 ? HIGH : LOW);
  digitalWrite(IN4, der < 0 ? HIGH : LOW);
  ledcWriteChannel(PWM_CANAL_DER, abs(der));

  velIzq = izq;
  velDer = der;
}

void detener() {
  mover(0, 0);
}

// ---------------- EVASIÓN ----------------
void aplicarEvasion(int d) {
  switch (estadoEvasion) {
    case AVAZAR:
      mover(160, 160);
      if (d < UMBRAL_EVASION) {
        estadoEvasion = RETROCEDER;
        inicioEstado = millis();
        Serial.println("E: obstaculo, retrocediendo");
      }
      break;

    case RETROCEDER:
      mover(-150, -150);
      if (millis() - inicioEstado > 600) {
        estadoEvasion = GIRAR;
        inicioEstado = millis();
        // giro suave hacia un lado; se alterna en cada evento
        static bool girarDerecha = true;
        girarDerecha = !girarDerecha;
        mover(girarDerecha ? 150 : -150, girarDerecha ? -150 : 150);
      }
      break;

    case GIRAR:
      if (millis() - inicioEstado > 700) {
        estadoEvasion = AVAZAR;
      }
      break;
  }
}

// ---------------- COMANDOS ----------------
void procesarComando(String cmd) {
  if (cmd.length() == 0) return;

  if (cmd.charAt(0) == 'M') {
    int p1 = cmd.indexOf(',');
    int p2 = cmd.indexOf(',', p1 + 1);
    if (p1 > 0 && p2 > p1) {
      int izq = cmd.substring(p1 + 1, p2).toInt();
      int der = cmd.substring(p2 + 1).toInt();

      // Evitar choque en manual: bloquear avance si está muy cerca
      if (distancia < UMBRAL_CRITICO && izq > 0 && der > 0) {
        izq = 0;
        der = 0;
        Serial.println("E: muy cerca, avance bloqueado");
      }
      mover(izq, der);
    }
  }
  else if (cmd == "A") {
    modoAuto = !modoAuto;
    estadoEvasion = AVAZAR;
    detener();
    Serial.print("Modo ");
    Serial.println(modoAuto ? "AUTOMATICO" : "MANUAL");
  }
  else if (cmd == "S") {
    modoAuto = false;
    detener();
    Serial.println("Detenido");
  }
  else if (cmd == "D") {
    Serial.print("D:");
    Serial.println(distancia);
  }
  else if (cmd == "T") {
    enviarTelemetria();
  }
}

void enviarTelemetria() {
  Serial.print("T,");
  Serial.print(distancia);
  Serial.print(",");
  Serial.print(modoAuto ? 1 : 0);
  Serial.print(",");
  Serial.print(velIzq);
  Serial.print(",");
  Serial.println(velDer);
}
