#!/usr/bin/env python3
"""
Image Guardrail Module for Smart Fridge
Pre-filters images to detect if they contain food items before expensive GPT-4 Vision processing
"""
import base64
import io
from PIL import Image
import requests
from typing import Dict, Any, Tuple
import os


def analyze_image_with_huggingface(image_data: bytes) -> Dict[str, Any]:
    """
    Use Hugging Face's free food classification model to pre-filter images
    
    Args:
        image_data: Raw image bytes
        
    Returns:
        Dict with classification results
    """
    try:
        # Convert to PIL Image
        image = Image.open(io.BytesIO(image_data))
        
        # Convert to RGB if needed
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Resize image to reduce processing time (optional)
        if image.size[0] > 800 or image.size[1] > 800:
            image.thumbnail((800, 800), Image.Resampling.LANCZOS)
        
        # Convert back to bytes
        img_buffer = io.BytesIO()
        image.save(img_buffer, format='JPEG', quality=85)
        img_bytes = img_buffer.getvalue()
        
        # Use Hugging Face Inference API (free tier)
        # Food classification model
        API_URL = "https://api-inference.huggingface.co/models/nateraw/food"
        
        # Get HF token from environment (optional, works without token but with rate limits)
        hf_token = os.getenv("HUGGINGFACE_TOKEN")
        headers = {}
        if hf_token:
            headers["Authorization"] = f"Bearer {hf_token}"
        
        response = requests.post(API_URL, headers=headers, data=img_bytes, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            
            # Check if any food-related labels are detected with confidence > threshold
            food_confidence = 0.0
            detected_labels = []
            
            if isinstance(result, list) and len(result) > 0:
                for item in result[:5]:  # Check top 5 predictions
                    label = item.get('label', '').lower()
                    score = item.get('score', 0.0)
                    
                    detected_labels.append(f"{label}: {score:.2f}")
                    
                    # Check if it's food-related
                    food_keywords = [
                        'food', 'fruit', 'vegetable', 'meat', 'dairy', 'bread',
                        'apple', 'banana', 'orange', 'carrot', 'potato', 'tomato',
                        'cheese', 'milk', 'egg', 'chicken', 'beef', 'fish',
                        'pizza', 'sandwich', 'salad', 'soup', 'cake', 'cookie'
                    ]
                    
                    if any(keyword in label for keyword in food_keywords):
                        food_confidence = max(food_confidence, score)
            
            return {
                "is_food_likely": food_confidence > 0.3,  # 30% confidence threshold
                "food_confidence": food_confidence,
                "detected_labels": detected_labels,
                "method": "huggingface_food_classifier"
            }
        else:
            print(f"Hugging Face API error: {response.status_code}")
            return fallback_basic_check(image_data)
            
    except Exception as e:
        print(f"Error in Hugging Face classification: {e}")
        return fallback_basic_check(image_data)


def analyze_image_with_basic_vision(image_data: bytes) -> Dict[str, Any]:
    """
    Use a basic computer vision approach to detect if image might contain food
    
    Args:
        image_data: Raw image bytes
        
    Returns:
        Dict with basic analysis results
    """
    try:
        from PIL import Image, ImageStat
        import numpy as np
        
        # Convert to PIL Image
        image = Image.open(io.BytesIO(image_data))
        
        # Convert to RGB
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Basic heuristics for food detection
        stats = ImageStat.Stat(image)
        
        # Get color statistics
        mean_colors = stats.mean  # RGB means
        
        # Food images typically have:
        # 1. Varied colors (not monochrome)
        # 2. Certain color ranges (greens, reds, yellows, browns)
        # 3. Good contrast
        
        # Calculate color variance
        color_variance = np.var(mean_colors)
        
        # Check for food-like colors
        r, g, b = mean_colors
        
        # Food color indicators
        has_green = g > 80  # Vegetables
        has_red = r > 100   # Fruits, meat
        has_yellow = r > 120 and g > 120 and b < 100  # Fruits, cheese
        has_brown = r > 80 and g > 60 and b < 80      # Bread, meat
        
        food_color_score = sum([has_green, has_red, has_yellow, has_brown]) / 4
        
        # Simple scoring
        is_likely_food = (
            color_variance > 500 and  # Has color variation
            food_color_score > 0.25   # Has some food-like colors
        )
        
        return {
            "is_food_likely": is_likely_food,
            "food_confidence": min(0.7, food_color_score + (color_variance / 2000)),
            "detected_labels": [f"color_analysis: {food_color_score:.2f}"],
            "method": "basic_computer_vision"
        }
        
    except Exception as e:
        print(f"Error in basic vision analysis: {e}")
        return fallback_basic_check(image_data)


def fallback_basic_check(image_data: bytes) -> Dict[str, Any]:
    """
    Fallback method - just check if it's a valid image
    
    Args:
        image_data: Raw image bytes
        
    Returns:
        Dict with basic validation
    """
    try:
        # Just verify it's a valid image
        image = Image.open(io.BytesIO(image_data))
        
        # If we can open it, assume it might be food (conservative approach)
        return {
            "is_food_likely": True,  # Conservative - allow through
            "food_confidence": 0.5,  # Medium confidence
            "detected_labels": ["valid_image"],
            "method": "fallback_validation"
        }
        
    except Exception as e:
        return {
            "is_food_likely": False,
            "food_confidence": 0.0,
            "detected_labels": ["invalid_image"],
            "method": "fallback_validation",
            "error": str(e)
        }


def should_process_with_gpt_vision(image_data: bytes, 
                                 confidence_threshold: float = 0.3) -> Tuple[bool, Dict[str, Any]]:
    """
    Main guardrail function to determine if image should be processed with GPT-4 Vision
    
    Args:
        image_data: Raw image bytes
        confidence_threshold: Minimum confidence to proceed with GPT-4 Vision
        
    Returns:
        Tuple of (should_process, analysis_details)
    """
    
    # Try Hugging Face first (most accurate)
    analysis = analyze_image_with_huggingface(image_data)
    
    # If HF fails, try basic computer vision
    if not analysis.get("is_food_likely") and analysis.get("method") == "fallback_validation":
        analysis = analyze_image_with_basic_vision(image_data)
    
    # Decision logic
    should_process = (
        analysis.get("is_food_likely", False) and 
        analysis.get("food_confidence", 0.0) >= confidence_threshold
    )
    
    return should_process, analysis


# Example usage and testing
if __name__ == "__main__":
    # Test with a sample image
    try:
        with open("../fridge.jpg", "rb") as f:
            test_image = f.read()
        
        should_process, analysis = should_process_with_gpt_vision(test_image)
        
        print("=== Image Guardrail Test ===")
        print(f"Should process with GPT-4 Vision: {should_process}")
        print(f"Analysis: {analysis}")
        
    except FileNotFoundError:
        print("Test image not found. Please provide a test image.") 