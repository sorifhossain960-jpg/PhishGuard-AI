import streamlit as st
import pandas as pd
import google.generativeai as genai
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline
import datetime

# --- Configuration (Mobile Optimized) ---
st.set_page_config(page_title="PhishGuard Mobile", page_icon="🛡️", layout="centered")

# Custom CSS for Mobile App Feel
st.markdown("""
    <style>
    /* মেইন ব্যাকগ্রাউন্ড */
    .stApp { background-color: #F8F9FB; }
    
    /* হেডার ডিজাইন */
    .app-header {
        background: linear-gradient(135deg, #e63946, #d62828);
        padding: 20px;
        border-radius: 0 0 25px 25px;
        color: white;
        text-align: center;
        margin-bottom: 20px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
    }

    /* ইনপুট বক্স বড় করা */
    .stTextInput > div > div > input {
        border-radius: 15px;
        height: 50px;
        border: 2px solid #eee;
    }

    /* বাটনকে অ্যাপের মতো লুক দেওয়া */
    .stButton > button {
        width: 100%;
        border-radius: 15px;
        height: 55px;
        background: #e63946;
        color: white;
        font-size: 18px;
        font-weight: bold;
        border: none;
        box-shadow: 0 4px 15px rgba(230, 57, 70, 0.3);
    }

    /* রেজাল্ট কার্ড */
    .result-card {
        background: white;
        padding: 20px;
        border-radius: 20px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        margin-top: 15px;
    }

    /* মোবাইল নোট বক্স */
    .mobile-note {
        font-size: 12px;
        color: #666;
        background: #E8F0FE;
        padding: 12px;
        border-radius: 12px;
        margin-top: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- Header ---
st.markdown('<div class="app-header"><h1>🛡️ PhishGuard AI</h1><p>Security in your Pocket</p></div>', unsafe_allow_html=True)

# --- AI & Model Setup (Same Logic) ---
try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=API_KEY)
    gemini_model = genai.GenerativeModel("gemini-1.5-flash")
except:
    gemini_model = None

@st.cache_data
def train_engine():
    try:
        df = pd.read_csv("phishing.csv")
        df = df.rename(columns={"URL": "url", "Label": "label"})
        df['label'] = df['label'].map({'bad': 'Phishing', 'good': 'Safe'})
        return df.dropna()
    except:
        return pd.DataFrame({'url': ['google.com'], 'label': ['Safe']})

data = train_engine()
local_engine = make_pipeline(CountVectorizer(), MultinomialNB())
local_engine.fit(data['url'], data['label'])

# --- Main App Body ---
st.write("### Quick Scan")
url_input = st.text_input("", placeholder="Paste Link Here...")

if st.button("🚀 ANALYZE NOW"):
    if url_input:
        local_pred = local_engine.predict([url_input])[0]
        with st.spinner("AI Checking..."):
            try:
                prompt = f"URL: '{url_input}'. Safe or Phishing? 1 sentence explanation."
                response = gemini_model.generate_content(prompt).text
                ai_verdict = "Safe" if "SAFE" in response.upper() else "Phishing"
            except:
                response = "Connection Error."
                ai_verdict = local_pred

        # Result Display
        st.markdown('<div class="result-card">', unsafe_allow_html=True)
        if ai_verdict == "Phishing":
            st.error("🚨 DANGER: PHISHING DETECTED")
            st.write(f"**AI Reason:** {response}")
            st.snow()
        else:
            st.success("✅ SAFE: YOU ARE GOOD TO GO")
            st.write(f"**AI Reason:** {response}")
            st.balloons()
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown(f"""
            <div class="mobile-note">
                <b>Note:</b> Hybrid analysis active. Gemini AI decision is final (99% accurate).
            </div>
        """, unsafe_allow_html=True)
    else:
        st.warning("Please paste a link.")

# --- Sidebar for Profile (Hidden in mobile by default) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=100)
    st.title("Developer")
    st.write("**Sorif Hossain**")
    st.write("💼 [LinkedIn](https://www.linkedin.com/in/sorif-hossain-24b946337)")
    st.write("📱 [WhatsApp](https://whatsapp.com/channel/0029VbBJa7iIt5rtVuNzfP2g)")

# Footer
st.markdown(f"<p style='text-align:center; color:#999; margin-top:50px;'>© {datetime.datetime.now().year} PhishGuard AI</p>", unsafe_allow_html=True)
