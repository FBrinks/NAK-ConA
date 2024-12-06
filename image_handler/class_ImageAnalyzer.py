""" This module handles image classification and processing using OpenAI Vision API. 
It is not used in the current version of the program, but is a work in progress for future features.
And an improved and more thorough image handling including cropping and identifying the image type,
check for non-white backgrounds on product images, and more. """

from openai import OpenAI
import cv2
import numpy as np
import base64
import os
import json
from datetime import datetime
from typing import Dict, Tuple, Optional


class ImageAnalyzer:
    """Handles image classification and processing using OpenAI Vision API."""

    def __init__(self, api_key: str, cache_file: str = "image_cache.json"):
        """Initialize analyzer with OpenAI API key and optional cache file."""
        self.client = OpenAI(api_key=api_key)
        self.cache_file = cache_file
        self._load_cache()

    def _load_cache(self) -> None:
        """Load cached results from file."""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, "r") as f:
                    self.cache = json.load(f)
            else:
                self.cache = {}
        except Exception as e:
            print(f"Cache loading error: {e}")
            self.cache = {}

    def _save_cache(self) -> None:
        """Save results to cache file."""
        try:
            with open(self.cache_file, "w") as f:
                json.dump(self.cache, f)
        except Exception as e:
            print(f"Cache saving error: {e}")

    def classify_image(self, image_path: str) -> Tuple[str, bool]:
        """
        Classify image using OpenAI Vision API.
        Returns: (category, from_cache)
        """
        # Check cache first
        if image_path in self.cache:
            return self.cache[image_path], True

        try:
            with open(image_path, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode("utf-8")

            response = self.client.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Classify this image into one of these categories: 'studio-product', 'lifestyle-product', 'mood'. Respond with just the category.",
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                },
                            },
                        ],
                    }
                ],
                max_tokens=10,
            )
            category = response.choices[0].message.content.strip()
            self.cache[image_path] = category
            self._save_cache()
            return category, False
        except Exception as e:
            print(f"Classification error: {e}")
            return "error", False

    def process_product_image(self, image_path):
        """Process product images - add padding and frame"""
        # Read image
        img = cv2.imread(image_path)

        # Convert to square with padding
        height, width = img.shape[:2]
        max_dim = max(height, width)

        # Create white background
        square = np.ones((max_dim, max_dim, 3), dtype=np.uint8) * 255

        # Calculate padding
        y_offset = (max_dim - height) // 2
        x_offset = (max_dim - width) // 2

        # Place image in center
        square[y_offset : y_offset + height, x_offset : x_offset + width] = img

        # Add frame (5% padding)
        frame_size = int(max_dim * 0.05)
        framed = cv2.copyMakeBorder(
            square,
            frame_size,
            frame_size,
            frame_size,
            frame_size,
            cv2.BORDER_CONSTANT,
            value=[255, 255, 255],
        )

        return framed


# Initialize
analyzer = ImageAnalyzer(api_key="your_openai_api_key")

# Classify image
category, from_cache = analyzer.classify_image("path/to/image.jpg")

# Process if it's a product
if category in ["studio-product", "lifestyle-product"]:
    processed = analyzer.process_product_image("path/to/image.jpg")
    if processed is not None:
        cv2.imwrite("processed_image.jpg", processed)
