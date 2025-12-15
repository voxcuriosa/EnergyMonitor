import streamlit as st
import google_auth_oauthlib.flow
from googleapiclient.discovery import build
import os

# CONSTANTS
# Scopes defines what we want to access. 
# "openid" is required for authentication.
# "userinfo.email" lets us check who you are.
SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile"
]

def get_google_auth_config():
    """
    Henter secrets og forbereder dem for Google-biblioteket.
    """
    try:
        # Hent rad fra secrets
        client_config = st.secrets["google"]
        
        # Konverter til standard dictionary for å unngå immutability-problemer
        config = dict(client_config)
        
        # Sjekk at vi har de viktigste feltene
        required_keys = ["client_id", "client_secret", "redirect_uri"]
        missing = [key for key in required_keys if key not in config]
        
        if missing:
            st.error(f"Mangler følgende nøkler i [.streamlit/secrets.toml] under [google]: {missing}")
            st.stop()

        # Google biblioteket krever at 'auth_uri' og 'token_uri' finnes. 
        # Vi legger dem til manuelt hvis de mangler.
        if "auth_uri" not in config:
            config["auth_uri"] = "https://accounts.google.com/o/oauth2/auth"
        if "token_uri" not in config:
            config["token_uri"] = "https://oauth2.googleapis.com/token"

        # Biblioteket forventer strukturen {"web": { ... }}
        return {"web": config}

    except Exception as e:
        st.error(f"Kunne ikke laste Google-konfigurasjon: {e}")
        st.stop()


def authenticate_user():
    """
    Hovedfunksjon for å håndtere innlogging.
    Returnerer brukerinfo (dict) hvis innlogget, ellers None (og stopper scriptet).
    """
    
    # 1. SJEKK OM VI ALLEREDE ER INNLOGGET I SESSION STATE
    if "user_info" in st.session_state:
        return st.session_state["user_info"]

    # Hent konfigurasjon
    client_config = get_google_auth_config()
    redirect_uri = client_config["web"]["redirect_uri"].rstrip("/")

    # 2. LAG FLOW-OBJEKTET
    # Dette objektet styrer hele dansen med Google.
    try:
        flow = google_auth_oauthlib.flow.Flow.from_client_config(
            client_config,
            scopes=SCOPES,
            redirect_uri=redirect_uri
        )
    except Exception as e:
        st.error(f"Feil ved oppsett av Google Auth Flow: {e}")
        st.stop()

    # 3. SJEKK OM VI KOMMER TILBAKE FRA GOOGLE MED EN CODE
    # Når Google sender brukeren tilbake, legger de til ?code=... i URL-en
    if "code" in st.query_params:
        try:
            code = st.query_params["code"]
            
            # Bytt koden mot tokens
            flow.fetch_token(code=code)
            credentials = flow.credentials

            # VERIFISERING: Hent info om hvem dette er
            # Vi bruker 'people' API da dette er mer robust enn oauth2 v2
            service = build('people', 'v1', credentials=credentials)
            person = service.people().get(
                resourceName='people/me', 
                personFields='names,emailAddresses'
            ).execute()

            # Hent ut e-post og navn
            email = person.get('emailAddresses', [])[0]['value']
            name = person.get('names', [])[0].get('displayName', 'Ukjent')

            # Lagre i session state
            user_data = {"email": email, "name": name}
            st.session_state["user_info"] = user_data

            # Rydd opp URL-en (fjern ?code=...) slik at ved refresh så logger vi ikke inn på nytt
            st.query_params.clear()
            st.rerun()

        except Exception as e:
            st.error(f"Noe gikk galt under innloggingen: {e}")
            st.markdown("Trykk på knappen under for å prøve på nytt.")
            if st.button("Prøv igjen"):
                st.query_params.clear()
                st.rerun()
            st.stop()

    # 4. HVIS IKKE INNLOGGET: VIS LOGIN-KNAPP
    else:
        # Generer login-URL
        auth_url, _ = flow.authorization_url(
            prompt='consent',
            access_type='offline',
            include_granted_scopes='true'
        )

        st.markdown(f"""
            <style>
            .login-btn {{
                background-color: #4285F4;
                color: white;
                padding: 15px 32px;
                text-align: center;
                text-decoration: none;
                display: inline-block;
                font-size: 16px;
                margin: 4px 2px;
                cursor: pointer;
                border-radius: 8px;
                border: none;
                font-family: 'Roboto', sans-serif;
                font-weight: 500;
                box-shadow: 0 2px 4px 0 rgba(0,0,0,0.2);
            }}
            .login-btn:hover {{
                box-shadow: 0 4px 8px 0 rgba(0,0,0,0.2);
                background-color: #357ae8;
            }}
            .container {{
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                height: 50vh;
            }}
            </style>
            <div class="container">
                <h1>⚡ Energy Monitor</h1>
                <p>Du må logge inn for å se strømdata.</p>
                <a href="{auth_url}" target="_blank">
                    <button class="login-btn">
                        Logg inn med Google
                    </button>
                </a>
            </div>
        """, unsafe_allow_html=True)
        
        # DEBUG INFO (Kun synlig hvis man åpner den)
        with st.expander("🛠️ Debug Info (Klikk her hvis innlogging feiler)"):
            st.write(f"**Client ID som brukes:** `{client_config['web'].get('client_id')}`")
            st.write(f"**Redirect URI som brukes:** `{redirect_uri}`")
            st.warning("Sjekk at disse stemmer NØYAKTIG med det som står i Google Cloud Console.")
            st.info("Tips: Pass på at det ikke er noen mellomrom før eller etter ID-ene i secrets.toml")
        
        # Stopp resten av appen fra å kjøre
        st.stop()
