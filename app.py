import streamlit as st
import pandas as pd
import google.generativeai as genai
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline
import datetime

# --- Configuration ---
st.set_page_config(page_title="PhishGuard AI", page_icon="🛡️", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f4f7f6; }
    .stButton>button {
        width: 100%; border-radius: 10px; background: linear-gradient(135deg, #e63946, #d62828);
        color: white; font-weight: bold; height: 3.5rem; border: none;
    }
    .footer {
        position: fixed; left: 0; bottom: 0; width: 100%; background-color: white;
        color: #333; text-align: center; padding: 10px; font-size: 14px; border-top: 1px solid #eee;
    }
    </style>
    """, unsafe_allow_html=True)

# --- AI & Model Setup ---
try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=API_KEY)
    model_names = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    gemini_model = genai.GenerativeModel(model_names[0] if model_names else "gemini-1.5-flash")
    status = "Active"
except:
    gemini_model = None
    status = "Maintenance"

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

# --- Sidebar (Developer Profile) ---
with st.sidebar:
    # তোমার ছবির বদলে একটি প্রফেশনাল সিকিউরিটি আইকন
    st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=120)
    st.title("PhishGuard Panel")
    st.write(f"**Security Status:** {status}")
    st.divider()
    
    st.markdown("### Developer")
    st.write("**Sorif Hossain**")
    st.caption("Computer Science Student")
    st.write("📧 [Email Me](mailto:codehackwithsorif@gmail.com)")
    
    st.markdown("### Connect & Follow")
    st.write("💼 [LinkedIn Profile](https://www.linkedin.com/in/sorif-hossain-24b946337)")
    st.write("📱 [WhatsApp Channel](https://whatsapp.com/channel/0029VbBJa7iIt5rtVuNzfP2g)")
    st.write("🎥 [YouTube Channel](https://www.youtube.com/channel/UCmGne4ahuFAAfD4sYP9nLDw)")

# --- Main UI ---
st.title("🛡️ PhishGuard AI Security")
st.write("Detecting digital threats using Machine Learning and Generative AI.")

url_input = st.text_input("Enter URL to scan:", placeholder="https://login-verify-account.tk")

if st.button("RUN SECURITY SCAN"):
    if url_input:
        prediction = local_engine.predict([url_input])[0]
        with st.spinner("AI Analysis in progress..."):
            try:
                prompt = f"Analyze URL: '{url_input}'. Verdict (Safe/Phishing) + 1-sentence expert reason."
                ai_reply = gemini_model.generate_content(prompt).text
            except:
                ai_reply = "AI Analysis is currently unavailable."

        st.subheader("Security Analysis Report")
        col1, col2 = st.columns(2)
        col1.metric("Database Verdict", prediction)
        col2.write("**AI Deep Insights:**")
        col2.write(ai_reply)

        if "PHISHING" in ai_reply.upper() or prediction == "Phishing":
            st.error("🚨 DANGEROUS LINK DETECTED!")
            st.snow()
        else:
            st.success("✅ THIS LINK IS SAFE")
            st.balloons()
    else:
        st.warning("Please provide a valid URL.")

# --- Footer ---
year = datetime.datetime.now().year
st.markdown(f"""
    <div class="footer">
        © {year} <b>PhishGuard AI</b> | Developed by <b>Sorif Hossain</b> | All Rights Reserved.
    </div>
    """, unsafe_allow_html=True)
