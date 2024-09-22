import requests
from PIL import Image
import io
import os

# Giả sử rằng logger đã được định nghĩa
from .logger import logger

class ImagePreviewWithWebhook:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),  # Nhận đầu vào là một hình ảnh
                "webhook_url": ("STRING",),  # URL của webhook
            }
        }

    RETURN_TYPES = ("STRING",)  # Để trả về thông báo thành công
    FUNCTION = "execute"

    def execute(self, image, webhook_url):
        # Tạo file tạm thời từ ảnh đầu vào
        image_data = Image.fromarray(image)

        # Lưu ảnh ra file tạm thời
        image_path = "/tmp/generated_image.png"  # Đường dẫn tạm
        image_data.save(image_path, format='PNG')

        # Định nghĩa payload để gửi lên webhook
        with open(image_path, 'rb') as img_file:
            files = {'file': img_file}
            payload = {
                'message': 'Image generated from ComfyUI',
            }

            # Gửi POST request tới webhook
            try:
                response = requests.post(webhook_url, files=files, data=payload)
                if response.status_code == 200:
                    logger.info(f"Webhook sent successfully to {webhook_url}")
                    return (f"Webhook sent successfully: {image_path}, Status: {response.status_code}, Response: {response.text}",)
                else:
                    logger.error(f"Failed to send webhook: {response.status_code}")
                    return (f"Failed to send webhook: {response.status_code}, Response: {response.text}",)
            except requests.exceptions.RequestException as e:
                logger.error(f"Error sending webhook: {e}")
                return (f"Error sending webhook: {e}",)

        # Xóa file tạm nếu cần thiết
        if os.path.exists(image_path):
            os.remove(image_path)

        return (image_path,)  # Trả về đường dẫn ảnh đã tạo
