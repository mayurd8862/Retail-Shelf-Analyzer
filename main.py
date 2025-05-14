import google.generativeai as genai
from PIL import Image
import os
import json
from dotenv import load_dotenv
import os
load_dotenv()
# --- Configuration ---
# Load the API key from an environment variable
API_KEY = os.getenv("GOOGLE_API_KEY")

if not API_KEY:
    print("Error: GEMINI_API_KEY environment variable not set.")
    print("Please set it before running the script.")
    exit()

genai.configure(api_key=API_KEY)

# --- Helper Functions ---

def load_image(image_path):
    """Loads an image from the given path."""
    try:
        img = Image.open(image_path)
        # Gemini API works well with RGB images
        if img.mode != 'RGB':
            img = img.convert('RGB')
        return img
    except FileNotFoundError:
        print(f"Error: Image file not found at {image_path}")
        return None
    except Exception as e:
        print(f"Error loading image: {e}")
        return None

def analyze_product_image_with_gemini(image_path, custom_prompt=None):

    img = load_image(image_path)
    if not img:
        return "Error: Could not load image."

    # Choose the Gemini Pro Vision model
    model = genai.GenerativeModel('gemini-1.5-flash')

    if custom_prompt:
        prompt = custom_prompt
    else:
        # Detailed default prompt asking for JSON output
        prompt = """
        Analyze the provided image of products on a retail shelf or rack.
        Identify each distinct product or group of identical products.
        For each distinct product type, provide the following information in a JSON list format:
        - "product_name": A descriptive name for the product (e.g., "Red Soda Cans", "Blue Cereal Box").
        - "estimated_count": An estimated count of this specific product visible.
        - "brand": The brand name, if visible and identifiable. If not, use "Unknown".
        - "category": A likely category (e.g., "Beverage", "Snack", "Cleaning Supply").
        - "packaging_type": (e.g., "Can", "Box", "Bottle", "Bag").
        - "color_primary": The dominant color of the product or packaging.
        - "shelf_location_description": A brief description of where it is on the shelf (e.g., "Top shelf, left side", "Middle row, center").
        - "distinguishing_features": Any other notable features (e.g., "Label shows a cartoon character", "Large size variant").

        If some information is not clearly visible or identifiable, use "N/A" or "Unknown" for that field.
        The output should be a valid JSON list of objects, where each object represents a distinct product type.
        Example of a single product entry:
        {
            "product_name": "BrandX Energy Drink",
            "estimated_count": 6,
            "brand": "BrandX",
            "category": "Beverage",
            "packaging_type": "Can",
            "color_primary": "Green",
            "shelf_location_description": "Middle shelf, right side",
            "distinguishing_features": "Sugar-free label visible"
        }
        Ensure the entire response is only the JSON list.
        """

    print("\nSending request to Gemini API. This may take a moment...")
    try:
        response = model.generate_content([prompt, img])

        # Attempt to extract and parse JSON
        raw_text = response.text
        # print(f"\n--- Raw Gemini Response Text ---\n{raw_text}\n------------------------------")

        # Sometimes Gemini might add markdown backticks around JSON
        if raw_text.strip().startswith("```json"):
            raw_text = raw_text.strip()[7:] # Remove ```json
            if raw_text.strip().endswith("```"):
                raw_text = raw_text.strip()[:-3] # Remove ```

        try:
            product_summary = json.loads(raw_text)
            return product_summary
        except json.JSONDecodeError as e:
            print(f"Warning: Could not parse Gemini's response as JSON. Error: {e}")
            print("Returning raw text output instead.")
            return raw_text # Return raw text if JSON parsing fails

    except Exception as e:
        print(f"An error occurred while communicating with Gemini API: {e}")
        if hasattr(e, 'response') and e.response: # For google.api_core.exceptions
            print(f"API Response Error: {e.response}")
        return f"Error: Gemini API communication failed. {e}"

def display_summary(summary_data, image_path):
    """Neatly prints the product summary."""
    print(f"\n--- Product Summary for: {image_path} ---")
    if isinstance(summary_data, list): # Successfully parsed JSON
        if not summary_data:
            print("No products identified or summary is empty.")
            return

        total_items_identified = 0
        for i, product in enumerate(summary_data):
            print(f"\nProduct Group #{i+1}:")
            print(f"  Name: {product.get('product_name', 'N/A')}")
            print(f"  Estimated Count: {product.get('estimated_count', 'N/A')}")
            print(f"  Brand: {product.get('brand', 'N/A')}")
            print(f"  Category: {product.get('category', 'N/A')}")
            print(f"  Packaging: {product.get('packaging_type', 'N/A')}")
            print(f"  Color: {product.get('color_primary', 'N/A')}")
            print(f"  Location: {product.get('shelf_location_description', 'N/A')}")
            print(f"  Features: {product.get('distinguishing_features', 'N/A')}")

            count = product.get('estimated_count')
            if isinstance(count, (int, float)):
                total_items_identified += count
            elif isinstance(count, str) and count.isdigit():
                 total_items_identified += int(count)


        print("\n--- Overall ---")
        print(f"Total distinct product groups identified: {len(summary_data)}")
        if total_items_identified > 0 :
             print(f"Estimated total individual items (sum of counts): {total_items_identified}")
        else:
            print("Could not sum total individual items (counts might be N/A or non-numeric).")

    elif isinstance(summary_data, str): # Raw text output or error message
        print(summary_data)
    else:
        print("Summary data is in an unexpected format.")
    print("--------------------------------------")


# --- Main Execution ---
if __name__ == "__main__":

    image_file_path = "prod.webp"
    # Example: image_file_path = "products_on_rack.jpg" # or "/path/to/your/image.png"

    if not os.path.exists(image_file_path):
        print(f"Error: The file '{image_file_path}' does not exist. Please check the path.")
    else:

        custom_user_prompt = None

        product_details = analyze_product_image_with_gemini(image_file_path, custom_prompt=custom_user_prompt)
        display_summary(product_details, image_file_path)