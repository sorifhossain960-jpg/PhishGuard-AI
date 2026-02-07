import streamlit as st
import pandas as pd
import google.generativeai as genai
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline

# ---------------------------------------------------------
# 1. API KEY SECURITY (নিরাপদ পদ্ধতি)
# ---------------------------------------------------------
# GitHub-এ Key থাকবে না, এটি Streamlit Cloud-এর সেটিংস থেকে আসবে
GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]

st.set_page_config(page_title="PhishGuard AI", page_icon="🛡️")

# 2. AI Setup
try:
    genai.configure(api_key=GOOGLE_API_KEY)
    gemini_model = genai.GenerativeModel('gemini-1.5-flash')
    gemini_status = "✅ Online"
except:
    gemini_model = None
    gemini_status = "❌ Offline"

# 3. Local Engine
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("phishing.csv", low_memory=False)
        df = df.rename(columns={"URL": "url", "Label": "label"})
        df['label'] = df['label'].map({'bad': 'Phishing', 'good': 'Safe'})
        return df.dropna()
    except:
        return pd.DataFrame({'url': ['google.com'], 'label': ['Safe']})

data = load_data()
local_model = make_pipeline(CountVectorizer(), MultinomialNB())
local_model.fit(data['url'], data['label'])

# 4. UI
st.title("🛡️ PhishGuard AI Security")
url_input = st.text_input("🔗 Paste link here:")

if st.button("SCAN"):
    if url_input:
        local_result = local_model.predict([url_input])[0]
        with st.spinner("AI Investigating..."):
            try:
                prompt = f"Analyze URL: '{url_input}'. Reply in 1 short sentence starting with 'VERDICT: SAFE' or 'VERDICT: PHISHING'."
                response = gemini_model.generate_content(prompt)
                gemini_reply = response.text
            except:
                gemini_reply = "AI Busy"
        
        if "VERDICT: SAFE" in gemini_reply.upper():
            st.success("✅ SAFE")
        else:
            st.error("🚫 PHISHING DETECTED")
        st.info(f"💡 AI Opinion: {gemini_reply}")