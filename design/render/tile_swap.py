"""Swap the designer's grey marble for the owner's real travertine tile (image space, shading preserved)."""
import sys, numpy as np
from PIL import Image, ImageFilter
TEX = '/home/user/My-apartment/design/phase-1/img/travertine_tile_rect.jpg'

def swap(src, dst, tile_px=260):
    im = Image.open(src).convert('RGB'); W, H = im.size
    a = np.asarray(im).astype(float) / 255
    hsv = np.asarray(im.convert('HSV')).astype(float) / 255; s, v = hsv[..., 1], hsv[..., 2]
    m = ((s < 0.14) & (v > 0.25) & (v < 0.97)).astype('uint8') * 255
    m = Image.fromarray(m).filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.MinFilter(9)).filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(1.2))
    m = np.asarray(m).astype(float)[..., None] / 255
    t = Image.open(TEX).convert('RGB'); k = tile_px / t.size[0]   # one real 60x120 tile, laid vertically
    t = t.resize((int(t.size[0] * k), int(t.size[1] * k)), Image.LANCZOS)
    big = Image.new('RGB', (W, H))
    for x in range(0, W, t.size[0]):
        for y in range(0, H, t.size[1]): big.paste(t, (x, y))
    tex = np.asarray(big).astype(float) / 255
    mu = tex.reshape(-1, 3).mean(0); tex = mu + 0.65 * (tex - mu); tex = tex * np.array([1.05, 1.0, 0.93])
    tl = tex @ [0.299, 0.587, 0.114]; tex = tex / tl.mean()          # texture colour, normalised to mean lum 1
    L = a @ [0.299, 0.587, 0.114]
    shade = np.asarray(Image.fromarray((L * 255).astype('uint8')).filter(ImageFilter.GaussianBlur(6))).astype(float) / 255
    detail = L / np.maximum(shade, 1e-3)                               # keeps joints and small shadows
    new = np.clip(tex * (shade * 1.02)[..., None] * np.clip(detail, 0.6, 1.2)[..., None], 0, 1)
    out = a * (1 - m) + new * m
    Image.fromarray((out * 255).astype('uint8')).save(dst, quality=92)

if __name__ == '__main__':
    swap(sys.argv[1], sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 360)
