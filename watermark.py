import cv2
import numpy as np

def add_invisible_watermark(image_path):
    img = cv2.imread(image_path)

    # Create a transparent pattern (low opacity watermark)
    watermark = np.full(img.shape, (5, 5, 5), dtype=np.uint8)

    # Blend the watermark subtly
    watermarked_img = cv2.addWeighted(img, 1, watermark, 0.05, 0)

    output_path = "processed/watermarked_" + image_path.split("/")[-1]
    cv2.imwrite(output_path, watermarked_img)
    return output_path
