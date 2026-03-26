import streamlit as st
from groq import Groq

# --- 1. PAGE CONFIG & STYLING ---
st.set_page_config(
    page_title="Nico Stengel - AI Twin", 
    page_icon="🤖", 
    layout="centered"
)

# Custom CSS for a professional, modern look
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
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #1e293b;
        color: white;
    }
    section[data-testid="stSidebar"] .stMarkdown {
        color: #f1f5f9;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. LOAD DATA ---
def load_bio():
    try:
        with open("bio.txt", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "Error: bio.txt not found. Please ensure the file exists."

my_resume_data = load_bio()

# --- 3. API KEY LOGIC (HYBRID) ---
# Automatically pulls from Streamlit Cloud Secrets or local input
api_key = st.secrets.get("GROQ_API_KEY")

# --- 4. SIDEBAR (PROFESSIONAL PROFILE) ---
with st.sidebar:
    st.title("👤 Nico Stengel")
    st.subheader("AI & Data Science Student")
    
    st.markdown("---")
    st.markdown("### 📞 Contact Details")
    st.markdown("📧 [Email Nico](mailto:nico.stengel@outlook.de)")
    st.markdown("📱 +49 15151700704")
    st.markdown("📍 Regensburg, Germany")
    
    st.markdown("---")
    st.markdown("### 🚀 Career Highlights")
    st.markdown("✅ **Ex-BMW** Software Engineer")
    st.markdown("✅ **LMU Klinikum** Developer")
    st.markdown("✅ **OTH Regensburg** Student")
    
    # API Key Input (only visible if Secret is missing)
    if not api_key:
        st.markdown("---")
        api_key = st.text_input("Enter Groq API Key to chat", type="password")
    else:
        st.markdown("---")
        st.success("🤖 AI Engine: Online")

# --- 5. MAIN INTERFACE ---
st.title("🤖 Chat with Nico's Digital Twin")
st.write("I am Nico's personal AI representative. Ask me anything about his professional journey, technical expertise, or current projects.")

# Initializing Chat History with the "Agent Persona"
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

# Display Chat Messages
for message in st.session_state.messages:
    if message["role"] != "system":
        avatar = "🧑‍💻" if message["role"] == "user" else "🤖"
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])

# --- 6. CHAT LOGIC ---
if api_key:
    try:
        client = Groq(api_key=api_key)
        
        if prompt := st.chat_input("Ask me about Nico's experience or skills..."):
            # Add User Message
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user", avatar="🧑‍💻"):
                st.markdown(prompt)

            # Generate Agent Response
            with st.chat_message("assistant", avatar="🤖"):
                response_placeholder = st.empty()
                full_response = ""
                
                completion = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
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

# --- 7. SUGGESTION FOOTER ---
st.markdown("---")
st.caption("Try asking: 'What was Nico's impact at BMW?' or 'What are his core technical skills?'")
