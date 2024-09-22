from pathlib import Path
import requests
from PIL import Image
import io

# Giả sử rằng logger và các tiện ích khác được định nghĩa trong thư mục này
from .logger import logger  # Nếu có logger
# Bạn có thể thêm các import khác nếu cần thiết

class ImagePreviewWithWebhook:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),  # Nhận đầu vào là một hình ảnh
                "webhook_url": ("STRING",),  # URL của webhook
            }
        }

    RETURN_TYPES = ()
    FUNCTION = "execute"

    def execute(self, image, webhook_url):
        # Tạo file tạm thời từ ảnh đầu vào
        image_data = Image.fromarray(image)

        # Lưu ảnh ra file tạm thời
        with io.BytesIO() as img_byte_arr:
            image_data.save(img_byte_arr, format='PNG')
            img_byte_arr.seek(0)

            # Định nghĩa payload để gửi lên webhook
            files = {'file': img_byte_arr.getvalue()}
            payload = {
                'message': 'Image generated from ComfyUI',
            }

            # Gửi POST request tới webhook
            try:
                response = requests.post(webhook_url, files=files, data=payload)
                if response.status_code == 200:
                    logger.info(f"Webhook sent successfully to {webhook_url}")
                else:
                    logger.error(f"Failed to send webhook: {response.status_code}")
            except requests.exceptions.RequestException as e:
                logger.error(f"Error sending webhook: {e}")

        # Không trả về gì vì chỉ là preview ảnh
        return ()

# Đăng ký node vào ComfyUI
NODE_CLASS_MAPPINGS = {
    "ImagePreviewWithWebhook": ImagePreviewWithWebhook
}
