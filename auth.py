import streamlit as st
import time

def check_pin(pin_input):
    """
    Sjekker om oppgitt PIN stemmer med secrets.
    """
    try:
        secret_pin = str(st.secrets["auth"]["pin"])
        if pin_input == secret_pin:
            return True
    except KeyError:
        st.error("Mangler PIN-konfigurasjon i secrets.toml. Legg til [auth] pin = '...'")
        st.stop()
    return False

def authenticate_user():
    """
    Hovedfunksjon for å håndtere innlogging med PIN.
    Returnerer en dummy brukerinfo (dict) hvis innlogget, ellers stopper scriptet og ber om PIN.
    """
    
    # 1. SJEKK OM VI ALLEREDE ER INNLOGGET I SESSION STATE
    if st.session_state.get("authenticated", False):
        return {"name": "Admin", "email": "admin@energymonitor"}

    # 2. HVIS IKKE INNLOGGET: VIS LOGIN-SKJERM
    st.markdown("""
        <style>
        .login-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 40vh;
            text-align: center;
        }
        </style>
        <div class="login-container">
            <h1>⚡ Energy Monitor</h1>
            <p>Skriv inn PIN-kode for å få tilgang til strømdata.</p>
        </div>
    """, unsafe_allow_html=True)

    # Bruk kolonner for å sentrere input-feltet
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        with st.form("login_form"):
            pin_input = st.text_input("PIN-kode", type="password", help="Skriv inn din hemmelige kode")
            submit_button = st.form_submit_button("Lås opp", use_container_width=True)
            
            if submit_button:
                if check_pin(pin_input):
                    st.session_state["authenticated"] = True
                    st.success("Innlogging vellykket! Laster data...")
                    time.sleep(0.5)
                    st.rerun()
                else:
                    st.error("Feil PIN-kode. Prøv igjen.")

    # Stopp resten av appen inntil vi er logget inn
    st.stop()
