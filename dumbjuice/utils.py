from PIL import Image

def create_ico(png_path: str, ico_path: str):
    icon_sizes = [(512, 512), (256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (24, 24), (16, 16)]
    img = Image.open(png_path).convert("RGBA")
    img.save(ico_path, format='ICO', sizes=icon_sizes)
    print(f"ICO saved as {ico_path}")