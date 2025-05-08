import streamlit as st

def show_header():
    """
    Displays the application header
    """
    header_html = """
    <div class="main-header">
        <div class="row">
            <div class="col s12">
                <h3><i class="material-icons left">image</i> Text to Image Generator</h3>
                <p>Transform your text into beautiful images with ease</p>
            </div>
        </div>
    </div>
    """
    st.markdown(header_html, unsafe_allow_html=True)