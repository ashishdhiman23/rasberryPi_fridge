#!/usr/bin/env python3
"""
Test script for image guardrail functionality
"""
import sys
import os
sys.path.append('backend')

from backend.image_guardrail import should_process_with_gpt_vision

def test_guardrail():
    """Test the guardrail with the fridge image"""
    
    print("=== Image Guardrail Test ===")
    
    # Test with fridge image
    try:
        with open("fridge.jpg", "rb") as f:
            fridge_image = f.read()
        
        should_process, analysis = should_process_with_gpt_vision(fridge_image)
        
        print(f"\n📸 Testing fridge.jpg:")
        print(f"Should process with GPT-4 Vision: {should_process}")
        print(f"Method used: {analysis.get('method', 'unknown')}")
        print(f"Food confidence: {analysis.get('food_confidence', 0):.2f}")
        print(f"Detected labels: {analysis.get('detected_labels', [])}")
        
        if should_process:
            print("✅ PASS: Image will be processed with GPT-4 Vision")
        else:
            print("❌ BLOCK: Image will be blocked from GPT-4 Vision")
            
    except FileNotFoundError:
        print("❌ fridge.jpg not found in current directory")
    except Exception as e:
        print(f"❌ Error testing fridge image: {e}")

def test_cost_savings():
    """Estimate potential cost savings"""
    
    print("\n=== Cost Savings Analysis ===")
    
    # GPT-4 Vision pricing (approximate)
    gpt4_vision_cost_per_image = 0.01  # $0.01 per image (rough estimate)
    huggingface_cost_per_image = 0.0   # Free tier
    
    # Assume 10% of images are non-food (conservative estimate)
    images_per_day = 100
    non_food_percentage = 0.10
    
    blocked_images_per_day = images_per_day * non_food_percentage
    daily_savings = blocked_images_per_day * gpt4_vision_cost_per_image
    monthly_savings = daily_savings * 30
    yearly_savings = daily_savings * 365
    
    print(f"📊 Estimated Cost Savings:")
    print(f"   Images per day: {images_per_day}")
    print(f"   Non-food images blocked: {blocked_images_per_day:.1f} per day")
    print(f"   Daily savings: ${daily_savings:.2f}")
    print(f"   Monthly savings: ${monthly_savings:.2f}")
    print(f"   Yearly savings: ${yearly_savings:.2f}")

if __name__ == "__main__":
    test_guardrail()
    test_cost_savings() 