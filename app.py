import streamlit as st
from groq import Groq
import os

st.set_page_config(
    page_title="Nico Stengel - AI Twin",
    page_icon="🤖",
    layout="centered"
)

st.markdown("""
    <style>
    .main {
        background-color: #f5f7f9;
    }
    .stChatMessage {
        border-radius: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

def load_bio():
    try:
        with open("bio.txt", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "Error: bio.txt not found. Please ensure the file exists."

my_resume_data = load_bio()

with st.sidebar:
    st.title("Settings")
    api_key = st.text_input("Enter Groq API Key", type="password")
    st.markdown("---")
    st.markdown("### Quick Facts")
    st.markdown("- **Name:** Nico Stengel")
    st.markdown("- **Focus:** AI & Data Science")
    st.markdown("- **Ex-BMW** Software Engineer")
    st.info("This AI answers questions based on Nico's professional profile.")

st.title("🤖 Chat with Nico's AI Twin")
st.write("Welcome! I am an AI assistant trained on Nico Stengel's CV and projects. How can I help you today?")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system",
            "content": f"""
            You are the professional AI Twin of Nico Stengel. 
            CONTEXT DATA:
            {my_resume_data}
            
            GUIDELINES:
            1. IDENTITY: You are Nico's digital representative. Speak professionally.
            2. LANGUAGE: ALWAYS answer in English.
            3. TRUTH: Use ONLY the provided context. If information is missing, say you don't know and offer his contact info.
            4. KEY POINTS: Highlight his 3-year experience at BMW and his current AI studies at OTH Regensburg.
            5. CONTACT: If asked, his email is nico.stengel@outlook.de.
            """
        }
    ]

for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"], avatar="🧑‍💻" if message["role"] == "user" else "🤖"):
            st.markdown(message["content"])

if api_key:
    client = Groq(api_key=api_key)

    if prompt := st.chat_input("Ask me about Nico's experience at BMW or his AI projects..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
       
        with open("logs.txt", "a", encoding="utf-8") as f:
            f.write(f"User Question: {prompt}\n")

        with st.chat_message("user", avatar="🧑‍💻"):
            st.markdown(prompt)
        with st.chat_message("user", avatar="🧑‍💻"):
            st.markdown(prompt)

        with st.chat_message("assistant", avatar="🤖"):
            response_placeholder = st.empty()
            full_response = ""
            
            try:
                completion = client.chat.completions.create(
                    model="llama3-8b-8192",
                    messages=st.session_state.messages,
                    stream=True,
                )
                
                for chunk in completion:
                    content = chunk.choices[0].delta.content
                    if content:
                        full_response += content
                        response_placeholder.markdown(full_response + "▌")
                
                response_placeholder.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})
            
            except Exception as e:
                st.error(f"An error occurred: {e}")

else:
    st.warning("👈 Please enter your Groq API Key in the sidebar to talk to the AI.")
    st.markdown("""
    ### Suggested Questions:
    * "What did Nico do at BMW?"
    * "Tell me about his studies at OTH Regensburg."
    * "What programming languages is he proficient in?"
    """)
