"""Combina el dataset de Roboflow con las capturas del montaje real.

Resultado: dataset_final/ con divisiones train/val/test y data.yaml de 9 clases.
"""

import os
import glob
import random
import shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ROBO = os.path.join(ROOT, "dataset_9clases")
REAL = os.path.join(ROOT, "dataset_reposicion")
DEST = os.path.join(ROOT, "dataset_final")

SEED = 42
random.seed(SEED)

NOMBRES = [
    "1000_pesos", "100_pesos", "100_pesos_nueva",
    "200_pesos", "200_pesos_nueva", "500_pesos",
    "500_pesos_nueva", "50_pesos", "50_pesos_nueva",
]

if os.path.exists(DEST):
    print("Reconstruyendo:", DEST)
    shutil.rmtree(DEST)

for split in ("train", "val", "test"):
    os.makedirs(os.path.join(DEST, "images", split), exist_ok=True)
    os.makedirs(os.path.join(DEST, "labels", split), exist_ok=True)

conteo = {s: 0 for s in ("train", "val", "test")}
roboflow_count = 0

# 1) Copiar el dataset de Roboflow manteniendo su division original.
for split in ("train", "val", "test"):
    for img in sorted(glob.glob(os.path.join(ROBO, "images", split, "*"))):
        shutil.copy2(img, os.path.join(DEST, "images", split, os.path.basename(img)))
        nombre = os.path.splitext(os.path.basename(img))[0] + ".txt"
        lbl = os.path.join(ROBO, "labels", split, nombre)
        if os.path.exists(lbl):
            shutil.copy2(lbl, os.path.join(DEST, "labels", split, nombre))
        conteo[split] += 1
        roboflow_count += 1

# 2) Dividir las capturas reales 80/10/10.
reales = []
for clase in NOMBRES:
    for img in sorted(glob.glob(os.path.join(REAL, "images", clase, "*.jpg"))):
        reales.append((img, clase))

random.shuffle(reales)
n = len(reales)
n_train = int(n * 0.80)
n_val = int(n * 0.10)

asignados = (
    [("train", x) for x in reales[:n_train]]
    + [("val", x) for x in reales[n_train:n_train + n_val]]
    + [("test", x) for x in reales[n_train + n_val:]]
)

for split, (img, clase) in asignados:
    base = os.path.basename(img)
    shutil.copy2(img, os.path.join(DEST, "images", split, base))
    lbl_origen = os.path.join(REAL, "labels", clase, base.replace(".jpg", ".txt"))
    if os.path.exists(lbl_origen):
        shutil.copy2(lbl_origen, os.path.join(DEST, "labels", split, base.replace(".jpg", ".txt")))
    conteo[split] += 1

# 3) data.yaml
yaml = (
    "path: '" + DEST.replace("\\", "/") + "'\n"
    "train: images/train\n"
    "val: images/val\n"
    "test: images/test\n"
    f"nc: {len(NOMBRES)}\n"
    "names:\n"
    + "".join(f"  {i}: {name}\n" for i, name in enumerate(NOMBRES))
)
with open(os.path.join(DEST, "data.yaml"), "w", encoding="utf-8") as f:
    f.write(yaml)

print("Dataset final:", DEST)
print("Imagenes de Roboflow:", roboflow_count)
print("Capturas reales:", n)
for split, c in conteo.items():
    print(f"  {split}: {c} imagenes")
