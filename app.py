import streamlit as st
import datetime
import requests
import re
import config


def zkontroluj_obsazenost_online():
    try:
        url = st.secrets["moje_tajne_odkazy"]["url_obsazenost"]
        odpoved = requests.get(url, timeout=5)
        if odpoved.status_code == 200:
            return "✅ OK (Synchronizace s e-chalupy.cz je aktivní)"
        return "❌ Problém s připojením k e-chalupy"
    except:
        return "🌐 Služba obsazenosti nedostupná"


def ziskej_info_o_pobytu(datum_prijezdu_str):
    try:
        prijezd_dt = datetime.datetime.strptime(datum_prijezdu_str, "%d.%m.%Y")
        mesic = prijezd_dt.month
        if mesic in [12, 1, 2]:
            sezona, tipy = "ZIMA ❄️", "lyže (Špičák), brusle a běžky"
        elif mesic in [6, 7, 8]:
            sezona, tipy = "LÉTO ☀️", "kolo, koupání v bazéně, v Jizeře"
        elif mesic in [3, 4, 5]:
            sezona, tipy = "JARO 🌱", "procházky a cykloturistika"
        else:
            sezona, tipy = "PODZIM 🍂", "houbaření a výšlapy"
        url_pocasi = st.secrets["moje_tajne_odkazy"]["api_pocasi"]
        odpoved = requests.get(url_pocasi, timeout=5).json()
        teplota = odpoved['current_weather']['temperature']
        return f"{sezona} (aktuálně v Tanvaldu {teplota}°C). Doporučujeme: {tipy}."
    except:
        return "Tanvald je krásný v každém počasí.😉"


st.set_page_config(page_title="Penzion pod Špičákem")

st.markdown("""
    <div style='text-align: center; margin-bottom: -15px;'>
        <span style='font-size: 40px;'>🏨</span>
    </div>
    <h1 style='text-align: center; line-height: 1.1; margin-top: 0;'>
        Rezervační systém<br>Penzion pod Špičákem
    </h1>
""", unsafe_allow_html=True)

if 'success' not in st.session_state:
    st.session_state.success = False

if st.session_state.success:
    st.success(f"✅ Rezervace potvrzena pro: {st.session_state.last_jmeno}!")
    st.info(f"💰 Celková cena: {st.session_state.last_cena} Kč")
    st.write(f"📊 {zkontroluj_obsazenost_online()}")
    st.write(f"🌦️ {ziskej_info_o_pobytu(st.session_state.last_prijezd)}")
    st.balloons()
    if st.button("Zadat další rezervaci"):
        st.session_state.success = False
        st.rerun()
else:
    with st.form("rezervace_form", clear_on_submit=False):
        jmeno = st.text_input("Jméno a příjmení")
        email = st.text_input("Email")
        telefon = st.text_input("Telefon")
        col1, col2 = st.columns(2)
        with col1:
            osob = st.number_input("Počet osob", config.MIN_KAPACITA, config.MAX_KAPACITA, config.MIN_KAPACITA)
            prijezd = st.date_input("Datum příjezdu", min_value=datetime.date.today(), format="DD.MM.YYYY")
        with col2:
            noci = st.number_input("Počet nocí", min_value=config.MIN_NOCI, value=config.MIN_NOCI)
            is_vip = st.checkbox("Mám věrnostní kartu")
            cislo_karty = st.text_input("Číslo karty (pokud máte)")
        submit = st.form_submit_button("Odeslat rezervaci")

    if submit:
        email_vzor = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        if not jmeno or not re.match(email_vzor, email):
            st.error("⚠️ Vyplňte prosím správně jméno a email.")
        else:
            cena_za_noc = min(osob * config.CENA_ZA_OSOBU_NOC, config.MAX_CENA_ZA_OBJEKT_NOC)
            celkova_cena = int(cena_za_noc * noci * (0.9 if is_vip else 1.0))
            prijezd_str = prijezd.strftime("%d.%m.%Y")
            odjezd_str = (prijezd + datetime.timedelta(days=noci)).strftime("%d.%m.%Y")
            vytvoreno = datetime.datetime.now().strftime("%d.%m.%Y %H:%M")

            # TADY JE TA OPRAVA: Názvy klíčů musí odpovídat tvému Apps Scriptu
            params = {
                "datum": vytvoreno,
                "jmeno": jmeno,
                "email": email,
                "telefon": telefon,
                "osob": osob,
                "prijezd": prijezd_str,
                "noci": noci,
                "vip": "ANO" if is_vip else "NE",
                "odjezd": odjezd_str,
                "cena": f"{celkova_cena} Kč"
            }

            try:
                url_tabulka = st.secrets["script_url"]
                # allow_redirects=True je klíčové pro Google Scripty
                res = requests.get(url_tabulka, params=params, timeout=15, allow_redirects=True)

                if res.status_code == 200:
                    st.session_state.last_jmeno = jmeno
                    st.session_state.last_cena = celkova_cena
                    st.session_state.last_prijezd = prijezd_str
                    st.session_state.success = True
                    st.rerun()
                else:
                    st.error(f"❌ Tabulka vrátila chybu {res.status_code}")
            except Exception as e:
                st.error(f"❌ Chyba spojení: {e}")




