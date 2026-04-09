import os
import json

def load_config_and_gifs(config_path, get_gif_files):
    """
    Load all GIF files, selected GIFs, and general configuration from the given config_path.
    get_gif_files: function to retrieve all available GIF files.
    Returns (all_gif_files, selected_gifs, general_config)
    """
    all_gif_files = get_gif_files()
    selected_gifs = set()
    general_config = {
        "interval": 30,
        "duration": 30,
        "position": "center",
        "working_hours": "8:00-16:30"
    }
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config_data = json.load(f)
                if isinstance(config_data, dict):
                    selected_gifs = set(config_data.get("selected_gifs", []))
                    for key in general_config:
                        if key in config_data:
                            general_config[key] = config_data[key]
                    # Ensure selected_gifs is included in general_config for downstream filtering
                    general_config["selected_gifs"] = list(selected_gifs)
                elif isinstance(config_data, list):
                    # Backward compatibility: old format
                    selected_gifs = set(config_data)
                    general_config["selected_gifs"] = list(selected_gifs)
        except Exception:
            pass
    return all_gif_files, selected_gifs, general_config

def save_config_to_file(config_path, general_config, selected_gifs):
    """
    Save the general configuration and selected GIFs to the given config_path.
    """
    config_data = general_config.copy()
    config_data["selected_gifs"] = list(selected_gifs)
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config_data, f, indent=2)