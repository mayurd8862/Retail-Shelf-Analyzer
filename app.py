import streamlit as st
import google.generativeai as genai
from PIL import Image
import os
from dotenv import load_dotenv
load_dotenv()

# --- Configuration ---
API_KEY = os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    st.error("Error: GOOGLE_API_KEY environment variable not set.")
    st.stop()

genai.configure(api_key=API_KEY)

# --- Page Config ---
st.set_page_config(
    page_title="Retail Shelf Analyzer",
    page_icon="🛍️"
)

st.title("🛍️ Retail Shelf Analyzer")
# st.markdown("Upload an image of retail shelves for detailed analysis")

st.subheader("Upload an image of retail shelves for detailed analysis", divider="rainbow")

def load_image(image_file):
    try:
        img = Image.open(image_file)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        return img
    except Exception as e:
        st.error(f"Error loading image: {e}")
        return None

def analyze_product_image_with_gemini(img, custom_prompt=None):
    if not img:
        return "Error: Could not load image."

    model = genai.GenerativeModel('gemini-1.5-flash')

    if custom_prompt:
        prompt = custom_prompt
    else:
        prompt = """
        You are a retail shelf analysis expert. Given a shelf image, analyze it visually and provide a detailed report structured exactly as follows. The goal is to evaluate product arrangement, compliance with display guidelines, and identify any merchandising opportunities or issues.

        Please format the output using the exact structure below:

        ---

        ### ANALYSIS RESULTS  
        **SHELF ANALYSIS COMPLETE**

        **Priority Actions:**  
        Identify 4–6 key actions required to improve the visual arrangement, accessibility, and compliance of the shelf display. Focus on:
        - Removing any obstructive promotional material or signage
        - Reorienting products to face-forward (horizontally, not vertically)
        - Grouping similar product variants together (e.g., Golden Oreos in one section)
        - Filling visible gaps to ensure the shelf looks full and consistent
        - Aligning and straightening packages for a neat visual presentation

        **Areas of Compliance:**  
        List 3–5 positive observations where the shelf follows merchandising guidelines, such as:
        - Proper grouping of product types
        - Required orientation (facing forward)
        - Visible price tags
        - Product variety on display

        **Additional Notes:**  
        Provide extra observations and suggestions, such as:
        - Brand blocking effectiveness
        - Mixing of flavors or product types
        - Visibility of promotional offers or missing signage
        - Recommendations for better customer experience

        ---  
        Do not provide any explanation or markdown. Only return the structured report text in plain format.
        """

    try:
        response = model.generate_content([prompt, img])
        raw_text = response.text.strip()

        if raw_text.startswith("```") and raw_text.endswith("```"):
            raw_text = raw_text.split("```")[1].strip()

        return raw_text

    except Exception as e:
        st.error(f"An error occurred while communicating with Gemini API: {e}")
        return f"Error: Gemini API communication failed. {e}"

# --- Sidebar ---
with st.sidebar:
    st.header("⚙️ Settings")
    custom_prompt = st.text_area(
        "Custom Analysis Prompt (Optional)",
        help="Leave empty to use default prompt",
        height=200
    )

# --- Main Content ---

# uploaded_file = st.file_uploader("Upload a shelf image", type=['png', 'jpg', 'jpeg', 'webp'])
enable_camera = st.checkbox("Click here to take a photo with your CAMERA")

uploaded_file = st.file_uploader(
    "Upload a shelf image",
    type=['png', 'jpg', 'jpeg', 'webp'],
    disabled=enable_camera  # Disable uploader if camera is enabled
)



image_main = None

if enable_camera:
    cam = st.camera_input("Take a picture")
    if cam is not None:
        image_main = cam
elif uploaded_file is not None:
    image_main = uploaded_file

if image_main is not None:
    img = load_image(image_main)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image(img, use_container_width=True)

    st.subheader("Analysis Results")
    if st.button("Analyze Shelf"):
        with st.spinner("Analyzing Shelf... Please wait..."):
            analysis = analyze_product_image_with_gemini(img, custom_prompt if custom_prompt else None)
            st.markdown(analysis)
else:
    st.info("👆 Please upload an image to begin analysis")


