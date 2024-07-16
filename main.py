import requests
import json
from typing import Tuple
from pydantic import BaseModel, Field, model_validator

from cat.log import log
from cat.experimental.form import form, CatForm


def generate_image_from_api(prompt: str, settings: dict) -> Tuple[str, Tuple[int, int]]:

    headers = {
        "Authorization": f"Bearer {settings['api_key']}",
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "quality": settings['quality'],
        "model": settings['model'],
        "prompt": prompt,
        "style": settings['style'],
        "size": settings['image_size']
    })
    req = requests.post(
        "https://api.openai.com/v1/images/generations", 
        headers=headers,
        data=data
    )
    res = req.json()

    image_url = res['data'][0]['url']
    size = settings['image_size'].split('x')
    size[0] = int(size[0])
    size[1] = int(size[1])

    return image_url, size



# data structure to fill up
class ImageGenerationPrompt(BaseModel):
    image_prompt: str

# forms let you control goal oriented conversations
@form
class ImageGenerationForm(CatForm):
    description = "Generate image"
    model_class = ImageGenerationPrompt
    start_examples = [
        "generate image",
        "create picture"
    ]
    stop_examples = [
        "stop image generation",
        "exit image",
        "don't want to create image"
    ]
    ask_confirm = True

    def submit(self, form_data):
        
        settings = self.cat.mad_hatter.get_plugin().load_settings()
        if settings == {}:
            log.error("No configuration found for MeowArt")
            return "You did not configure the API key for the image generation API!"
        
        prompt = form_data["image_prompt"]
        image, size = generate_image_from_api(prompt, settings)
 
        # TODO: It would be nice to add a button to download the original quality of the image
        return {
            "output": f"<img src='{image}' style='width: {int(size[0]) / 2}px; height: {int(size[1]) / 2}px;' alt='Generated image' />"
        }