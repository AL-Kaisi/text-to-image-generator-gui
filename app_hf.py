"""
Advanced Flask application for text-to-image generation
Using Ollama for LLMs and Automatic1111 API for Stable Diffusion
"""
import os
import uuid
import time
import json
import requests
import subprocess
import base64
import threading
import tempfile
from io import BytesIO
from flask import Flask, render_template, request, jsonify, url_for, send_from_directory
from PIL import Image, ImageDraw, ImageFont
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'fj38uoewfg7w3r7qwyrt8273r87qwt773t837tg8ew7t837'
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'images')

# Ensure the upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Ollama configuration
OLLAMA_HOST = os.environ.get('OLLAMA_HOST', 'http://localhost:11434')
DEFAULT_MODEL = os.environ.get('OLLAMA_DEFAULT_MODEL', 'llava')

# Automatic1111 configuration
SD_API_HOST = os.environ.get('SD_API_HOST', 'http://localhost:7860')
SD_API_AVAILABLE = True  # Will be checked during initialization

# Models for different types of generation
MODELS = {
    'llava': {
        'name': 'llava',
        'description': 'LLaVA (multimodal)',
        'type': 'multimodal'
    },
    'sdxl': {
        'name': 'sdxl',
        'description': 'Stable Diffusion XL',
        'type': 'diffusion'
    },
    'llava:13b': {
        'name': 'llava:13b',
        'description': 'LLaVA 13B (better quality)',
        'type': 'multimodal'
    },
    'bakllava': {
        'name': 'bakllava',
        'description': 'BakLLaVA (improved LLaVA)',
        'type': 'multimodal'
    },
    'stablelm-zephyr': {
        'name': 'stablelm-zephyr',
        'description': 'StableLM Zephyr',
        'type': 'text-only'
    },
    'brxce/stable-diffusion-prompt-generator': {
        'name': 'brxce/stable-diffusion-prompt-generator',
        'description': 'Stable Diffusion Prompt Generator',
        'type': 'prompt-generator'
    }
}

# Model pulling status
MODEL_PULLING_STATUS = {}

def check_sd_api_available():
    """Check if Automatic1111 Stable Diffusion API is available"""
    global SD_API_AVAILABLE
    try:
        response = requests.get(f"{SD_API_HOST}/sdapi/v1/sd-models", timeout=5)
        if response.status_code == 200:
            print("✅ Automatic1111 API is available")
            SD_API_AVAILABLE = True
            return True
        else:
            print(f"❌ Automatic1111 API returned status {response.status_code}")
    except Exception as e:
        print(f"❌ Automatic1111 API is not available: {str(e)}")
    
    SD_API_AVAILABLE = False
    return False

def ensure_ollama_running():
    """Check if Ollama is running, if not try to start it"""
    try:
        # Try to connect to Ollama API
        response = requests.get(f"{OLLAMA_HOST}/api/tags", timeout=2)
        if response.status_code == 200:
            print("✅ Ollama is running")
            return True
    except requests.exceptions.ConnectionError:
        print("Ollama is not running, attempting to start...")
    except requests.exceptions.Timeout:
        print("Connection to Ollama timed out")
    
    # Try to start Ollama
    try:
        # This runs as a background process
        subprocess.Popen(["ollama", "serve"], 
                         stdout=subprocess.PIPE, 
                         stderr=subprocess.PIPE)
        
        # Give it a moment to start
        time.sleep(5)
        
        # Check again
        try:
            response = requests.get(f"{OLLAMA_HOST}/api/tags", timeout=2)
            if response.status_code == 200:
                print("✅ Ollama started successfully")
                return True
        except:
            pass
    except:
        print("❌ Could not start Ollama automatically")
    
    return False

def get_available_models():
    """Get list of available models from Ollama"""
    try:
        response = requests.get(f"{OLLAMA_HOST}/api/tags", timeout=5)
        if response.status_code == 200:
            return response.json().get("models", [])
        else:
            print(f"Failed to get models: {response.status_code}")
    except Exception as e:
        print(f"Error getting models: {str(e)}")
    
    return []

