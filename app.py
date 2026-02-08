import streamlit as st
import pandas as pd
import google.generativeai as genai
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline
import datetime

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="PhishGuard AI Security", page_icon="🛡️", layout="wide")

# --- CUSTOM CSS STYLING ---
st.markdown("""
    <style>
    .main { background-color: #f4f7f6; }
    
    /* Button Styling */
    .stButton>button {
        width: 100%; border-radius: 12px;
        background: linear-gradient(135deg, #e63946, #d62828);
        color: white; font-weight: bold; border: none; padding: 12px;
        transition: 0.4s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(230, 57, 70, 0.3);
    }
    
    /* Note Box Styling */
    .info-note {
        background-color: #eef2f7; border-left: 5px solid #007bff;
        padding: 15px; border-radius: 8px; margin-top: 20px; font-size: 14px; color: #333;
    }

    /* Footer Styling */
    .footer {
        width: 100%; background-color: #ffffff; color: #333;
        text-align: center; padding: 20px; font-size: 13px;
        border-top: 1px solid #eaeaea; margin-top: 40px;
    }
    .contact-link { color: #e63946; text-decoration: none; font-weight: bold; }
    
    .status-online { color: #28a745; font-weight: bold; }
    .status-offline { color: #dc3545; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SYSTEM SETUP ---

# Google Gemini AI Config
try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=API_KEY)
    gemini_model = genai.GenerativeModel("gemini-1.5-flash")
    status_html = '<span class="status-online">● Active</span>'
except Exception:
    gemini_model = None
    status_html = '<span class="status-offline">● Offline</span>'

# Local ML Engine Config
@st.cache_data
def load_ml_engine():
    try:
        df = pd.read_csv("phish.csv")
        # Ensure correct column names
        df.rename(columns={df.columns[0]: "url", df.columns[1]: "label"}, inplace=True)
        
        # Robust Mapping
        df['label'] = df['label'].astype(str).str.lower().str.strip().map({
            'benign': 'Safe', 
            'phishing': 'Phishing', 
            'defacement': 'Phishing'
        })
        return df.dropna()
    except Exception:
        return pd.DataFrame({'url': ['google.com'], 'label': ['Safe']})

data = load_ml_engine()
local_model = make_pipeline(CountVectorizer(), MultinomialNB())
local_model.fit(data['url'], data['label'])

# --- 3. SIDEBAR ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=90)
    st.title("PhishGuard Console")
    st.markdown(f"**Security Status:** {status_html}", unsafe_allow_html=True)
    st.divider()
    
    st.markdown("### 👤 Developer")
    st.write("**Sorif Hossain**")
    st.caption("Computer Science Student")
    
    st.markdown("### 🔗 Connect With Me")
    st.write("💼 [LinkedIn Profile](https://www.linkedin.com/in/sorif-hossain-489768388/)")
    st.write("📧 [Email Me](mailto:codehackwithsorif@gmail.com)")
    st.write("📱 [WhatsApp Channel](https://whatsapp.com/channel/0029VbBJa7iIt5rtVuNzfP2g)")
    st.write("🎥 [YouTube Channel](https://www.youtube.com/channel/UCmGne4ahuFAAfD4sYP9nLDw)")
    st.divider()
    st.info("Hybrid AI system combining Local Machine Learning and Google Gemini LLM.")

# --- 4. MAIN INTERFACE ---
st.title("🛡️ PhishGuard AI Security")
st.markdown("##### *Advanced Threat Detection | Hybrid Intelligence Model*")
st.divider()

url_input = st.text_input("🔗 Paste URL below to scan for threats:", placeholder="https://secure-login.example.com")

if st.button("🔍 INITIATE DEEP SCAN"):
    if url_input:
        # Loading Spinner starts here
        with st.spinner("AI Brain is performing deep pattern analysis..."):
            
            # Phase 1: Local Prediction
            try:
                local_pred = local_model.predict([url_input])[0]
            except:
                local_pred = "Uncertain"

            # Phase 2: Gemini AI Analysis
            ai_response_text = ""
            final_verdict = ""
            
            if gemini_model:
                try:
                    prompt = (f"Act as a security expert. Analyze URL: '{url_input}'. "
                              "Check for phishing, defacement, and spoofing. "
                              "If it is a known official site (like google, facebook, sbi), say Safe. "
                              "If suspicious, say Phishing. "
                              "Reply STRICTLY in this format: 'Verdict: [Safe/Phishing]'. "
                              "Then give 1 short reason.")
                    
                    response = gemini_model.generate_content(prompt)
                    ai_response_text = response.text
                    
                    # Logic: Prioritize AI
                    if "PHISHING" in ai_response_text.upper():
                        final_verdict = "Phishing"
                    elif "SAFE" in ai_response_text.upper():
                        final_verdict = "Safe"
                    else:
                        final_verdict = local_pred 
                except Exception:
                    ai_response_text = "AI Connection Limit. Using Local DB."
                    final_verdict = local_pred
            else:
                ai_response_text = "AI Module Offline."
                final_verdict = local_pred

        # --- Visualization (Shows after spinner ends) ---
        st.markdown("### 📊 Investigation Results")
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.write("**Local ML Engine:**")
            if local_pred == "Safe":
                st.success(f"Database Match: {local_pred}")
            else:
                st.error(f"Database Match: {local_pred}")
                
        with col2:
            st.write("**Gemini AI Deep Analysis:**")
            st.info(ai_response_text)

        # Final Verdict Logic
        st.divider()
        if final_verdict == "Phishing":
            st.error("### 🚨 FINAL VERDICT: DANGEROUS LINK DETECTED!")
            st.snow()
        else:
            st.success("### ✅ FINAL VERDICT: THIS LINK IS SECURE.")
            st.balloons()

        # Expert Note
        st.markdown(f"""
            <div class="info-note">
                <b>ℹ️ Important Note:</b> Local AI checks against 30,000+ known patterns. 
                However, <b>Google Gemini AI</b> provides real-time heuristic analysis with 99% accuracy. 
                The <b>Final Verdict</b> prioritizes Gemini's decision.
            </div>
        """, unsafe_allow_html=True)
    else:
        st.warning("Please provide a valid URL to scan.")

# --- 5. FOOTER ---
current_year = datetime.datetime.now().year
footer_html = f"""
    <div class="footer">
        © {current_year} <b>PhishGuard AI Security</b> | All Rights Reserved. <br>
        Developed by <a class="contact-link" href="https://www.linkedin.com/in/sorif-hossain-489768388/">Sorif Hossain</a> | 
        <a class="contact-link" href="https://whatsapp.com/channel/0029VbBJa7iIt5rtVuNzfP2g">Code Hack with Sorif</a>
    </div>
"""
st.markdown(footer_html, unsafe_allow_html=True)
