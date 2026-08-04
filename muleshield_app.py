import streamlit as st
import pandas as pd
import joblib
import cv2

st.set_page_config(page_title="MuleShield", page_icon="🛡️")

st.title("🛡️ MuleShield")
st.caption("AI-powered mule account fraud prevention")

model = joblib.load('muleshield_model.pkl')

def get_risk_tier(probability):
    if probability < 0.30:
        return "LOW"
    elif probability < 0.70:
        return "MEDIUM"
    else:
        return "HIGH"

def get_auth_requirement(tier):
    if tier == "LOW":
        return "PIN only"
    elif tier == "MEDIUM":
        return "PIN + OTP"
    else:
        return "PIN + Face Recognition"

def check_face_verification():
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    cap = cv2.VideoCapture(0)
    for i in range(10):
        ret, frame = cap.read()
    cap.release()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.05, minNeighbors=3, minSize=(30, 30))
    return len(faces) > 0, frame, faces

st.subheader("Enter Transaction Details")
amount = st.number_input("Transaction Amount (₹)", min_value=0, value=500, step=100)
oldbalance = st.number_input("Account Balance Before (₹)", min_value=0, value=50000, step=100)
newbalance = st.number_input("Account Balance After (₹)", min_value=0, value=49500, step=100)

if st.button("🔍 Evaluate Transaction", type="primary"):
    orig_emptied = 1 if (newbalance == 0 and oldbalance > 0) else 0
    ratio = amount / (oldbalance + 1)

    input_data = pd.DataFrame([{
        'amount': amount,
        'oldbalanceOrg': oldbalance,
        'newbalanceOrig': newbalance,
        'orig_emptied': orig_emptied,
        'amount_to_balance_ratio': ratio
    }])

    probability = model.predict_proba(input_data)[0][1]
    tier = get_risk_tier(probability)
    auth = get_auth_requirement(tier)

    col1, col2 = st.columns(2)
    col1.metric("Fraud Probability", f"{probability:.1%}")
    col2.metric("Risk Tier", tier)

    st.info(f"**Authentication required:** {auth}")

    if tier == "HIGH":
        st.warning("⚠️ High risk detected — verifying face...")
        with st.spinner("Checking webcam for live face..."):
            verified, frame, faces = check_face_verification()

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        for (x, y, w, h) in faces:
            cv2.rectangle(frame_rgb, (x, y), (x+w, y+h), (0, 255, 0), 3)
        st.image(frame_rgb, caption="Live camera check", width=400)

        if verified:
            st.success("✅ Face verified — Transaction ALLOWED")
        else:
            st.error("🚫 No face detected — Transaction BLOCKED")
    else:
        st.success(f"✅ Transaction ALLOWED ({auth})")
