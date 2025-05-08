import streamlit as st
from components import header, sidebar, footer
from utils.image_generator import generate_image
from utils.text_processor import process_text
import base64

# Page configuration
st.set_page_config(
    page_title="Text to Image Generator",
    page_icon="🖼️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add Materialize CSS
def load_css():
    # Materialize CSS CDN link
    materialize_css = """
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/materialize/1.0.0/css/materialize.min.css">
    <link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/materialize/1.0.0/js/materialize.min.js"></script>
    
    <style>
        .main-header {
            background-color: #26a69a;
            color: white;
            padding: 20px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        
        .card-panel {
            border-radius: 8px;
        }
        
        .btn-generate {
            background-color: #26a69a;
            width: 100%;
        }
        
        .btn-download {
            margin-top: 10px;
            width: 100%;
        }
        
        .footer {
            margin-top: 30px;
            padding: 20px;
            text-align: center;
            color: #9e9e9e;
        }
        
        .image-container {
            display: flex;
            justify-content: center;
            margin-top: 20px;
        }
        
        /* Custom sidebar styling */
        .sidebar .sidebar-content {
            background-color: #f5f5f5;
        }
    </style>
    """
    st.markdown(materialize_css, unsafe_allow_html=True)

def get_image_download_link(img, filename, text):
    """Generates a link to download the generated image"""
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    href = f'<a class="waves-effect waves-light btn blue darken-3 btn-download" href="data:file/png;base64,{img_str}" download="{filename}">{text}<i class="material-icons right">download</i></a>'
    return href

# Load CSS
load_css()

# Display header
header.show_header()

# Display sidebar with options
settings = sidebar.show_sidebar()

# Main content
st.markdown('<div class="card-panel">', unsafe_allow_html=True)
st.markdown('<h5>Enter Text to Generate an Image</h5>', unsafe_allow_html=True)

# Text input
user_text = st.text_area("Your text", height=150)

# Generate button
generate_clicked = st.button("Generate Image", key="generate", 
                            help="Click to generate an image from your text",
                            use_container_width=True)

if generate_clicked and user_text:
    with st.spinner('Generating your image...'):
        # Process text based on settings
        processed_text = process_text(user_text, settings)
        
        # Generate image
        generated_image = generate_image(processed_text, settings)
        
        # Show the generated image
        st.markdown('<div class="image-container">', unsafe_allow_html=True)
        st.image(generated_image, caption="Generated Image", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Download button
        import io
        st.markdown(get_image_download_link(generated_image, "generated_image.png", "Download Image"), 
                   unsafe_allow_html=True)
elif generate_clicked and not user_text:
    st.error("Please enter some text to generate an image.")

st.markdown('</div>', unsafe_allow_html=True)

# Display footer
footer.show_footer()