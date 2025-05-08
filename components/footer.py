import streamlit as st

def show_footer():
    """
    Displays the application footer
    """
    footer_html = """
    <div class="footer">
        <div class="divider"></div>
        <p>
            <i class="material-icons tiny">code</i> 
            Developed with Streamlit & Materialize CSS
        </p>
        <p>
            <a href="https://github.com/AL-Kaisi/text-to-image-generator-gui" target="_blank" 
               class="waves-effect waves-light btn-small grey lighten-1">
                <i class="material-icons left">star</i>Star on GitHub
            </a>
        </p>
    </div>
    """
    st.markdown(footer_html, unsafe_allow_html=True)