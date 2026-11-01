
from pathlib import Path
import random
import shutil

# ==================================================
# 1. RUTAS DEL PROYECTO
# ==================================================

ROOT = Path(__file__).resolve().parent.parent

SOURCE = ROOT / "dataset_nuevo" / "train"
DEST = ROOT / "dataset_5clases"

SEED = 42
random.seed(SEED)

# ==================================================
# 2. CONVERSION DE CLASES
# ==================================================

# Clases originales de Roboflow:
# 0 = 1000_pesos
# 1 = 100_pesos
# 2 = 100_pesos_nueva
# 3 = 200_pesos
# 4 = 200_pesos_nueva
# 5 = 500_pesos
# 6 = 500_pesos_nueva
# 7 = 50_pesos
# 8 = 50_pesos_nueva

# Clases finales:
# 0 = 1000_pesos
# 1 = 100_pesos
# 2 = 200_pesos
# 3 = 500_pesos
# 4 = 50_pesos

CLASS_MAP = {
    0: 0,
    1: 1,
    2: 1,
    3: 2,
    4: 2,
    5: 3,
    6: 3,
    7: 4,
    8: 4,
}

CLASS_NAMES = [
    "1000_pesos",
    "100_pesos",
    "200_pesos",
    "500_pesos",
    "50_pesos",
]

IMAGE_EXTENSIONS = {
    ".jpg", ".jpeg", ".png", ".webp", ".bmp"
}

# ==================================================
# 3. CONVERTIR ETIQUETAS YOLO
# ==================================================

def convertir_etiqueta(linea, archivo, numero_linea):
    """
    Acepta etiquetas YOLO de detección o segmentación.

    Detección:
        clase x_centro y_centro ancho alto

    Segmentación:
        clase x1 y1 x2 y2 ... xn yn

    Las coordenadas están normalizadas entre 0 y 1.
    La salida siempre será una caja delimitadora YOLO.
    """

    partes = linea.strip().split()

    if len(partes) < 5:
        raise ValueError(
            f"\nEtiqueta incompleta:\n{archivo}\n"
            f"Línea: {numero_linea}\n"
            f"Contenido: {linea}"
        )

    try:
        clase_original = int(partes[0])
        coordenadas = [float(valor) for valor in partes[1:]]
    except ValueError as error:
        raise ValueError(
            f"\nHay valores no numéricos en:\n{archivo}\n"
            f"Línea: {numero_linea}\n"
            f"Contenido: {linea}"
        ) from error

    if clase_original not in CLASS_MAP:
        raise ValueError(
            f"\nClase desconocida {clase_original} en:\n{archivo}\n"
            f"Línea: {numero_linea}"
        )

    # Comprobar coordenadas normalizadas.
    if not all(0.0 <= valor <= 1.0 for valor in coordenadas):
        raise ValueError(
            f"\nCoordenadas fuera del rango 0-1:\n{archivo}\n"
            f"Línea: {numero_linea}\n"
            f"Contenido: {linea}"
        )

    # Caso A: etiqueta de detección con cuatro coordenadas.
    if len(coordenadas) == 4:
        x_centro, y_centro, ancho, alto = coordenadas

    # Caso B: etiqueta de segmentación con puntos del polígono.
    else:
        if len(coordenadas) % 2 != 0:
            raise ValueError(
                f"\nCantidad impar de coordenadas de segmentación:\n"
                f"{archivo}\nLínea: {numero_linea}"
            )

        xs = coordenadas[0::2]
        ys = coordenadas[1::2]

        x_min = min(xs)
        x_max = max(xs)
        y_min = min(ys)
        y_max = max(ys)

        x_centro = (x_min + x_max) / 2.0
        y_centro = (y_min + y_max) / 2.0
        ancho = x_max - x_min
        alto = y_max - y_min

    if ancho <= 0 or alto <= 0:
        raise ValueError(
            f"\nCaja delimitadora sin área:\n{archivo}\n"
            f"Línea: {numero_linea}"
        )

    # Convertir la clase original a una de las cinco clases.
    clase_nueva = CLASS_MAP[clase_original]

    return (
        f"{clase_nueva} "
        f"{x_centro:.6f} "
        f"{y_centro:.6f} "
        f"{ancho:.6f} "
        f"{alto:.6f}"
    )


# ==================================================
# 4. VERIFICAR LAS RUTAS
# ==================================================

print("=" * 55)
print("PREPARACION DEL DATASET DE MONEDAS")
print("=" * 55)

print("Carpeta del proyecto:", ROOT)
print("Buscando imágenes en:", SOURCE / "images")
print("Buscando etiquetas en:", SOURCE / "labels")

images_dir = SOURCE / "images"
labels_dir = SOURCE / "labels"

if not images_dir.is_dir():
    raise FileNotFoundError(
        f"\nNo existe la carpeta de imágenes:\n{images_dir}"
    )

if not labels_dir.is_dir():
    raise FileNotFoundError(
        f"\nNo existe la carpeta de etiquetas:\n{labels_dir}"
    )

images = sorted(
    archivo
    for archivo in images_dir.iterdir()
    if archivo.is_file()
    and archivo.suffix.lower() in IMAGE_EXTENSIONS
)

if not images:
    raise RuntimeError(
        f"No se encontraron imágenes en:\n{images_dir}"
    )

