import streamlit as st
import google_auth_oauthlib.flow

st.title("🔐 Auth Debugger")

# 1. Test Secrets
st.subheader("1. Secrets Check")
try:
    google_secrets = st.secrets["google"]
    st.success("✅ Secrets found!")
    st.write(f"Client ID: `{google_secrets['client_id']}`")
    st.write(f"Redirect URI: `{google_secrets['redirect_uri']}`")
except Exception as e:
    st.error(f"❌ Secrets failed: {e}")

# 2. Test Flow Generation
st.subheader("2. Flow URL Test")
try:
    config = dict(google_secrets)
    if "auth_uri" not in config:
        config["auth_uri"] = "https://accounts.google.com/o/oauth2/auth"
    if "token_uri" not in config:
        config["token_uri"] = "https://oauth2.googleapis.com/token"

    flow = google_auth_oauthlib.flow.Flow.from_client_config(
        {"web": config},
        scopes=["openid", "https://www.googleapis.com/auth/userinfo.email"],
        redirect_uri=google_secrets['redirect_uri'].rstrip('/')
    )
    auth_url, _ = flow.authorization_url(prompt='consent')
    st.success("✅ Flow generated!")
    if st.button("Generate Link"):
        st.code(auth_url)
        st.link_button("Test Login Link", auth_url)
except Exception as e:
    st.error(f"❌ Flow failed: {e}")
