import requests
import streamlit as st

API_URL = "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium"

def generate_response(prompt):
    try:
        # Fetch API key from Streamlit secrets
        api_key = st.secrets["api_key"]
        headers = {"Authorization": f"Bearer {api_key}"}
        
        # Prepare payload for the model API
        payload = {
            "inputs": prompt
        }
        
        # Make POST request to API
        response = requests.post(API_URL, headers=headers, json=payload)
        response.raise_for_status()  # Raise exception for HTTP errors
        
        # Parse JSON response
        if response.status_code == 200:
            json_response = response.json()
            if isinstance(json_response, list):
                # Handle list response, assuming it's a list of potential outputs
                if len(json_response) > 0 and isinstance(json_response[0], dict):
                    return json_response[0].get("generated_text", "No response text found")
                else:
                    return "No response text found"
            elif isinstance(json_response, dict):
                # Handle dictionary response, assuming it's a single response
                return json_response.get("generated_text", "No response text found")
            else:
                return "Unexpected response format"
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