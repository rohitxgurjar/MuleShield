import streamlit as st
import pandas as pd
import numpy as np
import joblib
import cv2

st.set_page_config(
    page_title="MuleShield",
    page_icon="🛡️"
)

st.title("🛡️ MuleShield")
st.caption("AI-powered mule account fraud prevention")

model = joblib.load("muleshield_model.pkl")


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


def check_face_verification(img_file):
    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades +
        "haarcascade_frontalface_default.xml"
    )

    bytes_data = img_file.getvalue()

    frame = cv2.imdecode(
        np.frombuffer(bytes_data, np.uint8),
        cv2.IMREAD_COLOR
    )

    if frame is None:
        return False, None, []

    gray = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2GRAY
    )

    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.05,
        minNeighbors=3,
        minSize=(30, 30)
    )

    return len(faces) > 0, frame, faces


st.subheader("Enter Transaction Details")

amount = st.number_input(
    "Transaction Amount (₹)",
    min_value=0.0,
    value=500.0,
    step=100.0
)

oldbalance = st.number_input(
    "Account Balance Before (₹)",
    min_value=0.0,
    value=50000.0,
    step=100.0
)

newbalance = oldbalance - amount

st.metric(
    "Account Balance After (₹)",
    f"₹{newbalance:,.2f}"
)


if st.button(
    "🔍 Evaluate Transaction",
    type="primary"
):

    if amount > oldbalance:
        st.error(
            "❌ Transaction rejected: transaction amount "
            "is greater than the available account balance."
        )
        st.stop()

    if oldbalance > 0 and newbalance <= 0.01 * oldbalance:
        orig_emptied = 1
    else:
        orig_emptied = 0

    if oldbalance > 0:
        drain_ratio = amount / oldbalance
    else:
        drain_ratio = 0

    drainage_risk = drain_ratio >= 0.90

    ratio = amount / (oldbalance + 1)

    input_data = pd.DataFrame([
        {
            "amount": amount,
            "oldbalanceOrg": oldbalance,
            "newbalanceOrig": newbalance,
            "orig_emptied": orig_emptied,
            "amount_to_balance_ratio": ratio
        }
    ])

    probability = model.predict_proba(
        input_data
    )[0][1]

    tier = get_risk_tier(probability)

    auth = get_auth_requirement(tier)

    face_required = (
        tier == "HIGH"
        or drainage_risk
        or orig_emptied == 1
    )

    col1, col2 = st.columns(2)

    col1.metric(
        "Fraud Probability",
        f"{probability:.1%}"
    )

    col2.metric(
        "Risk Tier",
        tier
    )

    st.write(
        f"**Balance Drainage:** {drain_ratio:.1%}"
    )

    if orig_emptied == 1:
        st.warning(
            "⚠️ Account is nearly empty after this transaction."
        )

    if drainage_risk:
        st.warning(
            "⚠️ Suspicious balance drainage detected."
        )

        st.info(
            "90% or more of the available balance is "
            "being transferred. Additional verification "
            "is required."
        )

    if face_required:
        st.error(
            "🔐 FACE VERIFICATION REQUIRED"
        )

        st.info(
            "Additional identity verification is required "
            "before the transaction can be completed."
        )
    else:
        st.info(
            f"**Authentication required:** {auth}"
        )

    st.session_state["tier"] = tier
    st.session_state["auth"] = auth
    st.session_state["drainage_risk"] = drainage_risk
    st.session_state["orig_emptied"] = orig_emptied
    st.session_state["face_required"] = face_required
    st.session_state["transaction_checked"] = True


if (
    st.session_state.get("transaction_checked", False)
    and
    st.session_state.get("face_required", False)
):

    if st.session_state.get("tier") == "HIGH":
        st.warning(
            "⚠️ High risk transaction detected — "
            "face verification required."
        )

    elif st.session_state.get("orig_emptied", False):
        st.warning(
            "⚠️ Account nearly emptied — "
            "face verification required."
        )

    else:
        st.warning(
            "⚠️ Large balance drainage detected — "
            "face verification required."
        )

    img_file = st.camera_input(
        "Look at the camera for verification"
    )

    if img_file is not None:

        with st.spinner(
            "Checking captured photo for a face..."
        ):

            verified, frame, faces = (
                check_face_verification(img_file)
            )

        if frame is None:
            st.error(
                "❌ Could not process the captured image."
            )
            st.stop()

        frame_rgb = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )

        for x, y, w, h in faces:
            cv2.rectangle(
                frame_rgb,
                (x, y),
                (x + w, y + h),
                (0, 255, 0),
                3
            )

        st.image(
            frame_rgb,
            caption="Captured photo",
            width=400
        )

        if verified:
            st.success(
                "✅ Face detected successfully."
            )

            st.success(
                "✅ Additional verification passed."
            )

            st.success(
                "✅ Transaction ALLOWED"
            )

        else:
            st.error(
                "🚫 No face detected."
            )

            st.error(
                "🚫 Additional verification failed."
            )

            st.error(
                "🚫 Transaction BLOCKED"
            )


elif (
    st.session_state.get("transaction_checked", False)
    and
    st.session_state.get("tier") in ("LOW", "MEDIUM")
):

    if not st.session_state.get(
        "drainage_risk",
        False
    ) and not st.session_state.get(
        "orig_emptied",
        False
    ):
        st.success(
            f"✅ Transaction ALLOWED "
            f"({st.session_state.get('auth')})"
        )









































