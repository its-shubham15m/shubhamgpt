import requests
import streamlit as st

API_URL = "https://api-inference.huggingface.co/models/deepset/bert-large-uncased-whole-word-masking-squad2"


def get_answer(question, context, api_key):
    try:
        headers = {"Authorization": f"Bearer {api_key}"}
        payload = {
            "question": question,
            "context": context
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
    except Exception as e:
        return {"error": f"Unexpected error: {e}"}