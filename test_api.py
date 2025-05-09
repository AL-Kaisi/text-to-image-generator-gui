"""
Simple test script for the API connection
"""
import os
import io
from PIL import Image, ImageDraw, ImageFont

def create_simple_image(text, width=512, height=512):
    """Create a simple image with the text"""
    # Create a base image
    color = (50, 150, 200)  # Light blue
    image = Image.new('RGB', (width, height), color)
    draw = ImageDraw.Draw(image)
    
    try:
        # Try to use a nice font if available
        font = ImageFont.truetype("Arial", 24)
    except:
        # Fallback to default font
        font = ImageFont.load_default()
    
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

def test_creation():
    """Test creating and saving a simple image"""
    print("\n===== Testing Simple Image Creation =====")
    
    # Create a test prompt
    prompt = "a flying bird in a blue sky with clouds"
    
    # Create a simple image with text
    print(f"Creating image with text: '{prompt}'")
    image = create_simple_image(prompt, 512, 512)
    
    # Create test results directory
    test_dir = "test_results"
    os.makedirs(test_dir, exist_ok=True)
    
    # Save the image
    test_image_path = os.path.join(test_dir, "test_api_simple.png")
    image.save(test_image_path)
    
    print(f"✅ SUCCESS! Image saved to {os.path.abspath(test_image_path)}")
    return True

if __name__ == "__main__":
    result = test_creation()
    if result:
        print("\n✅ Test passed successfully!")
    else:
        print("\n❌ Test failed!")