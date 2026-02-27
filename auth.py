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

    # BRUTE FORCE PROTECTION
    MAX_ATTEMPTS = 5
    LOCKOUT_TIME_SECONDS = 300 # 5 minutter

    if "login_attempts" not in st.session_state:
        st.session_state["login_attempts"] = 0
    if "lockout_time" not in st.session_state:
        st.session_state["lockout_time"] = 0

    # Sjekk om brukeren er låst ute
    current_time = time.time()
    if st.session_state["login_attempts"] >= MAX_ATTEMPTS:
        time_left = st.session_state["lockout_time"] - current_time
        if time_left > 0:
            st.error(f"For mange forsøk. Prøv igjen om {int(time_left)} sekunder.")
            st.stop()
        else:
            # Tiden er ute, nullstill forsøk
            st.session_state["login_attempts"] = 0

    # Bruk kolonner for å sentrere input-feltet
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        with st.form("login_form"):
            pin_input = st.text_input("PIN-kode", type="password", help="Skriv inn din hemmelige kode")
            submit_button = st.form_submit_button("Lås opp", use_container_width=True)
            
            if submit_button:
                if check_pin(pin_input):
                    st.session_state["authenticated"] = True
                    st.session_state["login_attempts"] = 0 # Nullstill ved suksess
                    st.success("Innlogging vellykket! Laster data...")
                    time.sleep(0.5)
                    st.rerun()
                else:
                    st.session_state["login_attempts"] += 1
                    attempts_left = MAX_ATTEMPTS - st.session_state["login_attempts"]
                    
                    if attempts_left <= 0:
                        st.session_state["lockout_time"] = time.time() + LOCKOUT_TIME_SECONDS
                        st.error("For mange feilforsøk. Du er låst ute i 5 minutter.")
                        time.sleep(1) # Liten forsinkelse for å straffe bots
                        st.rerun()
                    else:
                        st.error(f"Feil PIN-kode. Du har {attempts_left} forsøk igjen.")
                        time.sleep(0.5) # Liten forsinkelse for å straffe bots

    # Stopp resten av appen inntil vi er logget inn
    st.stop()
