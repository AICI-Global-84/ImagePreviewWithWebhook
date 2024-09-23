import os
import random
import requests
from PIL import Image
import numpy as np
from server import folder_paths
from nodes import SaveImage  # Thay thế 'SomeOtherModule' bằng tên module chứa SaveImage

class ImagePreviewWithWebhook(SaveImage):
    def __init__(self):
        # Save in temporary directory
        self.output_dir = folder_paths.get_temp_directory()
        self.type = "temp"
        self.prefix_append = "_preview_" + ''.join(random.choice("abcdefghijklmnopqrstupvxyz") for _ in range(5))
        self.compress_level = 1
        # Webhook URL (can be configured)
        self.webhook_url = "https://your-n8n-instance/webhook-endpoint"

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "images": ("IMAGE", ),
                "filename_prefix": ("STRING", {"default": "ComfyUI", "tooltip": "The prefix for the file to save."}),
                "webhook_url": ("STRING", {"default": "https://your-n8n-instance/webhook-endpoint", "tooltip": "n8n webhook URL to send the request."}),
            },
            "hidden": {
                "prompt": "PROMPT", 
                "extra_pnginfo": "EXTRA_PNGINFO"
            },
        }

    RETURN_TYPES = ("IMAGE", "STRING", "STRING")
    FUNCTION = "preview_and_webhook"
    CATEGORY = "image"

    def preview_and_webhook(self, images, filename_prefix="ComfyUI", webhook_url=None, prompt=None, extra_pnginfo=None):
        # Use provided webhook_url if present
        if webhook_url:
            self.webhook_url = webhook_url

        # Update filename prefix
        filename_prefix += self.prefix_append
        full_output_folder, filename, counter, subfolder, filename_prefix = folder_paths.get_save_image_path(filename_prefix, self.output_dir, images[0].shape[1], images[0].shape[0])
        
        results = []
        for (batch_number, image) in enumerate(images):
            # Convert the image from tensor to numpy array
            i = 255. * image.cpu().numpy()
            img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))
            
            # Define metadata (if needed)
            metadata = None
            if not args.disable_metadata:
                metadata = PngInfo()
                if prompt is not None:
                    metadata.add_text("prompt", json.dumps(prompt))
                if extra_pnginfo is not None:
                    for key in extra_pnginfo:
                        metadata.add_text(key, json.dumps(extra_pnginfo[key]))

            # Create unique filename for each batch
            filename_with_batch_num = filename.replace("%batch_num%", str(batch_number))
            file = f"{filename_with_batch_num}_{counter:05}_.png"
            img_path = os.path.join(full_output_folder, file)
            img.save(img_path, pnginfo=metadata, compress_level=self.compress_level)
            results.append({
                "filename": file,
                "subfolder": subfolder,
                "type": self.type
            })

            # Send HTTP request to n8n webhook
            try:
                response = requests.post(self.webhook_url, json={"image_path": img_path, "filename": file})
                if response.status_code != 200:
                    print(f"Failed to send webhook: {response.status_code}, {response.text}")
                else:
                    print(f"Webhook sent successfully: {response.status_code}")
            except Exception as e:
                print(f"Error sending webhook: {str(e)}")

            counter += 1

        # Generate preview image URL
        image_url = f"file://{img_path}"

        # Return the image, image URL, and filename for the UI
        return (image, image_url, file)

# Register node
NODE_CLASS_MAPPINGS = {
    "ImagePreviewWithWebhook": ImagePreviewWithWebhook
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ImagePreviewWithWebhook": "Image Preview with Webhook"
}
