#include <Stepper.h>
#include <ESP32Servo.h>

const long PASOS_VUELTA = 2048;

#define IN1 18
#define IN2 19
#define IN3 21
#define IN4 22

// Servo del mecanismo de direccionamiento
#define PIN_SERVO 12
Servo miServo;

// Pin de control de la banda transportadora
#define PIN_BANDA 13

// La banda enciende al recibir el caso y se apaga 10 s despues
const unsigned long DURACION_BANDA = 10000;
unsigned long momentoBanda = 0;
bool bandaPendiente = false;   // true mientras corre el temporizador de apagado
bool bandaEncendida = false;

Stepper motor(PASOS_VUELTA, IN1, IN3, IN2, IN4);

// Posicion actual en pasos
long posicionActual = 0;

// Angulos fijos de las monedas (los que envia YOLO por los casos 1..10)
const int ANGULO_MONEDA[11] = {
  0,
  0,    // 1  $50 antigua  -> 0 grados (cero)
  38,   // 2  $100 antigua
  75,   // 3  $200 antigua
  110,  // 4  $500 antigua
  148,  // 5  libre
  215,  // 6  $50 nueva
  182,  // 7  $100 nueva
  250,  // 8  $200 nueva
  285,  // 9  $500 nueva
  320   // 10 $1000
};

// ---------- SERVO: gira a 90 y vuelve a 0 ----------
void accionarServo() {
  Serial.println("Servo girando a 90 grados");
  miServo.write(90);
  delay(700);
  Serial.println("Servo regresando a 0 grados");
  miServo.write(0);
  delay(700);
}

void setup() {
  Serial.begin(115200);
  Serial.setTimeout(100);

  motor.setSpeed(8);

  miServo.setPeriodHertz(50);
  miServo.attach(PIN_SERVO, 500, 2400);
  miServo.write(0);
  delay(500);

  pinMode(PIN_BANDA, OUTPUT);
  digitalWrite(PIN_BANDA, LOW);   // banda apagada al iniciar

  Serial.println("CONTROL ANGULAR");
  Serial.println("Posicion inicial: 0 grados");
  Serial.println("Ingresa un angulo de 0 a 360:");
  Serial.println("Z = registrar cero | Z+ / Z- = ajuste fino | ZZ = ver cero");
  Serial.println("P,<angulo> = fijar posicion inicial (ej. P,30 sin mover)");
  Serial.println("B = banda ON/OFF (con un caso YOLO enciende 10 s y se apaga)");
}

void loop() {

  // ---- TEMPORIZADOR DE APAGADO (no bloqueante) ----
  if (bandaPendiente && (millis() - momentoBanda >= DURACION_BANDA)) {
    digitalWrite(PIN_BANDA, LOW);
    bandaEncendida = false;
    bandaPendiente = false;
    Serial.println("Banda transportadora APAGADA (10 s de funcionamiento)");
  }

  if (Serial.available() > 0) {

    String entrada = Serial.readStringUntil('\n');
    entrada.trim();

    if (entrada.length() == 0) return;

    // ---- AJUSTE MANUAL DEL CERO ----
    if (entrada == "Z") {
      posicionActual = 0;              // la posicion fisica actual pasa a ser 0
      Serial.println("Cero registrado en la posicion actual");
      return;
    }
    if (entrada == "Z+" || entrada == "Z-") {
      long paso = round(PASOS_VUELTA / 360.0);   // ~6 pasos = 1 grado
      long delta = (entrada == "Z+") ? paso : -paso;

      // camino mas corto
      if (delta > PASOS_VUELTA / 2) delta -= PASOS_VUELTA;
      else if (delta < -PASOS_VUELTA / 2) delta += PASOS_VUELTA;

      motor.step(delta);
      posicionActual += delta;
      posicionActual = 0;              // nueva posicion = cero
      Serial.print("Cero ajustado ");
      Serial.println(entrada);
      return;
    }
    if (entrada == "ZZ") {
      Serial.print("Cero actual: ");
      Serial.println(posicionActual * 360.0 / PASOS_VUELTA);
      return;
    }

    // Posicion inicial: P,<angulo> -> el motor NO se mueve, solo se le dice
    // en que angulo esta ahora. Ej: P,30 -> "estoy en 30 grados".
    if (entrada.startsWith("P,")) {
      float ang = entrada.substring(2).toFloat();
      if (ang < 0 || ang > 360) {
        Serial.println("Angulo invalido (0-360)");
        return;
      }
      if (ang == 360) ang = 0;
      posicionActual = round(ang * PASOS_VUELTA / 360.0);
      Serial.print("Posicion inicial fijada en ");
      Serial.print(ang);
      Serial.println(" grados (sin mover el motor)");
      return;
    }

    // Banda: apagar/encender manualmente
    if (entrada == "B") {
      bandaEncendida = !bandaEncendida;
      bandaPendiente = false;
      digitalWrite(PIN_BANDA, bandaEncendida ? HIGH : LOW);
      Serial.println(bandaEncendida ? "Banda ENCENDIDA" : "Banda APAGADA");
      return;
    }

    // ---- CASOS QUE MANDA YOLO ----
    int opcion = entrada.toInt();
    if (opcion >= 1 && opcion <= 10) {
      float angulo = ANGULO_MONEDA[opcion];

      long destino = round(angulo * PASOS_VUELTA / 360.0);
      long diferencia = destino - posicionActual;

      if (diferencia > PASOS_VUELTA / 2) diferencia -= PASOS_VUELTA;
      else if (diferencia < -PASOS_VUELTA / 2) diferencia += PASOS_VUELTA;

      Serial.print("Caso ");
      Serial.print(opcion);
      Serial.print(" -> ");
      Serial.print(angulo);
      Serial.println(" grados");

      motor.step(diferencia);
      posicionActual = destino;

      // Mover el servo del mecanismo de direccionamiento
      accionarServo();

      // Banda ENCENDIDA de inmediato y apagado automatico en 10 s
      digitalWrite(PIN_BANDA, HIGH);
      bandaEncendida = true;
      bandaPendiente = true;
      momentoBanda = millis();
      Serial.println("Banda transportadora ENCENDIDA (se apagara en 10 s)");

      Serial.println("Esperando siguiente orden...");
      Serial.println("-------------------------");
      return;
    }

    // ---- ANGULO MANUAL (tu codigo original) ----
    float angulo = entrada.toFloat();

    if (angulo < 0 || angulo > 360) {
      Serial.println("Angulo invalido");
      return;
    }

    if (angulo == 360) angulo = 0;

    long destino = round(angulo * PASOS_VUELTA / 360.0);
    long diferencia = destino - posicionActual;

    if (diferencia > PASOS_VUELTA / 2) {
      diferencia -= PASOS_VUELTA;
    }
    else if (diferencia < -PASOS_VUELTA / 2) {
      diferencia += PASOS_VUELTA;
    }

    Serial.print("Posicion anterior: ");
    Serial.println(posicionActual * 360.0 / PASOS_VUELTA);

    Serial.print("Destino: ");
    Serial.println(angulo);

    Serial.print("Movimiento: ");
    Serial.println(diferencia * 360.0 / PASOS_VUELTA);

    motor.step(diferencia);

    posicionActual = destino;

    Serial.print("Posicion guardada: ");
    Serial.println(posicionActual * 360.0 / PASOS_VUELTA);

    Serial.println("Esperando siguiente orden...");
    Serial.println("-------------------------");
  }
}
