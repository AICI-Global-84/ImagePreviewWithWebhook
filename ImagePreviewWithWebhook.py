import os
import json
import requests
from PIL import Image
from PIL.PngImagePlugin import PngInfo
import numpy as np
import time

import folder_paths
from server import PromptServer

class ImagePreviewWithWebhook:
    def __init__(self):
        self.output_dir = folder_paths.get_output_directory()
        self.type = "output"
        self.prefix_append = ""
        self.compress_level = 4

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "images": ("IMAGE", {"tooltip": "The images to save and send to webhook."}),
                "filename_prefix": ("STRING", {"default": "ComfyUI", "tooltip": "The prefix for the file to save."}),
                "webhook_url": ("STRING", {"default": "https://your-n8n-webhook-url.com", "tooltip": "The n8n webhook URL to send the image information to."})
            },
            "hidden": {
                "prompt": "PROMPT",
                "extra_pnginfo": "EXTRA_PNGINFO"
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("image_url",)
    FUNCTION = "process_and_send_image"
    OUTPUT_NODE = True
    CATEGORY = "image"

    def upload_to_postimage(self, image_path):
        """Upload image to PostImage and return the direct URL."""
        post_image_url = "https://postimages.org/json/rr"
        files = {"file": open(image_path, "rb")}
        data = {
            "expiry": "0",  # No expiration
            "upload_session": "123",  # Mocked session ID
        }
        try:
            response = requests.post(post_image_url, files=files, data=data)
            response.raise_for_status()
            json_response = response.json()
            return json_response['url']
        except requests.RequestException as e:
            print(f"Failed to upload image to PostImage: {e}")
            return None

    def process_and_send_image(self, images, filename_prefix="ComfyUI", webhook_url="", prompt=None, extra_pnginfo=None):
        filename_prefix += self.prefix_append
        full_output_folder, filename, counter, subfolder, filename_prefix = folder_paths.get_save_image_path(filename_prefix, self.output_dir, images[0].shape[1], images[0].shape[0])
        
        results = []
        for batch_number, image in enumerate(images):
            i = 255. * image.cpu().numpy()
            img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))
            
            metadata = PngInfo()
            if prompt is not None:
                metadata.add_text("prompt", json.dumps(prompt))
            if extra_pnginfo is not None:
                for x in extra_pnginfo:
                    metadata.add_text(x, json.dumps(extra_pnginfo[x]))

            filename_with_batch_num = filename.replace("%batch_num%", str(batch_number))
            file = f"{filename_with_batch_num}_{counter:05}_.png"
            full_path = os.path.join(full_output_folder, file)
            img.save(full_path, pnginfo=metadata, compress_level=self.compress_level)

            # Upload image to PostImage
            public_image_url = self.upload_to_postimage(full_path)
            if not public_image_url:
                print(f"Failed to upload image for batch {batch_number}. Skipping...")
                continue

            # Send webhook
            if webhook_url:
                try:
                    payload = {
                        "image_url": public_image_url,
                        "filename": file,
                        "subfolder": subfolder,
                        "prompt": prompt,
                        "extra_info": extra_pnginfo
                    }
                    response = requests.post(webhook_url, json=payload)
                    response.raise_for_status()
                except requests.RequestException as e:
                    print(f"Failed to send webhook: {e}")

            results.append({
                "filename": file,
                "subfolder": subfolder,
                "type": self.type,
                "image_url": public_image_url
            })
            counter += 1

        return (public_image_url, {"ui": {"images": results}})

# A dictionary that contains all nodes you want to export with their names
NODE_CLASS_MAPPINGS = {
    "ImagePreviewWithWebhook": ImagePreviewWithWebhook
}

# A dictionary that contains the friendly/humanly readable titles for the nodes
NODE_DISPLAY_NAME_MAPPINGS = {
    "ImagePreviewWithWebhook": "Image Preview with Webhook"
}
