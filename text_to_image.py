import requests
import io
from PIL import Image

API_URLS = {
    "Stable Diffusion XL": "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0",
    "Stable Diffusion v1.5": "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5"
}

def query_model(prompt, api_key, model_name):
    headers = {"Authorization": f"Bearer {api_key}"}
    payload = {"inputs": prompt}
    response = requests.post(API_URLS[model_name], headers=headers, json=payload)
    
    # Check if the request was successful
    if response.status_code == 200:
        return response.content
    else:
        print(f"Error: API request failed with status code {response.status_code}")
        return None

def generate_image(prompt, api_key, model_name):
    try:
        image_bytes = query_model(prompt, api_key, model_name)
        if image_bytes:
            image = Image.open(io.BytesIO(image_bytes))
            
            # Generate a filename based on the prompt (you can modify this as needed)
            filename = f"{prompt.replace(' ', '_')}_image.png"
            
            return image, filename
        else:
            print("Error: Failed to retrieve image bytes from API")
            return None, None
    except requests.exceptions.RequestException as e:
        print(f"Error making request to API: {e}")
    except IOError as e:
        print(f"Error opening image: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    return None, None
