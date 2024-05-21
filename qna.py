import requests
import streamlit as st

API_URL = "https://api-inference.huggingface.co/models/deepset/bert-large-uncased-whole-word-masking-squad2"

def get_answer(question, context):
    try:
        # Fetch API key from Streamlit secrets
        api_key = st.secrets["api_key"]
        headers = {"Authorization": f"Bearer {api_key}"}
        payload = {
            "inputs": {
                "question": question,
                "context": context
            }
        }
        
        response = requests.post(API_URL, headers=headers, json=payload)
        response.raise_for_status()  # Raise exception for HTTP errors
        
        # Parse JSON response
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, dict) and "answer" in result:
                return result["answer"]
            elif isinstance(result, list) and len(result) > 0 and "answer" in result[0]:
                return result[0]["answer"]
            else:
                return {"error": "No answer found in API response."}
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