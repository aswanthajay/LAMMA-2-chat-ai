import json
import streamlit as st
from cloudflare import Cloudflare

# Set up the app title
st.title("Code Assist Bot by Aswanth - Based on LLAMA 3.1")

# Initialize Cloudflare client with API token
client = Cloudflare(api_token=st.secrets["CLOUDFLARE_API_TOKEN"])

# Initialize chat history if not already done
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("What is up?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Prepare assistant response
    with st.chat_message("assistant"):
        try:
            # Run the model on Cloudflare Workers with streaming enabled
            with client.workers.ai.with_streaming_response.run(
                account_id=st.secrets["CLOUDFLARE_ACCOUNT_ID"],
                model_name="@cf/meta/llama-3.1-8b-instruct-fast",
                messages=[
                    {"role": "system", "content": "AI name: Aira Chatbot, Made by Aswanth Ajay and team Votion Cloud, Version 0.9 ASW Deepcode Alpha"},
                    *st.session_state.messages,
                ],
                stream=True,
            ) as response:
                # Token iterator for streaming response
                def iter_tokens(r):
                    for line in r.iter_lines():
                        if line.startswith("data: ") and not line.endswith("[DONE]"):
                            entry = json.loads(line.replace("data: ", ""))
                            yield entry["response"]

                completion = "".join(iter_tokens(response))
                st.markdown(completion)

            # Append assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": completion})

        except Exception as e:
            st.error(f"An error occurred: {e}")

