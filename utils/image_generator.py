from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os
import textwrap
import numpy as np
from PIL.ImageColor import getrgb

def generate_image(text, settings):
    """
    Generate an image with the given text and settings
    
    Args:
        text: String containing the text to render
        settings: Dictionary containing all the image generation settings
    
    Returns:
        PIL Image object
    """
    # Extract settings
    width = settings["dimensions"]["width"]
    height = settings["dimensions"]["height"]
    font_size = settings["font"]["size"]
    font_color = settings["font"]["color"]
    alignment = settings["alignment"]
    text_effects = settings["text_effects"]
    effect_settings = settings["effects"]
    padding = settings["advanced"]["padding"]
    line_spacing = settings["advanced"]["line_spacing"]
    text_wrap = settings["advanced"]["text_wrap"]
    text_transform = settings["advanced"]["text_transform"]
    
    # Create the base image with the specified background
    img = create_background(width, height, settings["background"])
    
    # Initialize drawing context
    draw = ImageDraw.Draw(img)
    
    # Try to load a nice font, fallback to default if not available
    font = None
    
    # List of common system fonts to try
    system_fonts = [
        "Arial", 
        "Helvetica", 
        "Times New Roman", 
        "Verdana", 
        "Courier New",
        "DejaVu Sans",
        "Liberation Sans"
    ]
    
    # First try our bundled font
    try:
        font_path = os.path.join("assets", "fonts", "Roboto-Regular.ttf")
        if os.path.exists(font_path):
            font = ImageFont.truetype(font_path, font_size)
            print(f"Using bundled font: {font_path}")
    except Exception as e:
        print(f"Error loading bundled font: {str(e)}")
    
    # If bundled font failed, try system fonts
    if font is None:
        for system_font in system_fonts:
            try:
                font = ImageFont.truetype(system_font, font_size)
                print(f"Using system font: {system_font}")
                break
            except Exception as e:
                print(f"Could not load system font {system_font}: {str(e)}")
    
    # If all else fails, use default font
    if font is None:
        try:
            font = ImageFont.load_default()
            font_size = 12  # Default size for the default font
            print("Using default font")
        except Exception as e:
            print(f"Error loading default font: {str(e)}")
            raise Exception("Could not load any fonts for text rendering")
    
    # Apply text transformations if specified
    if text_transform == "uppercase":
        text = text.upper()
    elif text_transform == "lowercase":
        text = text.lower()
    elif text_transform == "capitalize":
        text = text.title()
    
    # Word wrap the text if enabled
    if text_wrap:
        # Calculate approximate chars per line (this is an approximation)
        avg_char_width = font_size * 0.6  # Approximation
        chars_per_line = int((width - 2 * padding) / avg_char_width)
        lines = textwrap.wrap(text, width=chars_per_line)
    else:
        lines = text.split('\n')
    
    # Calculate text block dimensions
    line_height = font_size * line_spacing
    text_height = len(lines) * line_height
    
    # Calculate starting y position based on text height and alignment
    if alignment == "center":
        y_position = (height - text_height) / 2
    else:
        y_position = padding
    
    # Apply text effects if enabled
    if "Outline" in text_effects and "outline" in effect_settings:
        outline_color = effect_settings["outline"]["color"]
        outline_width = effect_settings["outline"]["width"]
    else:
        outline_width = 0
        outline_color = None
    
    # Draw each line of text
    for line in lines:
        # Calculate x position based on alignment
        if alignment == "center":
            x_position = width / 2
            align = "center"
        elif alignment == "left":
            x_position = padding
            align = "left"
        else:  # right
            x_position = width - padding
            align = "right"
        
        # Apply shadow effect
        if "Shadow" in text_effects and "shadow" in effect_settings:
            shadow_color = effect_settings["shadow"]["color"]
            shadow_blur = effect_settings["shadow"]["blur"]
            
            # Draw shadow text
            draw.text((x_position + shadow_blur, y_position + shadow_blur), 
                     line, font=font, fill=shadow_color, align=align,
                     anchor=get_anchor_position(align))
        
        # Apply glow effect
        if "Glow" in text_effects and "glow" in effect_settings:
            glow_color = effect_settings["glow"]["color"]
            glow_strength = effect_settings["glow"]["strength"]
            
            # Create a temporary image for the glow effect
            glow_img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
            glow_draw = ImageDraw.Draw(glow_img)
            
            # Draw the text in the glow color
            glow_draw.text((x_position, y_position), line, font=font, 
                          fill=glow_color, align=align,
                          anchor=get_anchor_position(align))
            
            # Apply blur to create glow effect
            glow_img = glow_img.filter(ImageFilter.GaussianBlur(glow_strength))
            
            # Composite the glow onto the main image
            img = Image.alpha_composite(img.convert('RGBA'), glow_img)
            draw = ImageDraw.Draw(img)
        
        # Draw the main text with outline if specified
        if outline_width > 0:
            # Draw text outline
            for offset_x in range(-outline_width, outline_width + 1, 2):
                for offset_y in range(-outline_width, outline_width + 1, 2):
                    if offset_x == 0 and offset_y == 0:
                        continue
                    draw.text((x_position + offset_x, y_position + offset_y), 
                             line, font=font, fill=outline_color, align=align,
                             anchor=get_anchor_position(align))
        
        # Draw the main text
        draw.text((x_position, y_position), line, font=font, 
                 fill=font_color, align=align,
                 anchor=get_anchor_position(align))
        
        # Move to next line
        y_position += line_height
    
    return img

