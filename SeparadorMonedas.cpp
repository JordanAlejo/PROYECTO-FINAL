/*
#include <ESP32Servo.h>
#include <Stepper.h>
#include <math.h>
*/
// ---------- CONFIGURACION DEL MOTOR PASO A PASO ----------
const int PASOS_POR_VUELTA = 2048;

Stepper motor(PASOS_POR_VUELTA, 18, 21, 19, 22);

// ---------- CONFIGURACION DEL SERVO ----------
Servo miServo;
const int PIN_SERVO = 12;

// ---------- VARIABLES ----------
int opcion = -1;
int posicionActual = 0;

// ---------- FUNCION DEL SERVO ----------
void accionarServo() {
  delay(2000); 
  Serial.println("Servo girando a 180 grados");

  miServo.write(180);
  delay(700);

  Serial.println("Servo regresando a 0 grados");

  miServo.write(0);
  delay(700);
}

// ---------- FUNCION DEL MOTOR ----------
void moverAlAngulo(int anguloObjetivo) {

  // Normalizar el angulo objetivo entre 0 y 359
  anguloObjetivo = ((anguloObjetivo % 360) + 360) % 360;

  // Normalizar la posicion actual
  int posicionNormalizada =
      ((posicionActual % 360) + 360) % 360;

  // Calcular la diferencia angular
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

  // Primero mover el motor paso a paso
  motor.step(pasos);

  // Actualizar la posicion
  posicionActual = anguloObjetivo;

  Serial.println("Motor en posicion.");

  // Solo cuando termina el motor, accionar el servo
  accionarServo();

  Serial.println("Proceso terminado.");
}

// ---------- MENU ----------
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

// ---------- SETUP ----------
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

// ---------- LOOP ----------
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