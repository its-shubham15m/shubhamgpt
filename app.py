import streamlit as st
import io, os
from dialoGPT import generate_response
from qna import get_answer
from text_to_image import generate_image
from text_generation import generate_text_response
from summarization import summarization_text

st.title("सुभम GPT")

def load_css():
    css_file = os.path.join("assets/styles.css")
    with open(css_file, "r") as f:
        css = f"<style>{f.read()}</style>"
        st.markdown(css, unsafe_allow_html=True)


# Initialize session state
ms = st.session_state
if "themes" not in ms:
    ms.themes = {
        "current_theme": "light",
        "refreshed": True,
        "light": {
            "theme.base": "dark",
            "theme.backgroundColor": "black",
            "theme.primaryColor": "#c98bdb",
            "theme.secondaryBackgroundColor": "#092635",
            "theme.textColor": "white",
            "button_face": "🌜"
        },
        "dark": {
            "theme.base": "light",
            "theme.backgroundColor": "white",
            "theme.primaryColor": "#FF7B36",
            "theme.secondaryBackgroundColor": "#FFDFBE",
            "theme.textColor": "#0a1464",
            "button_face": "🌞"
        }
    }


# Function to change theme
def change_theme():
    previous_theme = ms.themes["current_theme"]
    tdict = ms.themes["light"] if ms.themes["current_theme"] == "light" else ms.themes["dark"]
    for vkey, vval in tdict.items():
        if vkey.startswith("theme"):
            st._config.set_option(vkey, vval)

    ms.themes["refreshed"] = False
    if previous_theme == "dark":
        ms.themes["current_theme"] = "light"
    elif previous_theme == "light":
        ms.themes["current_theme"] = "dark"


# Button face based on current theme
btn_face = ms.themes["light"]["button_face"] if ms.themes["current_theme"] == "light" else ms.themes["dark"][
    "button_face"]

# Button to change theme
st.button(btn_face, on_click=change_theme)

# Check if theme needs to be refreshed
if not ms.themes["refreshed"]:
    ms.themes["refreshed"] = True


# Function to initialize session states for each model
def initialize_model_states():
    if "model_states" not in st.session_state:
        st.session_state.model_states = {
            "Text-GenerationLLM": {"messages": [], "chat_history_ids": None, "max_tokens": 200},
            "Image Generation": {"messages": [], "chat_history_ids": None},
            "Text Summarization": {"messages": [], "chat_history_ids": None},
            "Dialogue Generation": {"messages": [], "chat_history_ids": None},
            "Question Answering": {"messages": [], "chat_history_ids": None}
        }

    # Initialize current_model if not already present
    if "current_model" not in st.session_state:
        st.session_state.current_model = "Text-GenerationLLM"  # Initialize with a default model

    # Initialize messages for the current model if not already present
    current_model = st.session_state.current_model
    if "messages" not in st.session_state.model_states[current_model]:
        st.session_state.model_states[current_model]["messages"] = []

# Initialize model states if not already present
initialize_model_states()

# Sidebar for model selection
st.sidebar.image("assets/logo.png")
st.sidebar.title("Shubham-GPT")
st.sidebar.subheader("Select GPT-Model")
model_option = st.sidebar.radio("Choose a model:", ("Text-GenerationLLM", "Image Generation", "Text Summarization", "Dialogue Generation", "Question Answering"))

# Update session state based on selected model
if "current_model" not in st.session_state:
    st.session_state.current_model = model_option

if model_option != st.session_state.current_model:
    if model_option not in st.session_state.model_states:
        st.session_state.model_states[model_option] = {"messages": [], "chat_history_ids": None}
    
    st.session_state.current_model = model_option

# Add headings for each model
if model_option == "Text-GenerationLLM":
    st.header("Text-GenerationLLM Model")
    st.caption("powered by mistralai/Mistral-7B-Instruct-v0.2")
    max_tokens = st.session_state.model_states[model_option].get("max_tokens", 200)
    max_tokens = st.sidebar.slider("Max Tokens", min_value=10, max_value=500, value=max_tokens)
    st.session_state.model_states[model_option]["max_tokens"] = max_tokens
