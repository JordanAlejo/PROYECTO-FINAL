"""Prepara el dataset original de Roboflow (9 clases) para YOLO detection.

Fuente: la carpeta exportada por Roboflow que contiene train/images y train/labels.
Las etiquetas de segmentacion (poligonos) se convierten a cajas delimitadoras
para la tarea de deteccion. Se conservan las 9 clases originales.
"""

from pathlib import Path
import random
import shutil

ROOT = Path(__file__).resolve().parent.parent

SOURCE = Path(r"C:\Users\Cocot\Desktop\My First Project.v1i.yolov8\train")
DEST = ROOT / "dataset_9clases"

SEED = 42
random.seed(SEED)

CLASS_NAMES = [
    "1000_pesos",
    "100_pesos",
    "100_pesos_nueva",
    "200_pesos",
    "200_pesos_nueva",
    "500_pesos",
    "500_pesos_nueva",
    "50_pesos",
    "50_pesos_nueva",
]

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}


def poligono_a_caja(valores):
    """Convierte coords normalizadas x1,y1,x2,y2,... a x_centro,y_centro,ancho,alto."""
    if len(valores) < 6 or len(valores) % 2 != 0:
        raise ValueError(f"Cantidad de coordenadas invalida: {len(valores)}")

    if not all(0.0 <= v <= 1.0 for v in valores):
        raise ValueError("Coordenadas fuera del rango 0-1")

    xs = valores[0::2]
    ys = valores[1::2]
    x_min, x_max = min(xs), max(xs)
    y_min, y_max = min(ys), max(ys)
    ancho = x_max - x_min
    alto = y_max - y_min

    if ancho <= 0 or alto <= 0:
        raise ValueError("Poligono sin area")

    xc = (x_min + x_max) / 2.0
    yc = (y_min + y_max) / 2.0
    return xc, yc, ancho, alto


print("=" * 55)
print("PREPARANDO DATASET ROBOFLOW - 9 CLASES")
print("=" * 55)
print("Fuente:", SOURCE)
print("Destino:", DEST)

images_dir = SOURCE / "images"
labels_dir = SOURCE / "labels"

if not images_dir.is_dir() or not labels_dir.is_dir():
    raise FileNotFoundError(f"No se encontraron images/labels en {SOURCE}")

images = sorted(
    f for f in images_dir.iterdir()
    if f.is_file() and f.suffix.lower() in IMAGE_EXTENSIONS
)

records = []
missing = []
conversiones = 0
cajas_directas = 0

for image_path in images:
    label_path = labels_dir / f"{image_path.stem}.txt"
    if not label_path.is_file():
        missing.append(image_path.name)
        continue

    new_lines = []
    for numero, linea in enumerate(
        label_path.read_text(encoding="utf-8-sig").splitlines(), start=1
    ):
        if not linea.strip():
            continue

        partes = linea.split()
        clase = int(partes[0])
        coords = [float(v) for v in partes[1:]]

        if clase not in range(len(CLASS_NAMES)):
            raise ValueError(f"Clase desconocida {clase} en {label_path.name}")

        if len(coords) == 4:
            xc, yc, ancho, alto = coords
            cajas_directas += 1
        else:
            xc, yc, ancho, alto = poligono_a_caja(coords)
            conversiones += 1

        new_lines.append(
            f"{clase} {xc:.6f} {yc:.6f} {ancho:.6f} {alto:.6f}"
        )

    records.append((image_path, new_lines))

if missing:
    raise RuntimeError(f"{len(missing)} imagenes sin etiqueta: {missing[:5]}")

print(f"\nImagenes: {len(records)}")
print("Poligonos convertidos a cajas:", conversiones)
print("Cajas directas:", cajas_directas)

random.shuffle(records)
total = len(records)
n_train = int(total * 0.80)
n_val = int(total * 0.10)

splits = {
    "train": records[:n_train],
    "val": records[n_train:n_train + n_val],
    "test": records[n_train + n_val:],
}

for nombre, datos in splits.items():
    print(f"{nombre}: {len(datos)} imagenes")

if DEST.exists():
    raise FileExistsError(f"Ya existe {DEST}. Renombralo o borralo antes de continuar.")

for nombre, datos in splits.items():
    out_img = DEST / "images" / nombre
    out_lbl = DEST / "labels" / nombre
    out_img.mkdir(parents=True, exist_ok=True)
    out_lbl.mkdir(parents=True, exist_ok=True)

    for image_path, new_lines in datos:
        shutil.copy2(image_path, out_img / image_path.name)
        contenido = "\n".join(new_lines)
        if contenido:
            contenido += "\n"
        (out_lbl / f"{image_path.stem}.txt").write_text(contenido, encoding="utf-8")

yaml_path = DEST / "data.yaml"
yaml_path.write_text(
    "path: '"
    + DEST.resolve().as_posix()
    + "'\n"
    + "train: images/train\n"
    + "val: images/val\n"
    + "test: images/test\n"
    + f"nc: {len(CLASS_NAMES)}\n"
    + "names:\n"
    + "".join(f"  {i}: {name}\n" for i, name in enumerate(CLASS_NAMES)),
    encoding="utf-8",
)

print("\nDataset listo en:", DEST)
print("YAML:", yaml_path)
