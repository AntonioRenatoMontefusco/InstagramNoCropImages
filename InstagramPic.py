import os
from PIL import Image, ImageFilter, ExifTags

# Variabili globali
INSTA_WIDTH = 1080
INSTA_HEIGHT = 1350
INPUT_FOLDER = r"C:\Users\Antonio Montefusco\Desktop\Foto Sony\Editate\Roberta"
OUTPUT_FOLDER = "cartella_output"
BLUR_VALUE=100
def correct_exif_orientation(image):
    try:
        # Estrai i metadati EXIF
        exif = image._getexif()
        if exif is not None:
            for tag, value in exif.items():
                if tag == 274:  # 274 è il tag per l'orientamento
                    if value == 3:
                        image = image.rotate(180, expand=True)
                    elif value == 6:
                        image = image.rotate(270, expand=True)
                    elif value == 8:
                        image = image.rotate(90, expand=True)
                    break
    except (AttributeError, KeyError, IndexError):
        # Se l'immagine non ha metadati EXIF o il tag di orientamento non è presente
        pass
    return image

def format_for_instagram(image_path, output_path):
    # Apri l'immagine originale
    original = Image.open(image_path)

    # Correggi l'orientamento dell'immagine in base ai metadati EXIF
    original = correct_exif_orientation(original)

    # Crea una copia sfocata dell'immagine per lo sfondo
    background = original.copy()

    # Dimensioni dell'immagine originale
    orig_width, orig_height = original.size

    # Verifica se l'immagine è verticale o orizzontale
    if orig_width > orig_height:
        # Orizzontale: adattiamo al formato 4:5 orizzontale
        scale = INSTA_WIDTH / orig_width
        new_width = INSTA_WIDTH
        new_height = int(orig_height * scale)

        # Ridimensiona l'immagine originale mantenendo il rapporto d'aspetto
        resized_original = original.resize((new_width, new_height), Image.LANCZOS)

        # Adatta lo sfondo orizzontale
        background = background.resize((INSTA_WIDTH, INSTA_HEIGHT), Image.LANCZOS)
        background = background.filter(ImageFilter.GaussianBlur(BLUR_VALUE))

    else:
        # Verticale: adattiamo al formato 4:5 verticale
        scale = INSTA_HEIGHT / orig_height
        new_height = INSTA_HEIGHT
        new_width = int(orig_width * scale)

        # Ridimensiona l'immagine originale mantenendo il rapporto d'aspetto
        resized_original = original.resize((new_width, new_height), Image.LANCZOS)

        # Adatta lo sfondo verticale
        background = background.resize((INSTA_WIDTH, INSTA_HEIGHT), Image.LANCZOS)
        background = background.filter(ImageFilter.GaussianBlur(100))

    # Calcola le coordinate per centrare l'immagine sullo sfondo
    x_offset = (INSTA_WIDTH - new_width) // 2
    y_offset = (INSTA_HEIGHT - new_height) // 2

    # Incolla l'immagine ridimensionata sullo sfondo sfocato
    background.paste(resized_original, (x_offset, y_offset))

    # Aggiungi "_uncropped" al nome del file prima dell'estensione
    base_name, ext = os.path.splitext(os.path.basename(image_path))
    output_filename = f"{base_name}_uncropped{ext}"

    # Costruisci il percorso completo per il salvataggio
    output_path = os.path.join(OUTPUT_FOLDER, output_filename)

    background.save(output_path, "JPEG")
    print(f"Immagine salvata in: {output_path}")

def process_images_in_folder(input_folder, output_folder):
    # Crea la cartella di output se non esiste
    os.makedirs(output_folder, exist_ok=True)

    # Itera su tutti i file nella cartella di input
    for filename in os.listdir(input_folder):
        input_path = os.path.join(input_folder, filename)

        # Controlla se il file è un'immagine
        if os.path.isfile(input_path) and filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            output_path = os.path.join(output_folder, filename)
            try:
                format_for_instagram(input_path, output_path)
            except Exception as e:
                print(f"Errore durante l'elaborazione di {filename}: {e}")

def main():
    # Elabora tutte le immagini nella cartella di input
    process_images_in_folder(INPUT_FOLDER, OUTPUT_FOLDER)

if __name__ == "__main__":
    main()
