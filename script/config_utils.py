import os
import json

# Load all GIF files, selected GIFs, and general configuration from the config file.
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

# Save the general configuration and selected GIFs to the config file.
def save_config_to_file(config_path, general_config, selected_gifs):
    """
    Save the general configuration and selected GIFs to the given config_path.
    """
    config_data = general_config.copy()
    config_data["selected_gifs"] = list(selected_gifs)
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config_data, f, indent=2)

# Return a list of active GIF file paths, filtered by selected_gifs and optionally excluding the current GIF.
def get_active_gif_list(all_gif_files, selected_gifs, current_gif=None):
    """
    Return a list of GIF file paths to use, based on selected_gifs (by basename).
    If selected_gifs is empty, fallback to all_gif_files.
    Optionally exclude current_gif from the result.
    """
    if not selected_gifs:
        # Fallback: use all GIFs by basename
        selected_gif_names = {os.path.basename(f) for f in all_gif_files}
    else:
        selected_gif_names = set(selected_gifs)
    result = [f for f in all_gif_files if os.path.basename(f) in selected_gif_names]
    if current_gif is not None:
        result = [f for f in result if f != current_gif]
    return result