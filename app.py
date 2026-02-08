import streamlit as st
import pandas as pd
import google.generativeai as genai
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline
import datetime

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="PhishGuard AI Security", page_icon="🛡️", layout="wide")

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    .main { background-color: #f4f7f6; }
    .stButton>button {
        width: 100%; border-radius: 12px; background: linear-gradient(135deg, #e63946, #d62828);
        color: white; font-weight: bold; border: none; padding: 12px;
    }
    .info-note {
        background-color: #eef2f7; border-left: 5px solid #007bff;
        padding: 15px; border-radius: 8px; margin-top: 20px; font-size: 14px;
    }
    .status-online { color: #28a745; font-weight: bold; }
    .status-offline { color: #dc3545; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SETUP ---
try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=API_KEY)
    gemini_model = genai.GenerativeModel("gemini-1.5-flash")
    status_html = '<span class="status-online">● Active</span>'
except Exception as e:
    gemini_model = None
    status_html = f'<span class="status-offline">● Offline ({str(e)})</span>'

@st.cache_data
def load_ml_engine():
    try:
        df = pd.read_csv("phish.csv")
        df.rename(columns={df.columns[0]: "url", df.columns[1]: "label"}, inplace=True)
        df['label'] = df['label'].astype(str).str.lower().str.strip().map({
            'benign': 'Safe', 'phishing': 'Phishing', 'defacement': 'Phishing'
        })
        return df.dropna()
    except:
        return pd.DataFrame({'url': ['google.com'], 'label': ['Safe']})

data = load_ml_engine()
local_model = make_pipeline(CountVectorizer(), MultinomialNB())
local_model.fit(data['url'], data['label'])

# --- 3. SIDEBAR ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=90)
    st.title("PhishGuard Console")
    st.markdown(f"**Status:** {status_html}", unsafe_allow_html=True)
    st.info("Hybrid AI System Active")

# --- 4. MAIN UI ---
st.title("🛡️ PhishGuard AI Security")
url_input = st.text_input("🔗 Paste URL below:", placeholder="https://example.com")

if st.button("🔍 INITIATE DEEP SCAN"):
    if url_input:
        with st.spinner("AI Brain is performing deep pattern analysis..."):
            # Phase 1: Local
            try:
                local_pred = local_model.predict([url_input])[0]
            except:
                local_pred = "Uncertain"

            # Phase 2: Gemini (DEBUG MODE)
            ai_response_text = ""
            final_verdict = ""
            
            if gemini_model:
                try:
                    prompt = (f"Act as a security expert. Analyze URL: '{url_input}'. "
                              "Check for phishing. Reply STRICTLY: 'Verdict: [Safe/Phishing]'. Reason.")
                    
                    response = gemini_model.generate_content(prompt)
                    ai_response_text = response.text
                    
                    if "PHISHING" in ai_response_text.upper():
                        final_verdict = "Phishing"
                    elif "SAFE" in ai_response_text.upper():
                        final_verdict = "Safe"
                    else:
                        final_verdict = local_pred 
                except Exception as e:
                    # --- এই লাইনটি এখন আসল এরর দেখাবে ---
                    ai_response_text = f"🛑 REAL ERROR: {str(e)}"
                    final_verdict = local_pred
            else:
                ai_response_text = "AI Module Offline (Check Secrets)."
                final_verdict = local_pred

        # Result
        st.markdown("### 📊 Results")
        c1, c2 = st.columns(2)
        with c1:
            st.write("**Local ML:**")
            st.success(local_pred) if local_pred == "Safe" else st.error(local_pred)
        with c2:
            st.write("**Gemini AI:**")
            st.info(ai_response_text)

        st.divider()
        if final_verdict == "Phishing":
            st.error("### 🚨 FINAL VERDICT: DANGEROUS LINK!")
        else:
            st.success("### ✅ FINAL VERDICT: SAFE LINK.")
            
    else:
        st.warning("Please enter a URL.")

# Footer
st.markdown(f"<div class='footer'>© {datetime.datetime.now().year} PhishGuard AI | Sorif Hossain</div>", unsafe_allow_html=True)
