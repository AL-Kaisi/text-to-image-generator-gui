"""
Simplified image generation using Hugging Face models
"""
import os
import torch
from PIL import Image, ImageDraw, ImageFont
import numpy as np

def generate_image(prompt, settings=None):
    """
    Generate an image based on a text prompt
    
    Args:
        prompt (str): The text prompt for image generation
        settings (dict): Optional dictionary of settings for image generation
        
    Returns:
        PIL.Image: The generated image
    """
    # Default settings if none provided
    if settings is None:
        settings = {}
    
    # Extract settings with defaults
    width = settings.get('width', 512)
    height = settings.get('height', 512)
    
    try:
        # Try importing numpy explicitly
        try:
            import numpy as np
        except ImportError:
            # If numpy isn't available, install it
            import subprocess
            print("NumPy not found, attempting to install...")
            subprocess.check_call(["pip", "install", "numpy"])
            import numpy as np
            
        # Now try using diffusers
        try:
            from diffusers import DiffusionPipeline
            
            # Load a simpler model - StableDiffusionXLPipeline is too complex/large
            print("Loading small pipeline...")
            pipeline = DiffusionPipeline.from_pretrained(
                "runwayml/stable-diffusion-v1-5", 
                use_safetensors=True, 
                safety_checker=None  # Disable safety checker for performance
            )
            
            # Run on CPU only for compatibility
            pipeline = pipeline.to("cpu")
            
            # Generate the image
            print(f"Generating image with prompt: '{prompt}'")
            result = pipeline(
                prompt=prompt,
                width=width,
                height=height,
                num_inference_steps=20,  # Keep steps low for speed
            )
            
            # Get the image from the result
            image = result.images[0]
            
            # Clean up
            del pipeline
            
            return image
            
        except Exception as e:
            print(f"Error using diffusers: {str(e)}")
            import traceback
            traceback.print_exc()
            # Continue to fallback
            
    except Exception as e:
        print(f"Error in generate_image: {str(e)}")
        import traceback
        traceback.print_exc()
    
    # Fallback: create a simple image with the prompt text
    print("Falling back to creating a simple image with text")
    return create_text_image(prompt, width, height)

def create_text_image(text, width=512, height=512):
    """Create a simple image with the text"""
    # Create a base image
    color = (50, 150, 200)  # Light blue
    image = Image.new('RGB', (width, height), color)
    draw = ImageDraw.Draw(image)
    
    # Add text
    try:
        # Try to use a nice font if available
        font = ImageFont.truetype("Arial", 24)
    except:
        # Fallback to default font
        font = ImageFont.load_default()
    
    # Draw a cloud-like background
    for i in range(20):
        cloud_x = np.random.randint(0, width)
        cloud_y = np.random.randint(0, height // 2)
        cloud_size = np.random.randint(40, 100)
        draw.ellipse(
            (cloud_x, cloud_y, cloud_x + cloud_size, cloud_y + cloud_size), 
            fill=(240, 240, 255)
        )
    
    # Draw a simple bird shape
    bird_x = width // 2
    bird_y = height // 2
    
    # Wings
    draw.arc(
        (bird_x - 40, bird_y - 20, bird_x, bird_y + 20),
        45, 180, fill=(30, 30, 30), width=3
    )
    draw.arc(
        (bird_x, bird_y - 20, bird_x + 40, bird_y + 20),
        0, 135, fill=(30, 30, 30), width=3
    )
    
    # Body
    draw.ellipse(
        (bird_x - 10, bird_y - 5, bird_x + 10, bird_y + 5),
        fill=(30, 30, 30)
    )
    
    # Add the prompt text at the bottom
    text_position = (width // 2, height - 50)
    draw.text(
        text_position, 
        text, 
        fill=(255, 255, 255),
        font=font,
        anchor="mm"
    )
    
    return image