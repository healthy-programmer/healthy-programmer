import os
from PIL import Image

# Directory containing original GIFs
GIF_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../exercise/images')
# Directory to save resized GIFs
RESIZED_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../exercise/images/resized')

# Target thumbnail size (height, width)
THUMB_HEIGHT = 74

def resize_gif(gif_path, output_path, thumb_height=THUMB_HEIGHT):
    try:
        img = Image.open(gif_path)
        orig_width, orig_height = img.size
        thumb_width = int(orig_width * (thumb_height / orig_height))
        thumb_size = (thumb_width, thumb_height)
        frames = []
        durations = []
        try:
            while True:
                frame = img.copy().resize(thumb_size, Image.LANCZOS)
                frames.append(frame)
                durations.append(img.info.get('duration', 100))
                img.seek(len(frames))
        except EOFError:
            pass
        if frames:
            frames[0].save(
                output_path,
                save_all=True,
                append_images=frames[1:],
                duration=durations,
                loop=0,
                optimize=True
            )
            print(f"Resized: {os.path.basename(gif_path)} -> {output_path}")
        else:
            print(f"Failed to resize: {gif_path}")
    except Exception as e:
        print(f"Error resizing {gif_path}: {e}")

def main():
    if not os.path.exists(RESIZED_DIR):
        os.makedirs(RESIZED_DIR)
    gif_files = [f for f in os.listdir(GIF_DIR) if f.lower().endswith('.gif')]
    for gif_name in gif_files:
        gif_path = os.path.join(GIF_DIR, gif_name)
        output_path = os.path.join(RESIZED_DIR, gif_name)
        resize_gif(gif_path, output_path)

if __name__ == "__main__":
    main()