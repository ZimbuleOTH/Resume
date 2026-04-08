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
        background-color: #f8f9fa;
    }
    .stChatMessage {
        border-radius: 12px;
        border: 1px solid #e0e0e0;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
    }
    section[data-testid="stSidebar"] {
        background-color: #1e293b;
        color: white;
    }
    section[data-testid="stSidebar"] .stMarkdown {
        color: #f1f5f9;
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

api_key = st.secrets.get("GROQ_API_KEY")

with st.sidebar:
    st.title("👤 Nico Stengel")
    st.subheader("AI & Data Science Student")
    
    st.markdown("---")
    st.markdown("### 📞 Contact Details")
    st.markdown("📧 [Nico's Mail](mailto:nico.stengel@hotmail.com)")
    st.markdown("📱 +49 15151700704")
    st.markdown("📍 Regensburg, Germany")
    
    st.markdown("---")
    st.markdown("### 🚀 Career Highlights")
    st.markdown("✅ **Ex-BMW** Software Engineer")
    st.markdown("✅ **LMU Klinikum** Developer")
    st.markdown("✅ **OTH Regensburg** Student")
    
    if not api_key:
        st.markdown("---")
        api_key = st.text_input("Enter Groq API Key to chat", type="password")
    else:
        st.markdown("---")
        st.success("🤖 AI Engine: Online")

st.title("🤖 Chat with Nico's Digital Twin")
st.write("I am Nico's personal AI representative. Ask me anything about his professional journey, technical expertise, or current projects.")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system", 
            "content": f"""
            ROLE: You are the professional Digital Twin and exclusive representative of Nico Stengel. 
            CONTEXT: You know Nico's entire professional history based on this data: {my_resume_data}
            
            YOUR COMMUNICATION STYLE:
            1. PERSPECTIVE: Speak as Nico's well-informed agent. NEVER say "the document says" or "according to the text". 
            2. PHRASING: Use phrases like "Nico spent three years at BMW...", "He is currently mastering AI at OTH...", or "One of Nico's core strengths is...".
            3. TONE: Professional, tech-savvy, and highly supportive of Nico's career goals.
            4. LANGUAGE: Always respond in ENGLISH.
            5. LIMITS: If information is missing, politely steer the conversation back to his professional profile and offer his contact details.
            6. DIRECTNESS: Be concise but impressive.
            """
        }
    ]

for message in st.session_state.messages:
    if message["role"] != "system":
        avatar = "🧑‍💻" if message["role"] == "user" else "🤖"
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])

if api_key:
    try:
        client = Groq(api_key=api_key)
        
        if prompt := st.chat_input("Ask me about Nico's experience or skills..."):
            with open("logs.txt", "a", encoding="utf-8") as f:
                f.write(f"User Question: {prompt}\n")

            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user", avatar="🧑‍💻"):
                st.markdown(prompt)

            with st.chat_message("assistant", avatar="🤖"):
                response_placeholder = st.empty()
                full_response = ""
                
                completion = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
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
        st.error(f"AI Connection Error: {e}")
else:
    st.warning("Please provide a Groq API Key in the sidebar or Secrets to start the chat.")

st.markdown("---")
st.caption("Try asking: 'What was Nico's impact at BMW?' or 'What are his core technical skills?'")
with st.sidebar:
    st.markdown("---")
    input_password = st.text_input("Admin Access", type="password", placeholder="Enter code")
    if input_password and input_password == st.secrets.get("ADMIN_PASSWORD"):
        st.success("Admin Mode Active")
        if os.path.exists("logs.txt"):
            with open("logs.txt", "r", encoding="utf-8") as f:
                st.download_button(
                    label="📥 Download Logs",
                    data=f.read(),
                    file_name="nico_ai_logs.txt",
                    mime="text/plain"
                )
        else:
            st.info("No logs recorded yet.")
    elif input_password:
        st.error("Access Denied")