print(f"\nImágenes encontradas: {len(images)}")


# ==================================================
# 5. LEER Y CONVERTIR LAS ETIQUETAS
# ==================================================

records = []
missing_labels = []
empty_labels = 0
segmentacion_convertida = 0
deteccion_conservada = 0

for image_path in images:

    label_path = labels_dir / f"{image_path.stem}.txt"

    if not label_path.is_file():
        missing_labels.append(image_path.name)
        continue

    new_lines = []

    contenido_original = label_path.read_text(
        encoding="utf-8-sig"
    )

    for line_number, line in enumerate(
        contenido_original.splitlines(),
        start=1
    ):
        if not line.strip():
            continue

        partes = line.split()

        # Contar el formato original para informar al final.
        if len(partes) == 5:
            deteccion_conservada += 1
        elif len(partes) > 5:
            segmentacion_convertida += 1

        etiqueta_nueva = convertir_etiqueta(
            line,
            label_path,
            line_number
        )

        new_lines.append(etiqueta_nueva)

    if not new_lines:
        empty_labels += 1

    records.append((image_path, new_lines))


# No continuar si faltan etiquetas.
if missing_labels:
    ejemplos = "\n".join(missing_labels[:10])

    raise RuntimeError(
        f"\nHay {len(missing_labels)} imágenes sin etiqueta .txt.\n"
        f"Ejemplos:\n{ejemplos}\n"
        "Corrige las etiquetas antes de continuar."
    )

if len(records) < 10:
    raise RuntimeError(
        "Hay menos de 10 imágenes. "
        "Reúne más datos antes de dividir el dataset."
    )

print("\nEtiquetas procesadas correctamente.")
print("Etiquetas de detección:", deteccion_conservada)
print("Etiquetas de segmentación convertidas:", segmentacion_convertida)
print("Imágenes con etiquetas vacías:", empty_labels)


# ==================================================
# 6. DIVIDIR EL DATASET
# ==================================================

random.shuffle(records)

total = len(records)

n_train = int(total * 0.80)
n_val = int(total * 0.10)

splits = {
    "train": records[:n_train],
    "val": records[n_train:n_train + n_val],
    "test": records[n_train + n_val:],
}

print("\nDivisión del dataset:")

for split_name, split_records in splits.items():
    print(f"{split_name}: {len(split_records)} imágenes")


# ==================================================
# 7. PROTEGER EL DATASET EXISTENTE
# ==================================================

if DEST.exists():
    raise FileExistsError(
        f"\nLa carpeta de destino ya existe:\n{DEST}\n\n"
        "No se sobrescribieron archivos.\n"
        "Si quieres regenerarla, renombra o elimina "
        "manualmente la carpeta dataset_5clases "
        "después de comprobar su contenido."
    )


# ==================================================
# 8. COPIAR IMÁGENES Y GUARDAR ETIQUETAS
# ==================================================

try:
    for split_name, split_records in splits.items():

        out_images = DEST / "images" / split_name
        out_labels = DEST / "labels" / split_name

        out_images.mkdir(parents=True, exist_ok=True)
        out_labels.mkdir(parents=True, exist_ok=True)

        for image_path, new_lines in split_records:

            # Copiar imagen original sin modificarla.
            shutil.copy2(
                image_path,
                out_images / image_path.name
            )

            # Guardar las etiquetas ya convertidas.
            label_out = out_labels / f"{image_path.stem}.txt"

            content = "\n".join(new_lines)

            if content:
                content += "\n"

            label_out.write_text(
                content,
                encoding="utf-8"
            )

    # ==================================================
    # 9. CREAR DATA.YAML
    # ==================================================

    yaml_path = DEST / "data.yaml"

    yaml_content = (
        f"path: '{DEST.resolve().as_posix()}'\n"
        "train: images/train\n"
        "val: images/val\n"
        "test: images/test\n"
        "nc: 5\n"
        "names:\n"
        "  0: 1000_pesos\n"
        "  1: 100_pesos\n"
        "  2: 200_pesos\n"
        "  3: 500_pesos\n"
        "  4: 50_pesos\n"
    )

    yaml_path.write_text(
        yaml_content,
        encoding="utf-8"
    )

except Exception:
    # Eliminar solamente la carpeta nueva si la preparación falla.
    shutil.rmtree(DEST, ignore_errors=True)
    raise


# ==================================================
# 10. RESUMEN FINAL
# ==================================================

print("\n" + "=" * 55)
print("DATASET PREPARADO CORRECTAMENTE")
print("=" * 55)

print("\nClases finales:")

for class_id, name in enumerate(CLASS_NAMES):
    print(f"{class_id}: {name}")

print("\nTotal de imágenes:", total)

for split_name, split_records in splits.items():
    print(f"{split_name}: {len(split_records)} imágenes")

print("\nEtiquetas de detección:", deteccion_conservada)
print("Polígonos convertidos a cajas:", segmentacion_convertida)
print("Etiquetas vacías:", empty_labels)

print("\nDataset creado en:", DEST)
print("Archivo YAML:", DEST / "data.yaml")

print("\nEl dataset original de Roboflow no se modificó.")
print("Los pesos anteriores del modelo no se modificaron.")
print("\nYa puedes comprobar el dataset antes de entrenar.")
