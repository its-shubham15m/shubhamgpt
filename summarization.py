import requests
import streamlit as st

API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"

def summarization_text(payload):
    try:
        # Fetch API key from Streamlit secrets
        api_key = st.secrets["api_key"]
        headers = {"Authorization": f"Bearer {api_key}"}
        
        # Make POST request to API
        response = requests.post(API_URL, headers=headers, json=payload)
        response.raise_for_status()  # Raise exception for HTTP errors
        
        # Parse JSON response
        if response.status_code == 200:
            return response.json()
        else:
            return {
                "error": f"Request failed with status code {response.status_code}",
                "details": response.text
            }
    
    except requests.exceptions.RequestException as e:
        return {"error": f"Request error: {e}"}
    except KeyError as e:
        return {"error": "API key not found. Please check your secrets.toml configuration."}
    except Exception as e:
        return {"error": f"Unexpected error: {e}"}