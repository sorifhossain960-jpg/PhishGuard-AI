import streamlit as st
import pandas as pd
import google.generativeai as genai
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline
import datetime

# ---------------------------------------------------------
# 1. PAGE CONFIG & PREMIUM DESIGN
# ---------------------------------------------------------
st.set_page_config(page_title="PhishGuard AI Security", page_icon="🛡️", layout="wide")

# প্রফেশনাল সিএসএস ডিজাইন
st.markdown("""
    <style>
    .main { background-color: #f4f7f6; }
    .stButton>button {
        width: 100%;
        border-radius: 12px;
        background: linear-gradient(135deg, #e63946, #d62828);
        color: white;
        font-weight: bold;
        border: none;
        height: 3.5rem;
        transition: 0.4s ease;
    }
    .stButton>button:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 20px rgba(230, 57, 70, 0.4);
    }
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: #ffffff;
        color: #333;
        text-align: center;
        padding: 15px;
        font-size: 14px;
        border-top: 1px solid #eaeaea;
        z-index: 100;
    }
    .contact-link { color: #e63946; text-decoration: none; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. AI SETUP WITH SECRETS
# ---------------------------------------------------------
try:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=GOOGLE_API_KEY)
    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    active_model_name = available_models[0] if available_models else "gemini-1.5-flash"
    gemini_model = genai.GenerativeModel(active_model_name)
    gemini_status = "✅ AI Core Active"
except Exception:
    gemini_model = None
    gemini_status = "⚠️ AI Offline (Check Config)"

# ---------------------------------------------------------
# 3. ML ENGINE (Phishing Database)
# ---------------------------------------------------------
@st.cache_data
def load_engine():
    try:
        df = pd.read_csv("phishing.csv")
        df = df.rename(columns={"URL": "url", "Label": "label"})
        df['label'] = df['label'].map({'bad': 'Phishing', 'good': 'Safe'})
        return df.dropna()
    except:
        return pd.DataFrame({'url': ['google.com'], 'label': ['Safe']})

data = load_engine()
local_model = make_pipeline(CountVectorizer(), MultinomialNB())
local_model.fit(data['url'], data['label'])

# ---------------------------------------------------------
# 4. MAIN INTERFACE
# ---------------------------------------------------------
st.title("🛡️ PhishGuard AI Security")
st.markdown("##### *Advanced Anti-Phishing System | Powered by Gemini AI*")
st.divider()

# সাইডবার সেটিংস
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=90)
    st.header("System Console")
    st.markdown(f"**Status:** {gemini_status}")
    st.markdown("---")
    
    st.markdown("### 👤 Developer Info")
    st.write("**Sorif Hossain**")
    st.caption("Computer Science Student")
    st.write(f"📧 [Email Us](mailto:codehackwithsorif@gmail.com)")
    
    st.markdown("### 🔗 Social Links")
    st.write(f"📱 [WhatsApp Channel](https://whatsapp.com/channel/0029VbBJa7iIt5rtVuNzfP2g)")
    st.write(f"🎥 [YouTube Channel](https://www.youtube.com/channel/UCmGne4ahuFAAfD4sYP9nLDw)")
    st.markdown("---")
    st.info("Protecting your digital identity with Artificial Intelligence.")

# স্ক্যান ইনপুট
col_main, _ = st.columns([2, 1])
with col_main:
    url_input = st.text_input("🔗 Paste URL to scan for threats:", placeholder="https://login-verify-account.tk")
    
    if st.button("🔍 INITIATE DEEP SCAN"):
        if url_input:
            local_prediction = local_model.predict([url_input])[0]
            with st.spinner("Analyzing URL structure and AI patterns..."):
                try:
                    prompt = f"Analyze URL: '{url_input}'. Verdict (Safe/Phishing) + 1-sentence expert reason."
                    response = gemini_model.generate_content(prompt)
                    ai_verdict = response.text
                except:
                    ai_verdict = "AI analysis encountered a network timeout."

            st.markdown("### 📑 Security Report")
            c1, c2 = st.columns(2)
            with c1:
                st.metric("Database Scan", local_prediction)
            with c2:
                st.write("**AI Deep Learning Analysis:**")
                st.write(ai_verdict)

            # ফাইনাল রেজাল্ট লজিক
            if "PHISHING" in ai_verdict.upper() or local_prediction == "Phishing":
                st.error("### 🚨 VERDICT: DANGEROUS LINK DETECTED!")
                st.snow()
            else:
                st.success("### ✅ VERDICT: THIS LINK LOOKS SAFE")
                st.balloons()
        else:
            st.warning("Please provide a link to scan.")

# ---------------------------------------------------------
# 5. PROFESSIONAL FOOTER (All Rights Reserved)
# ---------------------------------------------------------
current_year = datetime.datetime.now().year
footer_html = f"""
    <div class="footer">
        © {current_year} <b>PhishGuard AI Security</b> | All Rights Reserved. <br>
        Developed by <a class="contact-link" href="mailto:codehackwithsorif@gmail.com">Sorif Hossain</a> | 
        <a class="contact-link" href="https://whatsapp.com/channel/0029VbBJa7iIt5rtVuNzfP2g">Code Hack with Sorif</a>
    </div>
"""
st.markdown(footer_html, unsafe_allow_html=True)
