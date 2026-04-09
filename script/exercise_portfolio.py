import os

# Directory containing GIF images and path to the reminder-data markdown.
GIF_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../exercise/images')
DATA_MD = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../exercise/reminder-data.md')

# Parse a markdown file with GIF descriptions and return a mapping of GIF names to their details.
def load_gif_descriptions(data_md_path):
    """
    Parse a markdown file with GIF descriptions and return a mapping.

    Args:
        data_md_path (str): Path to the markdown file.

    Returns:
        dict: Mapping of gif name to description, area, action, and category.
    """
    mapping = {}
    current_gif = None
    area = None
    action = None
    category = None
    desc_lines = []
    with open(data_md_path, encoding='utf-8') as mdfile:
        for line in mdfile:
            line = line.rstrip('\n')
            if line.startswith('## '):
                if current_gif:
                    mapping[current_gif] = {
                        "description": '\n'.join(desc_lines).strip(),
                        "area": area,
                        "action": action,
                        "category": category
                    }
                current_gif = line[3:].strip()
                area = None
                action = None
                category = None
                desc_lines = []
            elif current_gif is not None:
                if line.startswith('**Area:**'):
                    area = line.split('**Area:**', 1)[1].strip().strip()
                elif line.startswith('**Action:**'):
                    action = line.split('**Action:**', 1)[1].strip().strip()
                elif line.startswith('**Category:**'):
                    category = line.split('**Category:**', 1)[1].strip().strip()
                elif line.strip() == '':
                    continue
                else:
                    desc_lines.append(line)
        # Add last gif
        if current_gif:
            mapping[current_gif] = {
                "description": '\n'.join(desc_lines).strip(),
                "area": area,
                "action": action,
                "category": category
            }
    return mapping

# Retrieve all GIF files that are referenced in the reminder-data markdown.
def get_gif_files():
    gif_desc_map = load_gif_descriptions(DATA_MD)
    csv_gifs = set(gif_desc_map.keys())
    return [
        os.path.join(GIF_DIR, f)
        for f in os.listdir(GIF_DIR)
        if f.lower().endswith('.gif') and f in csv_gifs
    ]