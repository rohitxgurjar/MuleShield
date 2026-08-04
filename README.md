# 🛡️ MuleShield

**AI-driven step-up authentication to stop mule account fraud in digital payments.**

Mule accounts let scammers launder stolen money by routing it through accounts they don't own — because today's authentication (PIN, OTP) only proves someone *knows* a secret, not that the real account holder is present. MuleShield closes that gap.

## How it works

1. **Risk scoring** — a Random Forest model, trained on 6M+ real transaction records, scores every transaction for mule-fraud patterns (specifically: sudden account drainage and near-100% balance transfers).
2. **Tiered authentication** — low-risk transactions pass with a PIN, medium-risk gets an OTP challenge, and high-risk transactions trigger live face verification — so security scales with risk instead of annoying every user.
3. **Live face verification** — high-risk transactions activate the device camera and require a real, present face before approving the transfer, using OpenCV face detection.

## Tech stack

Python, scikit-learn, pandas, OpenCV, Streamlit

## Run it locally

```bash
pip install -r requirements.txt
streamlit run muleshield_app.py
```

## Team / Track

Built solo for Smart India Hackathon 2026 — Blockchain & Cybersecurity theme.
