# Text to Image Generator GUI

A web application that converts text descriptions into images using AI models. Built with Flask for the backend and Materialize CSS for the frontend. 

This version uses Hugging Face models for image generation, so it's completely free and doesn't require any API keys. The application can run 100% offline after the initial download of the models.

## Features

- **No API Keys Required**: Uses Hugging Face models that run locally
- **Works Offline**: After the initial model download, the app works without internet
- **GPU Support**: Automatically uses GPU if available for faster generation
- **CPU Fallback**: Works on CPU-only machines (slower but still functional)
- **Beautiful UI**: Modern interface built with Materialize CSS

## Features

- **AI-Powered Image Generation**: Transform text descriptions into realistic images
- **Multiple AI Models**: Support for different text-to-image AI models
- **Customizable Settings**: Adjust image dimensions, guidance scales, and more
- **Modern UI**: Beautiful interface built with Materialize CSS
- **Responsive Design**: Works well on desktop and mobile devices
- **Download Images**: Save generated images to your device

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/AL-Kaisi/text-to-image-generator-gui.git
   cd text-to-image-generator-gui
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   - Copy the `.env.example` file to `.env`
   - Edit the `.env` file and add your API keys
   ```bash
   cp .env.example .env
   # Now edit .env with your preferred text editor
   ```

5. **Run the application**:
   ```bash
   python app.py
   ```

6. **Access the web interface**:
   Open your browser and go to `http://localhost:5000`

## API Keys

This application requires API keys to generate images:

- **Replicate API**: Get your API key at [replicate.com/account](https://replicate.com/account)
- **Stability AI** (optional): Get your API key at [platform.stability.ai](https://platform.stability.ai/)

## Customization

### Changing the UI Theme

You can easily change the color theme by modifying the CSS classes in the templates:

1. Open `templates/base.html`
2. Change the color classes (e.g., replace `teal` with `blue`, `red`, `purple`, etc.)

### Adding New AI Models

To add support for additional AI models:

1. Modify the `utils/image_generator.py` file
2. Add a new generator function for your model
3. Update the model selection dropdown in `templates/index.html`

## Deployment

### Deploying to a Production Server

For production deployment, you can use Gunicorn:

```bash
gunicorn app:app
```

### Deploying to Heroku

```bash
heroku create
git push heroku main
heroku config:set REPLICATE_API_TOKEN=your-api-token-here
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.