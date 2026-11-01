import os, random
from PIL import Image, ImageDraw, ImageFont

ROOT = r"D:\Documents\Proyecto predeterminado\yolo_monedas_colombia"
IMG_TRAIN = os.path.join(ROOT, "data", "images", "train")
IMG_VAL = os.path.join(ROOT, "data", "images", "val")
LBL_TRAIN = os.path.join(ROOT, "data", "labels", "train")
LBL_VAL = os.path.join(ROOT, "data", "labels", "val")

CLASSES = [
 "moneda_20_antigua","moneda_50_antigua","moneda_50_nueva",
 "moneda_100_antigua","moneda_100_nueva","moneda_200_antigua",
 "moneda_200_nueva","moneda_500_antigua","moneda_500_nueva",
 "moneda_1000_antigua","moneda_1000_nueva",
]
# color palette per class (coin face color)
COLORS = {
 0:(180,140,90),1:(190,150,100),2:(200,160,110),
 3:(170,130,80),4:(210,170,120),5:(160,120,70),
 6:(195,155,105),7:(150,110,60),8:(205,165,115),
 9:(175,135,85),10:(215,175,125),
}

W,H = 640,640

def make_coin(img, cls, cx, cy, r):
    draw = ImageDraw.Draw(img)
    color = COLORS[cls]
    # outer circle
    draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=color, outline=(80,60,40), width=3)
    # inner ring for bimetallic high values
    if cls in (8,10):
        draw.ellipse([cx-r//2, cy-r//2, cx+r//2, cy+r//2], fill=(220,190,140), outline=(80,60,40), width=2)
    # text denomination
    try:
        font = ImageFont.truetype("arial.ttf", max(12, r//3))
    except:
        font = ImageFont.load_default()
    label = CLASSES[cls].split('_')[1].upper()
    draw.text((cx, cy), label, fill=(40,30,20), font=font, anchor="mm")

def gen_one(path_img, path_lbl):
    # random background
    bg_color = (random.randint(40,120), random.randint(40,120), random.randint(40,120))
    img = Image.new("RGB", (W,H), bg_color)
    # add noise texture
    draw = ImageDraw.Draw(img)
    for _ in range(200):
        x,y = random.randrange(W), random.randrange(H)
        draw.point((x,y), fill=(random.randint(0,255),)*3)
    labels = []
    ncoins = random.randint(1,4)
    placed = []
    for _ in range(ncoins):
        cls = random.randrange(len(CLASSES))
        r = random.randint(40, 90)
        # try place without overlap
        for attempt in range(20):
            cx = random.randint(r+5, W-r-5)
            cy = random.randint(r+5, H-r-5)
            ok = True
            for (px,py,pr) in placed:
                if (cx-px)**2+(cy-py)**2 < (r+pr+10)**2:
                    ok = False; break
            if ok:
                break
        else:
            continue
        placed.append((cx,cy,r))
        make_coin(img, cls, cx, cy, r)
        # YOLO label normalized
        x1,y1 = cx-r, cy-r
        x2,y2 = cx+r, cy+r
        xc = (x1+x2)/2/W
        yc = (y1+y2)/2/H
        bw = (x2-x1)/W
        bh = (y2-y1)/H
        labels.append(f"{cls} {xc:.6f} {yc:.6f} {bw:.6f} {bh:.6f}")
    img.save(path_img)
    with open(path_lbl,"w") as f:
        f.write("\n".join(labels))

def main(n_train=400, n_val=80):
    for i in range(n_train):
        gen_one(os.path.join(IMG_TRAIN, f"syn_{i:04d}.jpg"),
                os.path.join(LBL_TRAIN, f"syn_{i:04d}.txt"))
    for i in range(n_val):
        gen_one(os.path.join(IMG_VAL, f"syn_{i:04d}.jpg"),
                os.path.join(LBL_VAL, f"syn_{i:04d}.txt"))
    print("generated", n_train, n_val)

if __name__ == "__main__":
    main()
