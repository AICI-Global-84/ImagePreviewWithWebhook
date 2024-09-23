import os
import json
import requests
from PIL import Image
from PIL.PngImagePlugin import PngInfo
import numpy as np
import folder_paths

class ImagePreviewWithWebhook:
    def __init__(self):
        self.output_dir = folder_paths.get_output_directory()
        self.type = "output"
        self.prefix_append = ""
        self.compress_level = 4
        self.token = "61aa06d6116f7331ad7b2ba9c7fb707ec9b182e8"  # Token cố định
        self.upload_url = "https://postimg.cc/json?q=a"

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

    def upload_to_postimage(self, image_path, filename):
        """Upload image to PostImage using POST request and return the direct URL."""
        with open(image_path, 'rb') as img_file:
            files = {'file': img_file}
            data = {
                "token": self.token,
                "upload_session": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",  # Sinh ngẫu nhiên nếu cần
                "numfiles": "1",
                "upload_referer": "https://www.phpbb.com",
            }
    
            response = requests.post(self.upload_url, files=files, data=data)
    
            # In ra phản hồi JSON
            print(f"Response status code: {response.status_code}")
            print(f"Response text: {response.text}")
    
            if response.status_code == 200:
                response_data = response.json()
                if 'success' in response_data and 'url' in response_data:
                    # Lấy trang URL
                    page_url = response_data['url']
                    
                    # Xây dựng URL trực tiếp
                    direct_url = f"https://i.postimg.cc/{page_url.split('/')[-2]}/{filename}"
                    print(f"Direct image URL: {direct_url}")
                    return direct_url
                else:
                    print(f"Unexpected response structure: {response_data}")
            else:
                print(f"Failed to upload image to PostImage: {response.status_code} {response.text}")
            return None



    def process_and_send_image(self, images, filename_prefix="ComfyUI", webhook_url="", prompt=None, extra_pnginfo=None):
        filename_prefix += self.prefix_append
        full_output_folder, filename, counter, subfolder, _ = folder_paths.get_save_image_path(filename_prefix, self.output_dir, images[0].shape[1], images[0].shape[0])
    
        results = []
        for batch_number, image in enumerate(images):
            i = 255. * image.cpu().numpy()
            img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))
    
            # Đặt tên file đúng định dạng
            correct_filename = f"{filename.replace('%batch_num%', str(batch_number))}_{counter:05}.png"
            full_path = os.path.join(full_output_folder, correct_filename)
            img.save(full_path)
    
            # Upload ảnh và lấy URL trực tiếp
            public_image_url = self.upload_to_postimage(full_path, correct_filename)
    
            # Kiểm tra URL và xử lý webhook
            if webhook_url:
                try:
                    payload = {
                        "image_url": public_image_url,
                        "filename": correct_filename,
                        "subfolder": subfolder,
                        "prompt": prompt,
                        "extra_info": extra_pnginfo
                    }
                    response = requests.post(webhook_url, json=payload)
                    response.raise_for_status()
                except requests.RequestException as e:
                    print(f"Failed to send webhook: {e}")
    
            results.append({
                "filename": correct_filename,
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
