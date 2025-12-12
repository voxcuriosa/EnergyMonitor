import streamlit as st
import os
import google_auth_oauthlib.flow
from googleapiclient.discovery import build

class GoogleAuth:
    def __init__(self):
        # Hent secrets
        try:
            self.client_config = st.secrets["google_auth"]
        except KeyError:
            st.error("Mangler Google Auth konfigurasjon i secrets.toml")
            st.stop()
            
        self.scopes = [
            "openid",
            "https://www.googleapis.com/auth/userinfo.email", 
            "https://www.googleapis.com/auth/userinfo.profile"
        ]

    def get_flow(self):
        """Oppretter en auth flow instance."""
        # For å tillate http lokalt (viktig for testing)
        if "localhost" in st.query_params: # En enkel sjekk, men os env er bedre
             os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
        
        # Bestem redirect URI basert på hvor vi kjører
        # Dette er litt "hacky" i Streamlit, men fungerer ofte
        # Alternativt må brukeren hardkode redirect_uri i secrets
        
        redirect_uri = self.client_config.get("redirect_uri")
        if not redirect_uri:
            # Fallback guessing if not specified
            redirect_uri = "http://localhost:8501" 
        
        flow = google_auth_oauthlib.flow.Flow.from_client_config(
            self.client_config,
            scopes=self.scopes,
            redirect_uri=redirect_uri 
        )
        return flow

    def check_auth(self, allowed_emails=None):
        """Sjekker om bruker er logget inn, og håndterer login flow."""
        
        # 1. Er bruker allerede logget inn i session?
        if "google_auth_user" in st.session_state:
            user = st.session_state["google_auth_user"]
            if allowed_emails and user["email"] not in allowed_emails:
                st.error(f"Beklager, e-posten {user['email']} har ikke tilgang til denne appen.")
                if st.button("Logg ut"):
                    st.session_state.pop("google_auth_user")
                    st.rerun()
                st.stop()
            return user

        # 2. Kommer bruker tilbake fra Google Auth (har code i URL)?
        if "code" in st.query_params:
            try:
                code = st.query_params["code"]
                flow = self.get_flow()
                flow.fetch_token(code=code)
                credentials = flow.credentials
                
                # Hent brukerinfo
                service = build('oauth2', 'v2', credentials=credentials)
                user_info = service.userinfo().get().execute()
                
                st.session_state["google_auth_user"] = user_info
                
                # Rens URL
                st.query_params.clear() 
                st.rerun()
                
            except Exception as e:
                st.error(f"Feil under innlogging: {e}")
                st.write("Prøv å laste siden på nytt.")
                st.stop()
                
        # 3. Ikke logget inn - vis Login knapp
        flow = self.get_flow()
        auth_url, _ = flow.authorization_url(prompt='consent')
        
        st.markdown(f"""
            <div style="display: flex; justify-content: center; margin-top: 50px;">
                <a href="{auth_url}" target="_self" style="
                    background-color: #4285F4; 
                    color: white; 
                    padding: 12px 24px; 
                    text-decoration: none; 
                    border-radius: 4px; 
                    font-family: sans-serif; 
                    font-weight: bold;">
                    Logg inn med Google
                </a>
            </div>
        """, unsafe_allow_html=True)
        st.stop() # Stopp videre kjøring til vi er logget inn