def is_model_available(model_name):
    """Check if a model is available locally"""
    models = get_available_models()
    for model in models:
        if model.get("name") == model_name:
            return True
    return False

def async_pull_model(model_name):
    """Pull a model asynchronously and update status"""
    global MODEL_PULLING_STATUS
    
    MODEL_PULLING_STATUS[model_name] = "pulling"
    
    try:
        print(f"Starting pull of model {model_name}...")
        response = requests.post(
            f"{OLLAMA_HOST}/api/pull",
            json={"name": model_name},
            timeout=3600  # Long timeout for large models
        )
        
        if response.status_code == 200:
            print(f"✅ Successfully pulled {model_name}")
            MODEL_PULLING_STATUS[model_name] = "completed"
        else:
            print(f"❌ Failed to pull {model_name}: {response.text}")
            MODEL_PULLING_STATUS[model_name] = "failed"
    except Exception as e:
        print(f"❌ Error pulling model {model_name}: {str(e)}")
        MODEL_PULLING_STATUS[model_name] = "failed"

def pull_model(model_name):
    """Start pulling a model if not already available"""
    if is_model_available(model_name):
        return {"status": "available"}
    
    # Check if already pulling
    if model_name in MODEL_PULLING_STATUS:
        return {"status": MODEL_PULLING_STATUS[model_name]}
    
    # Start pulling in background
    thread = threading.Thread(target=async_pull_model, args=(model_name,))
    thread.daemon = True
    thread.start()
    
    return {"status": "pulling"}

