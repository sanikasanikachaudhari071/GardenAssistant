import base64 #this lib encode and decode binarry data like image
from pathlib import Path #helps with path for the image
from typing import Dict

class ImageHandler:
    @staticmethod
    def encode_image(image_path: str) -> Dict:
        path = Path(image_path)
        if not path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")
            
        with open(path, "rb") as image_file:
            encoded = base64.b64encode(image_file.read()).decode('utf-8')
            return {
                "url": f"data:image/{path.suffix[1:]};base64,{encoded}"
            }

    @staticmethod
    def create_message(query: str, image_path: str) -> Dict:
        return {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": query
                },
                {
                    "type": "image_url",
                    "image_url": ImageHandler.encode_image(image_path)
                }
            ]
        }

# Usage example
# image_path = "images/plant.jpg"
# message = ImageHandler.create_message("What plant is this?", image_path)