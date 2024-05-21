import streamlit as st
import requests

API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"


def generate_text_response(prompt, api_key, max_tokens=150):
    try:
        headers = {"Authorization": f"Bearer {api_key}"}
        payload = {"inputs": prompt, "options": {"max_tokens": max_tokens}}

        generated_text = ""
        continuation_token = None

        while True:
            if continuation_token:
                payload["options"]["continuation_token"] = continuation_token

            # Make POST request to API
            response = requests.post(API_URL, headers=headers, json=payload)
            response.raise_for_status()  # Raise exception for HTTP errors

            # Parse JSON response
            if response.status_code == 200:
                json_response = response.json()

                if isinstance(json_response, list):
                    # Append each generated text in the list
                    for item in json_response:
                        generated_text += item.get("generated_text", "") + "\n"
                        continuation_token = item.get("continuation_token")
                elif isinstance(json_response, dict):
                    # Single generated text
                    generated_text += json_response.get("generated_text", "") + "\n"
                    continuation_token = json_response.get("continuation_token")

                # Break if no continuation token is returned
                if not continuation_token:
                    break

            elif response.status_code == 403:
                return f"API request failed: Forbidden - Check your API key and permissions. Response content: {response.content}"
            else:
                return f"API request failed with status code {response.status_code}. Response content: {response.content}"

        return generated_text.strip()

    except requests.exceptions.RequestException as e:
        return f"Error making request to API: {e}"
    except ValueError as e:
        return f"Error parsing JSON response: {e}"
    except Exception as e:
        return f"Unexpected error: {e}"
