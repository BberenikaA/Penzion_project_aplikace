import streamlit as st
import datetime
import requests
import re
import config


def zapis_do_google_tabulky(data_dict):
    try:
        url = st.secrets["script_url"]
        response = requests.get(url, params=data_dict, timeout=10)
        return response.status_code == 200
    except:
        return False


def ziskej_info():
    try:
        url_pocasi = st.secrets["moje_tajne_odkazy"]["api_pocasi"]
        res = requests.get(url_pocasi).json()
        teplota = res['current_weather']['temperature']
        return f"Aktuálně je v Tanvaldu {teplota}°C."
    except:
        return "Vítejte v Penzionu pod Špičákem!"


st.set_page_config(page_title="Penzion pod Špičákem")
st.title("Rezervační systém")

if 'success' not in st.session_state:
    st.session_state.success = False

if not st.session_state.success:
    with st.form("rezervace_form"):
        jmeno = st.text_input("Jméno a příjmení")
        email = st.text_input("Email")
        telefon = st.text_input("Telefon")
        osob = st.number_input("Počet osob", config.MIN_KAPACITA, config.MAX_KAPACITA)
        prijezd = st.date_input("Datum příjezdu", min_value=datetime.date.today())
        noci = st.number_input("Počet nocí", min_value=config.MIN_NOCI)
        is_vip = st.checkbox("Mám věrnostní kartu")

        submit = st.form_submit_button("Odeslat rezervaci")

    if submit:
        if not jmeno or not email or "@" not in email:
            st.error("⚠️ Prosím vyplňte jméno a platný email.")
        elif not telefon.isdigit() or len(telefon) < 9:
            st.error("⚠️ Zadejte platný telefonní kontakt (pouze číslice).")
        else:
            cena_za_noc = min(osob * config.CENA_ZA_OSOBU_NOC, config.MAX_CENA_ZA_OBJEKT_NOC)
            celkova_cena = int(cena_za_noc * noci * (0.9 if is_vip else 1.0))

            prijezd_str = prijezd.strftime("%d.%m.%Y")
            odjezd_str = (prijezd + datetime.timedelta(days=noci)).strftime("%d.%m.%Y")

            data_pro_tabulku = {
                "datum": datetime.datetime.now().strftime("%d.%m.%Y %H:%M"),
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

            if zapis_do_google_tabulky(data_pro_tabulku):
                st.session_state.success = True
                st.session_state.vysledek = {"jmeno": jmeno, "cena": celkova_cena}
                st.rerun()
            else:
                st.error("❌ Nepodařilo se zapsat do tabulky. Zkontrolujte script_url v Secrets.")

else:
    st.success(f"✅ Rezervace pro {st.session_state.vysledek['jmeno']} byla úspěšně uložena!")
    st.info(f"💰 Celková cena: {st.session_state.vysledek['cena']} Kč")
    st.write(ziskej_info())
    st.balloons()

    if st.button("Zadat novou rezervaci"):
        st.session_state.success = False
        st.rerun()