def enhance_prompt_with_generator(prompt, model_name="brxce/stable-diffusion-prompt-generator"):
    """Use the prompt generator model to enhance a basic prompt"""
    if not is_model_available(model_name):
        print(f"⚠️ Prompt generator model {model_name} not available, using original prompt")
        return prompt
        
    try:
        url = f"{OLLAMA_HOST}/api/generate"
        payload = {
            "model": model_name,
            "prompt": prompt,
            "stream": False
        }
        
        response = requests.post(url, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            enhanced_prompt = result.get("response", "").strip()
            print(f"Enhanced prompt: {enhanced_prompt}")
            return enhanced_prompt
        else:
            print(f"❌ Error from prompt generator: {response.status_code}, {response.text}")
            return prompt
    except Exception as e:
        print(f"❌ Error using prompt generator: {str(e)}")
        return prompt

def generate_image_with_automatic1111(prompt, width=512, height=512, model_name="sdxl"):
    """
    Generate an image using Automatic1111 Stable Diffusion API
    """
    if not SD_API_AVAILABLE:
        raise Exception("Automatic1111 API is not available")
    
    # Set the model in Automatic1111 first
    try:
        # Try to select the SDXL model in Automatic1111
        available_models_response = requests.get(f"{SD_API_HOST}/sdapi/v1/sd-models", timeout=10)
        if available_models_response.status_code == 200:
            available_models = available_models_response.json()
            
            # Look for SDXL model
            sdxl_model = None
            for model in available_models:
                model_title = model.get("title", "").lower()
                if "sdxl" in model_title:
                    sdxl_model = model["title"]
                    break
            
            if sdxl_model:
                print(f"Found SDXL model: {sdxl_model}")
                # Set the model
                requests.post(
                    f"{SD_API_HOST}/sdapi/v1/options", 
                    json={"sd_model_checkpoint": sdxl_model},
                    timeout=30
                )
            else:
                print("⚠️ No SDXL model found in Automatic1111, using default model")
        else:
            print("⚠️ Unable to get model list from Automatic1111")
    except Exception as e:
        print(f"⚠️ Error setting model in Automatic1111: {str(e)}")
    
    # Now generate the image
    try:
        # Prepare the API call
        payload = {
            "prompt": prompt,
            "negative_prompt": "watermark, text, low quality, blurry, distorted, deformed, disfigured",
            "width": width,
            "height": height,
            "steps": 30,
            "cfg_scale": 7.5,
            "sampler_name": "DPM++ 2M Karras",
        }
        
        # Make the API call
        response = requests.post(
            f"{SD_API_HOST}/sdapi/v1/txt2img",
            json=payload,
            timeout=120
        )
        
        if response.status_code == 200:
            result = response.json()
            
            # Check if there's an image in the response
            if "images" in result and len(result["images"]) > 0:
                # Decode the base64 image
                image_data = base64.b64decode(result["images"][0])
                image = Image.open(BytesIO(image_data))
                return image
            else:
                print("❌ No image found in Automatic1111 response")
                raise Exception("No image found in response")
        else:
            print(f"❌ Error from Automatic1111 API: {response.status_code}, {response.text}")
            raise Exception(f"API error: {response.text}")
    
    except Exception as e:
        print(f"❌ Error generating image with Automatic1111: {str(e)}")
        raise

def generate_image_with_llava(prompt, model_name="llava", width=512, height=512):
    """
    Generate an image description using LLaVA's multimodal capabilities
    Note: LLaVA doesn't actually generate images, but can provide detailed descriptions
    """
    try:
        # Prepare the API call
        url = f"{OLLAMA_HOST}/api/generate"
        payload = {
            "model": model_name,
            "prompt": f"Generate a detailed description of what an image of '{prompt}' would look like. Make it detailed and vivid.",
            "stream": False
        }
        
        # Make the API call
        response = requests.post(url, json=payload, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            description = result.get("response", "")
            
            # Create a text image with the description
            image = create_text_image(prompt, description, width, height)
            return image
        else:
            print(f"❌ Error from LLaVA API: {response.status_code}, {response.text}")
            raise Exception(f"API error: {response.text}")
    
    except Exception as e:
        print(f"❌ Error generating with LLaVA: {str(e)}")
        raise

def create_text_image(prompt, description, width=512, height=512):
    """Create an image with text description when image generation fails"""
    # Create a gradient background
    image = Image.new('RGB', (width, height), (255, 255, 255))
    draw = ImageDraw.Draw(image)
    
    # Create a gradient background
    for y in range(height):
        # Calculate color based on position
        r = int(100 + (y / height) * 50)
        g = int(150 + (y / height) * 50)
        b = int(200 + (y / height) * 30)
        draw.line([(0, y), (width, y)], fill=(r, g, b))
    
    # Try to use a nice font
    try:
        title_font = ImageFont.truetype("Arial", 24)
        caption_font = ImageFont.truetype("Arial", 16)
    except:
        title_font = ImageFont.load_default()
        caption_font = title_font
    
    # Add the prompt text to the image
    draw.text(
        (width // 2, 50),
        f"Prompt: {prompt}",
        font=title_font,
        fill=(255, 255, 255),
        anchor="mm"
    )
    
    # Add description - wrap text to fit
    max_width = width - 60
    lines = []
    words = description.split()
    current_line = ""
    
    for word in words:
        test_line = current_line + " " + word if current_line else word
        # Estimate text width (this is approximate)
        if len(test_line) * 10 < max_width:  # rough estimate of text width
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word
    
    if current_line:
        lines.append(current_line)
    
    # Limit to a reasonable number of lines
    max_lines = 15
    if len(lines) > max_lines:
        lines = lines[:max_lines-1] + ["..."]
    
    # Draw the lines
    y_position = 100
    for line in lines:
        draw.text(
            (30, y_position),
            line,
            font=caption_font,
            fill=(255, 255, 255)
        )
        y_position += 24
    
    return image

def create_fallback_image(prompt, error_message, width=512, height=512):
    """Create a fallback image when generation fails"""
    # Create a gradient background
    image = Image.new('RGB', (width, height), (255, 255, 255))
    draw = ImageDraw.Draw(image)
    
    # Create a gradient background
    for y in range(height):
        # Calculate color based on position
        r = int(100 + (y / height) * 50)
        g = int(150 + (y / height) * 50)
        b = int(200 + (y / height) * 30)
        draw.line([(0, y), (width, y)], fill=(r, g, b))
    
    # Try to use a nice font
    try:
        title_font = ImageFont.truetype("Arial", 28)
        caption_font = ImageFont.truetype("Arial", 20)
    except:
        title_font = ImageFont.load_default()
        caption_font = title_font
    
    # Add error message
    draw.text(
        (width // 2, height // 3),
        error_message,
        font=caption_font,
        fill=(255, 0, 0),
        anchor="mm"
    )
    
    # Add the prompt text to the image
    draw.text(
        (width // 2, height // 2),
        f"Prompt: {prompt}",
        font=title_font,
        fill=(255, 255, 255),
        anchor="mm"
    )
    
    # Add help message based on what's missing
    if not ensure_ollama_running():
        message = "Install Ollama and start it with 'ollama serve'"
    elif not SD_API_AVAILABLE:
        message = "Install Automatic1111 and start the API server"
    else:
        message = "Check logs for more details on the error"
    
    draw.text(
        (width // 2, height * 2/3),
        message,
        font=caption_font,
        fill=(255, 255, 255),
        anchor="mm"
    )
    
    return image

@app.route('/')
def index():
    """Render the main page"""
    # Add a timestamp query parameter to prevent caching
    timestamp = int(time.time())
    
    # Get status of Ollama
    ollama_running = ensure_ollama_running()
    
    # Check if SD API is available
    sd_available = check_sd_api_available()
    
    # Get available models
    available_models = []
    if ollama_running:
        models = get_available_models()
        for model in models:
            model_name = model.get("name")
            if model_name in MODELS:
                available_models.append({
                    "name": model_name,
                    "description": MODELS[model_name]["description"]
                })
    
    # Add models that are in our list but not yet pulled
    for model_name, model_info in MODELS.items():
        if not any(m.get("name") == model_name for m in available_models):
            status = "not_pulled"
            if model_name in MODEL_PULLING_STATUS:
                status = MODEL_PULLING_STATUS[model_name]
                
            available_models.append({
                "name": model_name,
                "description": model_info["description"],
                "status": status
            })
    
    return render_template(
        'index_ollama.html', 
        timestamp=timestamp,
        ollama_running=ollama_running,
        sd_available=sd_available,
        available_models=available_models
    )

@app.route('/generate', methods=['POST'])
def generate():
    """Generate an image based on the provided text prompt"""
    # Get the text prompt from the form
    prompt = request.form.get('prompt', '')
    
    if not prompt:
        return jsonify({'success': False, 'error': 'No prompt provided'}), 400
    
    # Get model selection
    model_name = request.form.get('model', DEFAULT_MODEL)
    
    # Get image size from the form
    size_option = request.form.get('size', '512x512')
    if 'x' in size_option:
        width, height = map(int, size_option.split('x'))
    else:
        width, height = 512, 512
    
    try:
        # Check if Ollama is running
        if not ensure_ollama_running():
            return jsonify({
                'success': False,
                'error': 'Ollama is not running. Please install and start Ollama.'
            }), 500
        
        # Check if model is available
        if not is_model_available(model_name):
            # Try to pull the model
            pull_status = pull_model(model_name)
            
            if pull_status["status"] == "pulling":
                return jsonify({
                    'success': False,
                    'error': f"Model {model_name} is being downloaded. Please wait and try again later."
                }), 500
            elif pull_status["status"] == "failed":
                return jsonify({
                    'success': False,
                    'error': f"Failed to download model {model_name}. Please pull it manually with 'ollama pull {model_name}'."
                }), 500
            else:
                return jsonify({
                    'success': False,
                    'error': f"Model {model_name} is not available. Please pull it with 'ollama pull {model_name}'."
                }), 500
        
        # Generate a unique filename based on timestamp and random uuid
        timestamp = int(time.time())
        filename = f"{uuid.uuid4()}_{timestamp}.png"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Generate the image based on model type
        print(f"Generating image for prompt: '{prompt}' using model: {model_name}")
        
        # Determine the model type and use appropriate generator
        model_type = MODELS.get(model_name, {}).get("type", "unknown")
        
        # Enhance prompt if using diffusion
        if model_type == "diffusion":
            # First, enhance the prompt using stable-diffusion-prompt-generator if available
            enhanced_prompt = enhance_prompt_with_generator(prompt)
            
            # Use SD API if available
            if SD_API_AVAILABLE:
                image = generate_image_with_automatic1111(enhanced_prompt, width, height)
            else:
                raise Exception("Stable Diffusion API is not available. Please install Automatic1111 with API enabled.")
        elif model_type == "multimodal":
            # Use LLaVA-like generator
            image = generate_image_with_llava(prompt, model_name, width, height)
        else:
            # Fallback to default
            image = create_fallback_image(
                prompt, 
                f"Unsupported model type: {model_type}", 
                width, 
                height
            )
        
        # Save the image
        image.save(filepath)
        
        # Add timestamp to prevent browser caching
        image_url = url_for('static', filename=f'images/{filename}') + f'?t={timestamp}'
        
        # Return success response with image path
        return jsonify({
            'success': True,
            'message': 'Image generated successfully',
            'image_path': image_url,
            'timestamp': timestamp
        })
    
    except Exception as e:
        # Print full error details to console
        import traceback
        traceback.print_exc()
        
        # Generate a fallback image with error message
        try:
            error_message = str(e)
            if len(error_message) > 100:
                error_message = error_message[:97] + "..."
                
            timestamp = int(time.time())
            filename = f"error_{uuid.uuid4()}_{timestamp}.png"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            fallback_image = create_fallback_image(prompt, error_message, width, height)
            fallback_image.save(filepath)
            
            image_url = url_for('static', filename=f'images/{filename}') + f'?t={timestamp}'
            
            # Return error response with fallback image
            return jsonify({
                'success': False,
                'error': str(e),
                'fallback_image': image_url
            }), 500
        except:
            # Return plain error if even fallback fails
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

@app.route('/pull_model/<model_name>', methods=['POST'])
def start_model_pull(model_name):
    """Start pulling a model"""
    if model_name not in MODELS:
        return jsonify({
            'success': False,
            'error': f"Unknown model: {model_name}"
        }), 400
    
    # Check if Ollama is running
    if not ensure_ollama_running():
        return jsonify({
            'success': False,
            'error': 'Ollama is not running. Please install and start Ollama.'
        }), 500
    
    # Start pulling the model
    pull_status = pull_model(model_name)
    
    return jsonify({
        'success': True,
        'status': pull_status["status"],
        'message': f"Started pulling model {model_name}"
    })

@app.route('/model_status/<model_name>', methods=['GET'])
def get_model_status(model_name):
    """Get the status of a model"""
    if model_name not in MODELS:
        return jsonify({
            'success': False,
            'error': f"Unknown model: {model_name}"
        }), 400
    
    # Check if model is available locally
    if is_model_available(model_name):
        return jsonify({
            'success': True,
            'status': 'available'
        })
    
    # Check pull status
    if model_name in MODEL_PULLING_STATUS:
        return jsonify({
            'success': True,
            'status': MODEL_PULLING_STATUS[model_name]
        })
    
    return jsonify({
        'success': True,
        'status': 'not_pulled'
    })

# Custom route to serve images with no caching
@app.route('/image/<path:filename>')
def serve_image(filename):
    response = send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

if __name__ == '__main__':
    # Check services on startup
    ollama_running = ensure_ollama_running()
    sd_available = check_sd_api_available()
    
    if not ollama_running:
        print("⚠️ WARNING: Ollama is not running. Install and start Ollama with 'ollama serve'")
    
    if not sd_available:
        print("⚠️ WARNING: Automatic1111 API is not available.")
        print("📋 To use Stable Diffusion:")
        print("1. Install Automatic1111 WebUI from https://github.com/AUTOMATIC1111/stable-diffusion-webui")
        print("2. Start it with the '--api' flag (add this to webui-user.bat or COMMANDLINE_ARGS in webui-user.sh)")
        print("3. Make sure it's running on http://localhost:7860")
    
    app.run(debug=True)