import streamlit as st
import pandas as pd
import google.generativeai as genai
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline

# ---------------------------------------------------------
# 1. PAGE CONFIG & DESIGN (Hugging Face Style)
# ---------------------------------------------------------
st.set_page_config(page_title="PhishGuard AI", page_icon="🛡️", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        background-color: #ff4b4b;
        color: white;
        font-weight: bold;
        border: none;
    }
    .report-box {
        padding: 20px;
        border-radius: 12px;
        border-left: 5px solid #ff4b4b;
        background-color: white;
    }
    </style>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. SECRET API & AI SETUP
# ---------------------------------------------------------
# এখানে আমরা সরাসরি কি না লিখে Secrets ব্যবহার করছি
try:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=GOOGLE_API_KEY)
    
    # স্মার্ট মডেল ফাইন্ডার
    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    active_model_name = available_models[0] if available_models else "gemini-1.5-flash"
    gemini_model = genai.GenerativeModel(active_model_name)
    gemini_status = f"✅ AI System Online ({active_model_name.split('/')[-1]})"
except Exception as e:
    gemini_model = None
    gemini_status = "❌ AI Offline (Check Secrets)"

# ---------------------------------------------------------
# 3. ML ENGINE (CSV Data)
# ---------------------------------------------------------
@st.cache_data
def load_engine():
    try:
        df = pd.read_csv("phishing.csv")
        df = df.rename(columns={"URL": "url", "Label": "label"})
        df['label'] = df['label'].map({'bad': 'Phishing', 'good': 'Safe'})
        return df.dropna()
    except:
        # ব্যাকআপ ডেটা যদি CSV না পাওয়া যায়
        return pd.DataFrame({'url': ['google.com'], 'label': ['Safe']})

data = load_engine()
local_model = make_pipeline(CountVectorizer(), MultinomialNB())
local_model.fit(data['url'], data['label'])

# ---------------------------------------------------------
# 4. UI INTERFACE
# ---------------------------------------------------------
st.title("🛡️ PhishGuard AI Security")
st.write("Advanced Phishing Detection powered by Machine Learning & Gemini AI")

with st.sidebar:
    st.header("⚙️ System Control")
    st.markdown("---")
    if "✅" in gemini_status: st.success(gemini_status)
    else: st.error(gemini_status)
    st.markdown("---")
    st.write("Developer: **Sorif Hossain**")
    st.write("Channel: [Code Hack with Sorif](https://whatsapp.com/channel/your-link)") # তোমার লিঙ্ক এখানে দাও

# input Section
url_input = st.text_input("🔗 Paste the URL to investigate:", placeholder="https://example-site.com")

if st.button("🚀 START SCAN"):
    if url_input:
        # ১. লোকাল স্ক্যান
        local_prediction = local_model.predict([url_input])[0]
        
        # ২. এআই স্ক্যান
        with st.spinner("AI Brain is thinking..."):
            try:
                prompt = f"Analyze the URL '{url_input}'. Is it Phishing or Safe? Give a 1-sentence expert explanation."
                response = gemini_model.generate_content(prompt)
                ai_verdict = response.text
            except:
                ai_verdict = "AI analysis encountered an error."

        # রেজাল্ট দেখানো
        st.markdown("---")
        st.subheader("📊 Investigation Report")
        
        c1, c2 = st.columns(2)
        with c1:
            st.metric("Database Match", local_prediction)
        with c2:
            st.write("**AI Deep Analysis:**")
            st.write(ai_verdict)

        # ফাইনাল রেজাল্ট
        if "PHISHING" in ai_verdict.upper() or local_prediction == "Phishing":
            st.error("### 🚨 VERDICT: DANGEROUS LINK DETECTED!")
            st.snow()
        else:
            st.success("### ✅ VERDICT: THIS LINK LOOKS SAFE")
            st.balloons()
    else:
        st.warning("Please enter a URL first!")