def create_background(width, height, bg_settings):
    """
    Create a background image based on the specified settings
    
    Args:
        width: Image width
        height: Image height
        bg_settings: Dictionary containing background settings
    
    Returns:
        PIL Image with the background applied
    """
    bg_type = bg_settings["type"]
    
    if bg_type == "transparent":
        # Create a transparent image
        return Image.new('RGBA', (width, height), (0, 0, 0, 0))
    
    elif bg_type == "solid":
        # Create a solid color background
        color = bg_settings["color"]
        return Image.new('RGBA', (width, height), color)
    
    elif bg_type == "gradient":
        # Create a gradient background
        start_color = getrgb(bg_settings["start_color"])
        end_color = getrgb(bg_settings["end_color"])
        direction = bg_settings["direction"]
        
        # Create gradient array
        if direction == "horizontal":
            gradient = np.zeros((height, width, 3), dtype=np.uint8)
            for x in range(width):
                r = int(start_color[0] + (end_color[0] - start_color[0]) * x / width)
                g = int(start_color[1] + (end_color[1] - start_color[1]) * x / width)
                b = int(start_color[2] + (end_color[2] - start_color[2]) * x / width)
                gradient[:, x] = [r, g, b]
        
        elif direction == "vertical":
            gradient = np.zeros((height, width, 3), dtype=np.uint8)
            for y in range(height):
                r = int(start_color[0] + (end_color[0] - start_color[0]) * y / height)
                g = int(start_color[1] + (end_color[1] - start_color[1]) * y / height)
                b = int(start_color[2] + (end_color[2] - start_color[2]) * y / height)
                gradient[y, :] = [r, g, b]
        
        else:  # diagonal
            gradient = np.zeros((height, width, 3), dtype=np.uint8)
            for y in range(height):
                for x in range(width):
                    # Calculate position along diagonal (0 to 1)
                    pos = (x / width + y / height) / 2
                    r = int(start_color[0] + (end_color[0] - start_color[0]) * pos)
                    g = int(start_color[1] + (end_color[1] - start_color[1]) * pos)
                    b = int(start_color[2] + (end_color[2] - start_color[2]) * pos)
                    gradient[y, x] = [r, g, b]
        
        # Convert numpy array to PIL Image
        img = Image.fromarray(gradient)
        
        # Convert to RGBA
        return img.convert('RGBA')
    
    # Default fallback: black background
    return Image.new('RGBA', (width, height), (0, 0, 0, 255))

def get_anchor_position(alignment):
    """
    Get the anchor position string for PIL based on alignment
    
    Args:
        alignment: String with alignment type (left, center, right)
    
    Returns:
        Anchor position string for PIL
    """
    if alignment == "center":
        return "mm"  # middle middle
    elif alignment == "left":
        return "lm"  # left middle
    else:  # right
        return "rm"  # right middle