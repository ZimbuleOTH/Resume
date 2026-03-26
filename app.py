import streamlit as st
from groq import Groq

# --- 1. PAGE CONFIG & STYLING ---
st.set_page_config(
    page_title="Nico Stengel - AI Twin", 
    page_icon="🤖", 
    layout="centered"
)

# Custom CSS for a professional look
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stChatMessage {
        border-radius: 12px;
        border: 1px solid #e0e0e0;
    }
    /* Style for the sidebar contact info */
    .contact-info {
        font-size: 0.9rem;
        color: #555;
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
# Check if key is in Streamlit Cloud Secrets, otherwise look for an input
api_key = st.secrets.get("GROQ_API_KEY")

# --- 4. SIDEBAR (INFO & OPTIONAL KEY) ---
with st.sidebar:
    st.title("👤 Candidate Profile")
    st.markdown(f"""
    **Nico Stengel** *AI & Data Science Student* ---
    **Contact:**
    - 📧 [nico-stengel@outlook.de](mailto:nico-stengel@outlook.de)
    - 📞 +49 15151700704
    - 📍 Regensburg, Germany
    
    ---
    **Quick Facts:**
    - 🏎️ **Ex-BMW** Software Engineer
    - 🎓 **OTH Regensburg** (AI & DS)
    - 🏥 **LMU Klinikum** Developer
    """)
    
    # Show input field ONLY if Secret is missing
    if not api_key:
        st.markdown("---")
        api_key = st.text_input("Enter Groq API Key to Chat", type="password")
        st.info("To automate this, add 'GROQ_API_KEY' to Streamlit Secrets.")
    else:
        st.success("✅ AI Engine Connected")

# --- 5. MAIN INTERFACE ---
st.title("🤖 Talk to Nico's Digital Twin")
st.write("Hello! I am Nico's AI assistant. Ask me anything about his career at BMW, his studies in AI, or his technical skills.")

# Initializing Chat History
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system", 
            "content": f"""
            You are the professional AI Twin of Nico Stengel. 
            CONTEXT DATA FROM NICO'S CV:
            {my_resume_data}
            
            YOUR RULES:
            1. IDENTITY: You represent Nico Stengel. Speak professionally and helpfully.
            2. LANGUAGE: Always respond in ENGLISH.
            3. KNOWLEDGE: Use ONLY the provided context. If a detail is missing, provide his email for direct contact.
            4. HIGHLIGHTS: Focus on his transition from a BMW apprenticeship to a Software Engineer and now an AI student.
            5. LIMITS: Do not make up facts or discuss non-professional topics.
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
        
        if prompt := st.chat_input("Ask me about Nico's experience..."):
            # Add User Message
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user", avatar="🧑‍💻"):
                st.markdown(prompt)

            # Generate Assistant Response
            with st.chat_message("assistant", avatar="🤖"):
                response_placeholder = st.empty()
                full_response = ""
                
                # Using the latest Llama 3.1 model
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
        st.error(f"An error occurred: {e}")
else:
    st.warning("Please provide an API Key to start the conversation.")

# Suggestion Chips (Buttons to help the user start)
st.markdown("---")
st.write("Suggested questions:")
col1, col2 = st.columns(2)
if col1.button("Nico's time at BMW?"):
    st.info("Type: 'Tell me about your work at BMW.'")
if col2.button("Technical Skills?"):
    st.info("Type: 'What programming languages do you know?'")
