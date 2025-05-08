import streamlit as st

def show_sidebar():
    """
    Displays the sidebar with customization options
    Returns a dictionary containing all settings
    """
    with st.sidebar:
        st.markdown('<h4 class="center-align">Image Settings</h4>', unsafe_allow_html=True)
        
        st.markdown('<div class="card-panel">', unsafe_allow_html=True)
        
        # Image dimensions
        st.markdown("#### Image Size")
        col1, col2 = st.columns(2)
        with col1:
            width = st.number_input("Width", min_value=100, max_value=1920, value=800, step=50)
        with col2:
            height = st.number_input("Height", min_value=100, max_value=1080, value=600, step=50)
        
        # Font settings
        st.markdown("#### Font Settings")
        font_size = st.slider("Font Size", min_value=10, max_value=120, value=40)
        font_color = st.color_picker("Font Color", "#FFFFFF")
        
        # Background settings
        st.markdown("#### Background")
        bg_options = ["Solid Color", "Gradient", "Transparent"]
        bg_type = st.selectbox("Background Type", bg_options)
        
        if bg_type == "Solid Color":
            bg_color = st.color_picker("Background Color", "#000000")
            bg_settings = {"type": "solid", "color": bg_color}
        elif bg_type == "Gradient":
            col1, col2 = st.columns(2)
            with col1:
                gradient_start = st.color_picker("Start Color", "#000000")
            with col2:
                gradient_end = st.color_picker("End Color", "#0000FF")
            
            gradient_direction = st.selectbox("Direction", ["Horizontal", "Vertical", "Diagonal"])
            bg_settings = {
                "type": "gradient", 
                "start_color": gradient_start, 
                "end_color": gradient_end,
                "direction": gradient_direction.lower()
            }
        else:
            bg_settings = {"type": "transparent"}
        
        # Text effects
        st.markdown("#### Text Effects")
        text_effects = st.multiselect(
            "Effects", 
            ["Shadow", "Glow", "Outline", "Bold", "Italic"],
            default=["Shadow"]
        )
        
        effect_settings = {}
        if "Shadow" in text_effects:
            shadow_color = st.color_picker("Shadow Color", "#333333")
            shadow_blur = st.slider("Shadow Blur", 0, 20, 5)
            effect_settings["shadow"] = {"color": shadow_color, "blur": shadow_blur}
            
        if "Glow" in text_effects:
            glow_color = st.color_picker("Glow Color", "#FFFFFF")
            glow_strength = st.slider("Glow Strength", 0, 20, 10)
            effect_settings["glow"] = {"color": glow_color, "strength": glow_strength}
            
        if "Outline" in text_effects:
            outline_color = st.color_picker("Outline Color", "#000000")
            outline_width = st.slider("Outline Width", 1, 10, 2)
            effect_settings["outline"] = {"color": outline_color, "width": outline_width}
        
        # Text alignment
        alignment = st.selectbox("Text Alignment", ["Center", "Left", "Right"])
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Advanced options toggle
        with st.expander("Advanced Options"):
            padding = st.slider("Padding", 10, 100, 40)
            line_spacing = st.slider("Line Spacing", 1.0, 3.0, 1.5, 0.1)
            word_spacing = st.slider("Word Spacing", 1, 10, 4)
            
            # Text wrapping
            text_wrap = st.checkbox("Auto Text Wrap", value=True)
            
            # Text transformation
            text_transform = st.selectbox("Text Transform", 
                                         ["None", "Uppercase", "Lowercase", "Capitalize"])
    
    # Combine all settings
    settings = {
        "dimensions": {"width": width, "height": height},
        "font": {"size": font_size, "color": font_color},
        "background": bg_settings,
        "effects": effect_settings,
        "text_effects": text_effects,
        "alignment": alignment.lower(),
        "advanced": {
            "padding": padding,
            "line_spacing": line_spacing,
            "word_spacing": word_spacing,
            "text_wrap": text_wrap,
            "text_transform": text_transform.lower() if text_transform != "None" else None
        }
    }
    
    return settings