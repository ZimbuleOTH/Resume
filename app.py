import streamlit as st
from groq import Groq
import os
import requests
import datetime
from supabase import create_client, Client

# --- SETUP & CONFIG ---
st.set_page_config(
    page_title="Nico Stengel - AI Twin", 
    page_icon="🤖", 
    layout="centered"
)

# Supabase Client initialisieren
@st.cache_resource
def init_supabase():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

supabase = init_supabase()

# --- STYLING ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stChatMessage {
        border-radius: 12px;
        border: 1px solid #e0e0e0;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
    }
    section[data-testid="stSidebar"] { background-color: #1e293b; color: white; }
    section[data-testid="stSidebar"] .stMarkdown { color: #f1f5f9; }
    [data-testid="stSidebar"] [data-testid="stImage"] {
        display: flex; justify-content: center; background-color: transparent;
    }
    </style>
    """, unsafe_allow_html=True)

# --- HELPER FUNCTIONS ---
def load_bio():
    try:
        with open("bio.txt", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "Error: bio.txt not found."

def log_to_supabase(prompt):
    """Speichert Query, Zeit und Ort permanent."""
    try:
        # Standort abrufen
        geo = requests.get('https://ipapi.co/json/', timeout=2).json()
        location = f"{geo.get('city', 'Unknown')}, {geo.get('country_name', '??')}"
        
        # In Supabase schreiben
        supabase.table("logs").insert({
            "location": location,
            "query": prompt
        }).execute()
    except Exception as e:
        print(f"Logging failed: {e}")

# --- DATA ---
my_resume_data = load_bio()
api_key = st.secrets.get("GROQ_API_KEY")

# --- SIDEBAR ---
with st.sidebar:
    bitmojie_url = "https://raw.githubusercontent.com/ZimbuleOTH/Resume/main/Bitmojie.png"
    st.image(bitmojie_url, width=150)

    st.title("Nico Stengel")
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
    
    st.markdown("---")
    admin_password = st.text_input("Admin Access", type="password", placeholder="Enter code")
    
    if admin_password and admin_password == st.secrets.get("ADMIN_PASSWORD"):
        st.success("Admin Mode Active")
        # Zeige die letzten 10 Logs aus Supabase an
        if st.button("🔄 Show Live Logs"):
            res = supabase.table("logs").select("*").order("created_at", desc=True).limit(10).execute()
            for log in res.data:
                st.caption(f"📍 {log['location']} | 📅 {log['created_at'][:16]}")
                st.text(log['query'])
                st.markdown("---")

# --- MAIN CHAT INTERFACE ---
st.title("🤖 Chat with Nico's Digital Twin")
st.write("I am Nico's personal AI representative. Ask me anything about his professional journey.")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system", 
            "content": f"""
            ROLE: You are the professional Digital Twin and exclusive representative of Nico Stengel. 
            CONTEXT: You know Nico's entire professional history: {my_resume_data}
            STYLE: Speak as Nico's agent. Use phrases like "Nico spent three years at BMW...". 
            Respond in the language the user uses. Be professional and concise.
            """
        }
    ]

# Nachrichten anzeigen
for message in st.session_state.messages:
    if message["role"] != "system":
        avatar = "🧑‍💻" if message["role"] == "user" else "🤖"
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])

# Chat Logik
if api_key:
    try:
        client = Groq(api_key=api_key)
        if prompt := st.chat_input("Ask me about Nico's experience..."):
            
            # --- LOGGING START ---
            log_to_supabase(prompt)
            # --- LOGGING END ---

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
    st.warning("Please provide a Groq API Key to start.")

st.markdown("---")
st.caption("Try asking: 'What was Nico's impact at BMW?'")
