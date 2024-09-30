from .ImagePreviewWithWebhook import ImagePreviewWithWebhook
from .ImagePreviewWithWebhook2 import ImagePreviewWithWebhook2  # Import thêm node mới

NODE_CLASS_MAPPINGS = {
    "ImagePreviewWithWebhook": ImagePreviewWithWebhook,
    "ImagePreviewWithWebhook2": ImagePreviewWithWebhook2  # Thêm node mới vào danh sách mapping
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ImagePreviewWithWebhook": "Image Preview with Webhook",
    "ImagePreviewWithWebhook2": "Image Preview with Webhook 2"  # Tên hiển thị của node mới
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