elif model_option == "Image Generation":
    st.header("Image Generation Model")
    st.caption("powered by 'stabilityai/stable-diffusion-xl-base-1.0' & 'runwayml/stable-diffusion-v1-5'")
    st.sidebar.image_model_option = st.sidebar.selectbox("Choose an image generation model:", ("Stable Diffusion XL", "Stable Diffusion v1.5"))
elif model_option == "Text Summarization":
    st.header("Text Summarization Model")
    st.caption("powered by facebook/bart-large-cnn")
elif model_option == "Dialogue Generation":
    st.header("Dialogue Generation Model")
    st.caption("powered by microsoft/DialoGPT-large")
elif model_option == "Question Answering":
    st.header("Question Answering Model")
    st.caption("powered by deepset/bert-large-uncased-whole-word-masking-squad2")

# Display chat messages from history on app rerun
if "messages" in st.session_state.model_states[model_option]:
    for message in st.session_state.model_states[model_option]["messages"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
        if "image" in message:
            st.chat_message("assistant").image(message["image"], caption=message["prompt"], use_column_width=True)

# React to user input
prompt = st.chat_input("Message सुभम GPT")
if prompt:
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    # Add user message to chat history
    st.session_state.model_states[model_option]["messages"].append({"role": "user", "content": prompt})

    if model_option == "Dialogue Generation":
        # Generate a response using the dialogue generation model
        response = generate_response(prompt)
        
        # Display assistant message in chat message container
        with st.chat_message("assistant"):
            st.markdown(response)
        
        # Add assistant response to chat history
        st.session_state.model_states[model_option]["messages"].append({"role": "assistant", "content": response})

    elif model_option == "Question Answering":
        # Assume the context is the concatenation of all previous messages
        context = " ".join([msg["content"] for msg in st.session_state.model_states[model_option]["messages"] if msg["role"] == "user"])
        response = get_answer(prompt, context)
        
        # Display assistant message in chat message container
        with st.chat_message("assistant"):
            st.markdown(response)
        
        # Add assistant response to chat history
        st.session_state.model_states[model_option]["messages"].append({"role": "assistant", "content": response})

    elif model_option == "Image Generation":
        if not st.secrets.api_key:
            st.info("Please add your Hugging Face Token to continue.")
            st.stop()

        # Generate image based on the prompt
        image, filename = generate_image(prompt, st.secrets.api_key, st.sidebar.image_model_option)
        if image:
            msg = f'Here is your image related to "{prompt}"'
            st.session_state.model_states[model_option]["messages"].append({"role": "assistant", "content": msg, "prompt": prompt, "image": image})
            st.chat_message("assistant").write(msg)
            st.chat_message("assistant").image(image, caption=prompt, use_column_width=True)

            # Download button for the image
            image_bytes = io.BytesIO()
            image.save(image_bytes, format='PNG')
            st.download_button(
                label="Download Image",
                data=image_bytes.getvalue(),
                file_name=f"{filename}.png",  # Set filename based on prompt
                mime="image/png"
            )
        else:
            st.error("Failed to generate the image. Please try again.")

    elif model_option == "Text-GenerationLLM":
        # Generate response using Text-GenerationLLM model
        text_response = generate_text_response(prompt)
        
        # Display assistant message in chat message container
        with st.chat_message("assistant"):
            st.markdown(text_response)
        
        # Add assistant response to chat history
        st.session_state.model_states[model_option]["messages"].append({"role": "assistant", "content": text_response})
    
    elif model_option == "Text Summarization":
        if prompt:
            # Generate text summarization
            summarization_result = summarization_text({"inputs": prompt})
        
            # Check if summarization was successful
            if isinstance(summarization_result, list) and len(summarization_result) > 0:
                first_result = summarization_result[0]  # Assuming you only need the first result
                if "summary_text" in first_result:
                    summary_text = first_result["summary_text"]
                    # Display assistant message in chat message container
                    with st.chat_message("assistant"):
                        st.markdown(summary_text)
                
                    # Add assistant response to chat history
                    st.session_state.model_states[model_option]["messages"].append({"role": "assistant", "content": summary_text})
                else:
                    st.error("No summary text found in API response.")
            else:
                st.error("Empty or invalid response received from summarization API.")
