import os
import sys
import multiprocessing
from functools import partial
from PIL import Image, ImageFilter, ImageOps

# Global flag for HEIF support
HEIF_SUPPORT = False

# Try to import pillow-heif
try:
    import pillow_heif
    pillow_heif.register_heif_opener()
    HEIF_SUPPORT = True
except ImportError:
    print("Warning: pillow-heif not installed. HEIF/HEIC support will be limited.")
    print("Install it with: pip install pillow-heif")

# Global Constants
INSTA_WIDTH_HORIZONTAL = 4096   # Width 5:4
INSTA_HEIGHT_HORIZONTAL = 3277  # Height 5:4
INSTA_WIDTH_VERTICAL = 3277     # Width 4:5
INSTA_HEIGHT_VERTICAL = 4096    # Height 4:5
BLUR_VALUE = 100

def correct_image_orientation(image):
    """
    Correct image orientation using EXIF data
    """
    try:
        return ImageOps.exif_transpose(image)
    except Exception as e:
        print(f"Error correcting orientation: {e}")
        return image

def get_image_without_metadata(image_path):
    """
    Open image, correct orientation, and strip metadata

    Args:
        image_path (str): Path to the input image

    Returns:
        PIL.Image.Image: Image with minimal metadata
    """
    try:
        with Image.open(image_path) as img:
            # Correct orientation before processing
            img = correct_image_orientation(img)

            # Convert to RGB to remove alpha and simplify processing
            img = img.convert("RGB")

            # Create a copy without metadata
            img_copy = Image.new("RGB", img.size)
            img_copy.paste(img)

            return img_copy
    except Exception as e:
        print(f"Error processing {image_path}: {e}")
        raise

def process_single_image(output_folder, image_path):
    """
    Process a single image for Instagram

    Args:
        output_folder (str): Destination folder for processed images
        image_path (str): Path to input image
    """
    try:
        # Open image and strip metadata
        original = get_image_without_metadata(image_path)

        # Get original dimensions
        orig_width, orig_height = original.size

        if orig_width > orig_height:
            # Horizontal image (5:4) with bands above and below
            scale = INSTA_WIDTH_HORIZONTAL / orig_width
            new_width = INSTA_WIDTH_HORIZONTAL
            new_height = int(orig_height * scale)

            resized_original = original.resize((new_width, new_height), Image.LANCZOS)

            # Create blurred background
            background = original.resize((INSTA_WIDTH_HORIZONTAL, INSTA_HEIGHT_HORIZONTAL), Image.LANCZOS)
            background = background.filter(ImageFilter.GaussianBlur(BLUR_VALUE))

            # Center resized image on background
            x_offset = 0
            y_offset = (INSTA_HEIGHT_HORIZONTAL - new_height) // 2
            background.paste(resized_original, (x_offset, y_offset))

        else:
            # Vertical image (4:5) with side bands
            scale = INSTA_HEIGHT_VERTICAL / orig_height
            new_height = INSTA_HEIGHT_VERTICAL
            new_width = int(orig_width * scale)

            resized_original = original.resize((new_width, new_height), Image.LANCZOS)

            # Create blurred background
            background = original.resize((INSTA_WIDTH_VERTICAL, INSTA_HEIGHT_VERTICAL), Image.LANCZOS)
            background = background.filter(ImageFilter.GaussianBlur(BLUR_VALUE))

            # Center resized image on background
            x_offset = (INSTA_WIDTH_VERTICAL - new_width) // 2
            y_offset = 0
            background.paste(resized_original, (x_offset, y_offset))

        # Generate output filename
        base_name, _ = os.path.splitext(os.path.basename(image_path))
        output_filename = f"{base_name}_uncropped.jpg"
        output_path = os.path.join(output_folder, output_filename)

        # Save the processed image with minimal metadata
        background.save(output_path, "JPEG", quality=90, optimize=True)
        print(f"Image saved to: {output_path}")

    except Exception as e:
        print(f"Error processing {image_path}: {str(e)}")

def process_images_in_folder(input_folder, output_folder, num_processes=None):
    """
    Process all images in a folder in parallel

    Args:
        input_folder (str): Source folder with images
        output_folder (str): Destination folder for processed images
        num_processes (int, optional): Number of parallel processes
    """
    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Determine supported extensions
    supported_extensions = ['.jpg', '.jpeg', '.png']
    if HEIF_SUPPORT:
        supported_extensions.extend(['.heic', '.heif'])

    # Get list of image files
    image_files = [
        os.path.join(input_folder, filename)
        for filename in os.listdir(input_folder)
        if os.path.isfile(os.path.join(input_folder, filename))
           and any(filename.lower().endswith(ext) for ext in supported_extensions)
    ]

    # Warn if no HEIF support and HEIF files are present
    heif_files = [f for f in image_files if f.lower().endswith(('.heic', '.heif'))]
    if heif_files and not HEIF_SUPPORT:
        print("WARNING: HEIF/HEIC files detected, but pillow-heif is not installed.")
        print("These files will be skipped. Install pillow-heif to process them.")
        image_files = [f for f in image_files if not f.lower().endswith(('.heic', '.heif'))]

    # Use multiprocessing to process images in parallel
    if num_processes is None:
        num_processes = os.cpu_count()

    # Use Pool for parallel processing
    with multiprocessing.Pool(processes=num_processes) as pool:
        # Use partial to create a picklable function with fixed output_folder
        process_func = partial(process_single_image, output_folder)

        # Map the processing function to all image files
        pool.map(process_func, image_files)

def main():
    # Customize these paths as needed
    INPUT_FOLDER = r"C:\Users\Antonio Montefusco\Desktop\Foto Sony\Editate\Evento Nocera Cicalesi"
    OUTPUT_FOLDER = "cartella_output"

    # Process images using all available CPU cores
    process_images_in_folder(INPUT_FOLDER, OUTPUT_FOLDER)

if __name__ == "__main__":
    main()
