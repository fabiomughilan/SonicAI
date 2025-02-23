import random
from urllib.parse import quote

def generate_meme_image(text):
    """
    Generates a meme image based on the given text.
    """
    # URL encode text to avoid issues with special characters
    encoded_text = quote(text)

    meme_templates = [
        f"https://api.memegen.link/images/ds/{encoded_text}.png",
        f"https://api.memegen.link/images/buzz/{encoded_text}.png",
        f"https://api.memegen.link/images/cheems/{encoded_text}.png"
    ]
    
    # Randomly select a meme template
    image_url = random.choice(meme_templates)
    
    return image_url
