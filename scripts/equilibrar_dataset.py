"""Crea dataset_balanceado duplicando las clases minoritarias en train.

Las clases con menos ejemplos (100_pesos, 50_pesos, 100_pesos_nueva,
200_pesos_nueva) se repiten para que el modelo no las confunda con las
clases dominantes. train se modifica; val y test quedan intactos.
"""

import os
import glob
import shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ORIGEN = os.path.join(ROOT, "dataset_final")
DEST = os.path.join(ROOT, "dataset_balanceado")

# clase YOLO -> copias adicionales en train
REPETICIONES = {
    1: 4,  # 100_pesos (antigua): sigue siendo la mas escasa
    2: 2,  # 100_pesos_nueva
}

NOMBRES = [
    "1000_pesos", "100_pesos", "100_pesos_nueva",
    "200_pesos", "200_pesos_nueva", "500_pesos",
    "500_pesos_nueva", "50_pesos", "50_pesos_nueva",
]

if os.path.exists(DEST):
    print("Reconstruyendo:", DEST)
    shutil.rmtree(DEST)

for split in ("train", "val", "test"):
    for carpeta in ("images", "labels"):
        os.makedirs(os.path.join(DEST, carpeta, split), exist_ok=True)

conteo = {}
for split in ("train", "val", "test"):
    for img in sorted(glob.glob(os.path.join(ORIGEN, "images", split, "*"))):
        base = os.path.basename(img)
        stem = os.path.splitext(base)[0]
        ext = os.path.splitext(base)[1]
        lbl = os.path.join(ORIGEN, "labels", split, stem + ".txt")

        shutil.copy2(img, os.path.join(DEST, "images", split, base))
        if os.path.exists(lbl):
            shutil.copy2(lbl, os.path.join(DEST, "labels", split, stem + ".txt"))

        clase = None
        if os.path.exists(lbl):
            with open(lbl, encoding="utf-8") as f:
                primera = f.readline().split()
            if primera:
                clase = int(primera[0])

        conteo[clase] = conteo.get(clase, 0) + 1

        if split == "train" and clase in REPETICIONES:
            for k in range(1, REPETICIONES[clase] + 1):
                nuevo = f"{stem}_dup{k}{ext}"
                shutil.copy2(img, os.path.join(DEST, "images", "train", nuevo))
                if os.path.exists(lbl):
                    shutil.copy2(lbl, os.path.join(DEST, "labels", "train", f"{stem}_dup{k}.txt"))
                conteo[clase] += 1

yaml = (
    "path: '" + DEST.replace("\\", "/") + "'\n"
    "train: images/train\n"
    "val: images/val\n"
    "test: images/test\n"
    f"nc: {len(NOMBRES)}\n"
    "names:\n"
    + "".join(f"  {i}: {n}\n" for i, n in enumerate(NOMBRES))
)
with open(os.path.join(DEST, "data.yaml"), "w", encoding="utf-8") as f:
    f.write(yaml)

print("Dataset balanceado:", DEST)
for clase in sorted(conteo):
    nombre = NOMBRES[clase] if clase is not None else "sin clase"
    print(f"  {clase} {nombre}: {conteo[clase]}")
