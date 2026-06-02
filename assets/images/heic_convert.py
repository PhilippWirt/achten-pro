import pillow_heif
from PIL import Image
import os

pillow_heif.register_heif_opener()

src = "von vorne.HEIC"
img = Image.open(src)
print(f"Mode: {img.mode}, Size: {img.size}")

# Sicherstellen dass RGB (kein Graustufenproblem wie bei von links)
if img.mode != "RGB":
    img = img.convert("RGB")
    print(f"Konvertiert zu RGB")

w, h = img.size

# LinkedIn-Profile-Zuschnitt: Kopf bis Schultern, ~4:5 Format
# Bei typischen Portrait-Fotos (hochkant): Kopf ~10-20% von oben, Schultern ~40-50%
# Wir nehmen: y von 3% bis 55% (vertikal), horizontal zentriert
# Ergibt Bereich: Haarspitze knapp drüber bis Schultern gut sichtbar

top_pct    = 0.03   # 3% vom oberen Rand
bottom_pct = 0.55   # 55% — Schultern sichtbar

crop_h = int((bottom_pct - top_pct) * h)
crop_w = int(crop_h * 4 / 5)   # 4:5 Hochformat

# Horizontal zentrieren
left = max(0, (w - crop_w) // 2)
right = min(w, left + crop_w)
top = int(top_pct * h)
bottom = int(bottom_pct * h)

print(f"Zuschnitt: left={left}, top={top}, right={right}, bottom={bottom}")
print(f"Ausgabegröße: {right-left}x{bottom-top}px")

cropped = img.crop((left, top, right, bottom))

# Auf max 1000px Breite herunterskalieren (LinkedIn reicht 400px)
max_dim = 1000
if cropped.width > max_dim:
    scale = max_dim / cropped.width
    new_size = (max_dim, int(cropped.height * scale))
    cropped = cropped.resize(new_size, Image.LANCZOS)
    print(f"Skaliert auf: {new_size}")

out = "von_vorne_profil.jpg"
cropped.save(out, "JPEG", quality=90)
print(f"Gespeichert: {out} ({os.path.getsize(out)//1024} KB)")
