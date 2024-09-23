# __init__.py for registering the ImagePreviewWithWebhook node

from image_preview_with_webhook import ImagePreviewWithWebhook

# A dictionary that maps node class names to their corresponding classes
NODE_CLASS_MAPPINGS = {
    "ImagePreviewWithWebhook": ImagePreviewWithWebhook
}

# A dictionary that contains the human-readable display names for the nodes
NODE_DISPLAY_NAME_MAPPINGS = {
    "ImagePreviewWithWebhook": "Image Preview with Webhook"
}
