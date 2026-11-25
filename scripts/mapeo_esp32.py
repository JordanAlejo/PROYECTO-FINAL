"""Correspondencia entre YOLO y los cases del firmware SeparadorMonedas.cpp.

Orden de clases de YOLO (dataset_9clases/data.yaml):
  0=1000_pesos  1=100_pesos  2=100_pesos_nueva
  3=200_pesos   4=200_pesos_nueva  5=500_pesos
  6=500_pesos_nueva  7=50_pesos  8=50_pesos_nueva

Cadena completa (YOLO -> serial -> ESP32):

  YOLO clase | clase YOLO       | codigo enviado | case ESP32 | angulo
 ------------+------------------+----------------+------------+--------
      0      | 1000_pesos       |      10        |   case 10  |  320°
      1      | 100_pesos        |       2        |   case  2  |   38°
      2      | 100_pesos_nueva  |       7        |   case  7  |  182°
      3      | 200_pesos        |       3        |   case  3  |   75°
      4      | 200_pesos_nueva  |       8        |   case  8  |  250°
      5      | 500_pesos        |       4        |   case  4  |  110°
      6      | 500_pesos_nueva  |       9        |   case  9  |  285°
      7      | 50_pesos         |       1        |   case  1  |    0°
      8      | 50_pesos_nueva   |       6        |   case  6  |  215°

  El case 5 (148°) queda libre para uso manual; no lo usa el clasificador.

El ESP32 recibe el codigo con Serial.parseInt() dentro de loop() y ejecuta
moverAlAngulo(angulo), que mueve el motor paso a paso y luego el servo.
"""

NOMBRES = {
    0: "1000_pesos",
    1: "100_pesos",
    2: "100_pesos_nueva",
    3: "200_pesos",
    4: "200_pesos_nueva",
    5: "500_pesos",
    6: "500_pesos_nueva",
    7: "50_pesos",
    8: "50_pesos_nueva",
}

# ID de clase YOLO -> codigo que espera el ESP32 (= numero del case)
CLASIFICACION = {
    0: 10,  # 1000_pesos       -> case 10 -> 320°
    1: 2,   # 100_pesos        -> case  2 ->  38°
    2: 7,   # 100_pesos_nueva  -> case  7 -> 182°
    3: 3,   # 200_pesos        -> case  3 ->  75°
    4: 8,   # 200_pesos_nueva  -> case  8 -> 250°
    5: 4,   # 500_pesos        -> case  4 -> 110°
    6: 9,   # 500_pesos_nueva  -> case  9 -> 285°
    7: 1,   # 50_pesos         -> case  1 ->   0°
    8: 6,   # 50_pesos_nueva   -> case  6 -> 215°
}

# Codigo ESP32 -> angulo del motor paso a paso (mismo valor del switch-case)
ANGULOS = {
    1: 0,
    2: 38,
    3: 75,
    4: 110,
    5: 148,   # libre
    6: 215,
    7: 182,
    8: 250,
    9: 285,
    10: 320,
}

# Codigo ESP32 -> clase YOLO (util para verificar el cableado logico)
CASO_A_CLASE = {codigo: clase for clase, codigo in CLASIFICACION.items()}


def codigo_para_clase(clase_id):
    """Devuelve el codigo ESP32 para un ID de clase de YOLO, o None."""
    return CLASIFICACION.get(int(clase_id))


def angulo_para_clase(clase_id):
    """Devuelve el angulo del motor para una clase de YOLO."""
    codigo = codigo_para_clase(clase_id)
    return ANGULOS.get(codigo) if codigo is not None else None


def cadena_completa():
    """Texto con la cadena YOLO -> ESP32 para documentacion/debug."""
    lineas = ["YOLO -> ESP32 (codigo = case del switch)"]
    for clase in sorted(NOMBRES):
        codigo = codigo_para_clase(clase)
        lineas.append(
            f"  clase {clase}: {NOMBRES[clase]:16} -> "
            f"case {codigo:2} -> {ANGULOS[codigo]:3}°"
        )
    return "\n".join(lineas)


if __name__ == "__main__":
    print(cadena_completa())
