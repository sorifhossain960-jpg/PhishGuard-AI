import streamlit as st
import pandas as pd
import google.generativeai as genai
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline
import datetime

# --- Configuration ---
st.set_page_config(page_title="PhishGuard AI", page_icon="🛡️", layout="wide")

# CSS for styling
st.markdown("""
    <style>
    .main { background-color: #f4f7f6; }
    .stButton>button {
        width: 100%; border-radius: 10px; background: linear-gradient(135deg, #e63946, #d62828);
        color: white; font-weight: bold; height: 3.5rem; border: none;
    }
    .status-active {
        color: #008000; font-weight: bold; font-size: 1.1rem;
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
    # স্ট্যাটাস টেক্সট সবুজ করার জন্য HTML ব্যবহার
    status_html = '<span class="status-active">● Active</span>'
except:
    gemini_model = None
    status_html = '<span style="color:red; font-weight:bold;">● Maintenance</span>'

@st.cache_data
def train_engine():
    try:
        # লোকাল ইঞ্জিনকে শক্তিশালী করতে আমরা ডেটাবেস লোড করছি
        df = pd.read_csv("phishing.csv")
        df = df.rename(columns={"URL": "url", "Label": "label"})
        df['label'] = df['label'].map({'bad': 'Phishing', 'good': 'Safe'})
        return df.dropna()
    except:
        # যদি ফাইল কাজ না করে, তবে হ্যাকাথনের জন্য কিছু কমন প্যাটার্ন এখানে দেওয়া হলো
        return pd.DataFrame({
            'url': ['google.com', 'facebook.com', 'paypal-security.com', 'login-verify.tk', 'secure-update.net'],
            'label': ['Safe', 'Safe', 'Phishing', 'Phishing', 'Phishing']
        })

data = train_engine()
local_engine = make_pipeline(CountVectorizer(), MultinomialNB())
local_engine.fit(data['url'], data['label'])

# --- Sidebar ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=120)
    st.title("PhishGuard Panel")
    # স্ট্যাটাস সবুজ রঙে দেখাচ্ছে
    st.markdown(f"**Security Status:** {status_html}", unsafe_allow_html=True)
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
st.write("Real-time threat detection powered by Hybrid Machine Learning.")



url_input = st.text_input("Enter URL to scan:", placeholder="https://verify-your-bank-account.com")

if st.button("RUN SECURITY SCAN"):
    if url_input:
        # লোকাল ইঞ্জিনের প্রেডিকশন
        prediction = local_engine.predict([url_input])[0]
        
        with st.spinner("AI Brain is analyzing URL structure..."):
            try:
                # এআই-কে আরও নিখুঁতভাবে বিশ্লেষণ করতে বলা হয়েছে
                prompt = (f"Act as a cybersecurity expert. Analyze this URL: '{url_input}'. "
                          "Is it Safe or Phishing? Answer with 'Verdict: [Safe/Phishing]' and "
                          "provide one technical reason (like suspicious TLD, domain spoofing, or abnormal characters).")
                ai_reply = gemini_model.generate_content(prompt).text
            except:
                ai_reply = "Deep Analysis currently unavailable."

        st.subheader("Security Analysis Report")
        col1, col2 = st.columns(2)
        
        # লোকাল রেজাল্ট ডিজাইন
        with col1:
            st.write("**Local Engine Scan:**")
            if prediction == "Safe":
                st.success(f"Database Result: {prediction}")
            else:
                st.error(f"Database Result: {prediction}")
        
        with col2:
            st.write("**AI Deep Insights:**")
            st.info(ai_reply)

        # ফাইনাল লজিক (হ্যাকাথনের জন্য আরও নিখুঁত করা হয়েছে)
        if "PHISHING" in ai_reply.upper() or prediction == "Phishing":
            st.error("🚨 ALERT: THIS LINK IS IDENTIFIED AS A THREAT!")
            st.snow()
        else:
            st.success("✅ VERDICT: THE LINK APPEARS TO BE SECURE.")
            st.balloons()
    else:
        st.warning("Please enter a valid URL.")

# --- Footer ---
year = datetime.datetime.now().year
st.markdown(f"""
    <div class="footer">
        © {year} <b>PhishGuard AI</b> | Developed by <b>Sorif Hossain</b> | All Rights Reserved.
    </div>
    """, unsafe_allow_html=True)
