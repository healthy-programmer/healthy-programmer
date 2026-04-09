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