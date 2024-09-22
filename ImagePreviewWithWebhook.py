import requests
import random
import os
from PIL import Image
from pathlib import Path

# Giả sử rằng logger đã được định nghĩa
from .logger import logger
import folder_paths

class ImagePreviewWithWebhook:
    def __init__(self):
        self.output_dir = folder_paths.get_temp_directory()
        self.type = "temp"
        self.prefix_append = "_temp_" + ''.join(random.choice("abcdefghijklmnopqrstupvxyz") for x in range(5))
        self.compress_level = 1

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE",),
                "webhook_url": ("STRING",),  # Thêm đầu vào cho URL webhook
            },
            "hidden": {
                "prompt": "PROMPT",
                "extra_pnginfo": "EXTRA_PNGINFO",
            }
        }

    RETURN_TYPES = ("STRING",)  # Trả về URL hình ảnh
    FUNCTION = "execute"

    def execute(self, images, webhook_url):
        # Giả sử chỉ lấy ảnh đầu tiên từ danh sách
        image = images[0]
        image_name = f"{self.prefix_append}.png"
        image_path = Path(self.output_dir) / image_name
        
        # Lưu hình ảnh
        Image.fromarray(image).save(image_path)

        # Tạo URL cho hình ảnh
        image_url = f"http://your.server/path/to/images/{image_name}"  # Thay đổi đường dẫn này cho phù hợp

        # Gửi HTTP request tới webhook
        try:
            response = requests.post(webhook_url, json={"image_url": image_url})
            if response.status_code == 200:
                logger.info(f"Webhook sent successfully to {webhook_url} with image URL {image_url}")
            else:
                logger.error(f"Failed to send webhook: {response.status_code}, Response: {response.text}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Error sending webhook: {e}")

        return (image_url,)  # Trả về URL hình ảnh đã tạo
