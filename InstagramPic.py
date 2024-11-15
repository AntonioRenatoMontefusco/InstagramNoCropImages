import os
from PIL import Image, ImageFilter, ExifTags

# Variabili globali
INSTA_WIDTH_HORIZONTAL = 1350  # Larghezza 5:4
INSTA_HEIGHT_HORIZONTAL = 1080  # Altezza 5:4
INSTA_WIDTH_VERTICAL = 1080  # Larghezza 4:5
INSTA_HEIGHT_VERTICAL = 1350  # Altezza 4:5
INPUT_FOLDER = r"Input_directory"
OUTPUT_FOLDER = "Output_directory"
BLUR_VALUE = 100

def correct_exif_orientation(image):
    try:
        exif = image._getexif()
        if exif is not None:
            for tag, value in exif.items():
                if tag == 274:
                    if value == 3:
                        image = image.rotate(180, expand=True)
                    elif value == 6:
                        image = image.rotate(270, expand=True)
                    elif value == 8:
                        image = image.rotate(90, expand=True)
                    break
    except (AttributeError, KeyError, IndexError):
        pass
    return image

def format_for_instagram(image_path, output_path):
    original = Image.open(image_path)
    original = correct_exif_orientation(original)

    # Dimensioni dell'immagine originale
    orig_width, orig_height = original.size

    if orig_width > orig_height:
        # Immagine orizzontale (5:4) con bande sopra e sotto
        scale = INSTA_WIDTH_HORIZONTAL / orig_width
        new_width = INSTA_WIDTH_HORIZONTAL
        new_height = int(orig_height * scale)

        resized_original = original.resize((new_width, new_height), Image.LANCZOS)

        # Crea lo sfondo sfocato
        background = original.resize((INSTA_WIDTH_HORIZONTAL, INSTA_HEIGHT_HORIZONTAL), Image.LANCZOS)
        background = background.filter(ImageFilter.GaussianBlur(BLUR_VALUE))

        # Centra l'immagine ridimensionata sullo sfondo
        x_offset = 0
        y_offset = (INSTA_HEIGHT_HORIZONTAL - new_height) // 2
        background.paste(resized_original, (x_offset, y_offset))

    else:
        # Immagine verticale (4:5) con bande laterali
        scale = INSTA_HEIGHT_VERTICAL / orig_height
        new_height = INSTA_HEIGHT_VERTICAL
        new_width = int(orig_width * scale)

        resized_original = original.resize((new_width, new_height), Image.LANCZOS)

        # Crea lo sfondo sfocato
        background = original.resize((INSTA_WIDTH_VERTICAL, INSTA_HEIGHT_VERTICAL), Image.LANCZOS)
        background = background.filter(ImageFilter.GaussianBlur(BLUR_VALUE))

        # Centra l'immagine ridimensionata sullo sfondo
        x_offset = (INSTA_WIDTH_VERTICAL - new_width) // 2
        y_offset = 0
        background.paste(resized_original, (x_offset, y_offset))

    # Aggiungi "_uncropped" al nome del file prima dell'estensione
    base_name, ext = os.path.splitext(os.path.basename(image_path))
    output_filename = f"{base_name}_uncropped{ext}"
    output_path = os.path.join(OUTPUT_FOLDER, output_filename)

    background.save(output_path, "JPEG")
    print(f"Immagine salvata in: {output_path}")

def process_images_in_folder(input_folder, output_folder):
    os.makedirs(output_folder, exist_ok=True)
    for filename in os.listdir(input_folder):
        input_path = os.path.join(input_folder, filename)
        if os.path.isfile(input_path) and filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            output_path = os.path.join(output_folder, filename)
            try:
                format_for_instagram(input_path, output_path)
            except Exception as e:
                print(f"Errore durante l'elaborazione di {filename}: {e}")

def main():
    process_images_in_folder(INPUT_FOLDER, OUTPUT_FOLDER)

if __name__ == "__main__":
    main()
