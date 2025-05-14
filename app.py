# app.py
import streamlit as st
from PIL import Image
import os
from main import analyze_product_image_with_gemini
import json

# Configure Streamlit page
st.set_page_config(
    page_title="Retail Shelf Analyzer",
    page_icon="🛒",
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main {
        max-width: 1000px;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        padding: 10px 24px;
        border-radius: 8px;
        border: none;
    }
    .stButton>button:hover {
        background-color: #45a049;
    }
    .result-section {
        padding: 20px;
        background-color: #f9f9f9;
        border-radius: 10px;
        margin-top: 20px;
    }
    .upload-box {
        border: 2px dashed #ccc;
        border-radius: 5px;
        padding: 20px;
        text-align: center;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# App header
st.title("🛒 Retail Shelf Analyzer")
st.markdown("""
Upload an image of products on a retail shelf and get a detailed analysis using Google's Gemini AI.
""")

# Sidebar for additional options
with st.sidebar:
    st.header("Settings")
    show_raw_json = st.checkbox("Show raw JSON output", value=False)
    st.markdown("---")
    st.markdown("**Instructions:**")
    st.markdown("1. Upload an image of products on a shelf")
    st.markdown("2. Click 'Analyze Image'")
    st.markdown("3. View the results")

# Main content area
uploaded_file = st.file_uploader(
    "Upload a shelf image",
    type=["jpg", "jpeg", "png", "webp"],
    help="Upload a clear image of products on a retail shelf or rack"
)

if uploaded_file is not None:
    # Display the uploaded image
    st.subheader("Uploaded Image")
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Shelf Image")

    # Save the uploaded file temporarily
    temp_file_path = "temp_uploaded_image." + uploaded_file.name.split('.')[-1]
    with open(temp_file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    # Analyze button
    if st.button("Analyze Image", type="primary"):
        with st.spinner("Analyzing image with Gemini AI. This may take a moment..."):
            try:
                # Call the analysis function with default prompt
                result = analyze_product_image_with_gemini(temp_file_path)
                
                # Display results
                st.subheader("Analysis Results")
                
                if isinstance(result, list):  # JSON result
                    # Summary statistics
                    total_groups = len(result)
                    total_items = sum([p.get('estimated_count', 0) for p in result if isinstance(p.get('estimated_count'), int)])
                    
                    col1, col2 = st.columns(2)
                    col1.metric("Product Groups Identified", total_groups)
                    col2.metric("Total Items Estimated", total_items)
                    
                    # Detailed results in expandable sections
                    for i, product in enumerate(result):
                        with st.expander(f"Product Group {i+1}: {product.get('product_name', 'Unnamed')}"):
                            cols = st.columns(2)
                            cols[0].metric("Estimated Count", product.get('estimated_count', 'N/A'))
                            cols[1].metric("Brand", product.get('brand', 'N/A'))
                            
                            st.markdown(f"""
                            - **Category:** {product.get('category', 'N/A')}
                            - **Packaging:** {product.get('packaging_type', 'N/A')}
                            - **Primary Color:** {product.get('color_primary', 'N/A')}
                            - **Shelf Location:** {product.get('shelf_location_description', 'N/A')}
                            - **Features:** {product.get('distinguishing_features', 'N/A')}
                            """)
                    
                    # Show raw JSON if requested
                    if show_raw_json:
                        with st.expander("Raw JSON Output"):
                            st.code(json.dumps(result, indent=2), language="json")
                
                elif isinstance(result, str):  # Raw text or error
                    st.warning("The response couldn't be parsed as JSON. Showing raw output:")
                    st.text(result)
                
                # Clean up temporary file
                if os.path.exists(temp_file_path):
                    os.remove(temp_file_path)
                    
            except Exception as e:
                st.error(f"An error occurred during analysis: {str(e)}")
                if os.path.exists(temp_file_path):
                    os.remove(temp_file_path)