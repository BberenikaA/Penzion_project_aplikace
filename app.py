import streamlit as st
from streamlit_gsheets import GSheetsConnection
import datetime
import requests
import re
import config

st.set_page_config(page_title="Penzion pod Špičákem")

st.markdown("""
    <div style='text-align: center; margin-bottom: -15px;'>
        <span style='font-size: 40px;'>🏨</span>
    </div>
    <h1 style='text-align: center; line-height: 1.1; margin-top: 0;'>
        Rezervační systém<br>Penzion pod Špičákem
    </h1>
""", unsafe_allow_html=True)

st.write("")

conn = st.connection("gsheets", type=GSheetsConnection)

with st.form("rezervace_form"):
    jmeno = st.text_input("Jméno a příjmení")
    email = st.text_input("Email")
    telefon = st.text_input("Telefon")

    col1, col2 = st.columns(2)
    with col1:
        osob = st.number_input("Počet osob", min_value=12, max_value=22, value=12)
        prijezd = st.date_input(
            "Datum příjezdu",
            min_value=datetime.date.today(),
            format="DD.MM.YYYY"
        )
    with col2:
        noci = st.number_input("Počet nocí", min_value=2, value=2)
        vip = st.checkbox("Mám věrnostní kartu")

    submit = st.form_submit_button("Odeslat rezervaci")

if submit:
    if not jmeno or not email or not telefon:
        st.error("⚠️ Prosím, vyplňte všechna povinná pole (Jméno, Email a Telefon).")
    elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        st.error("⚠️ Zadejte prosím platný email.")
    elif not telefon.isdigit() or len(telefon) < 9:
        st.error("⚠️ Telefon musí obsahovat pouze číslice a mít alespoň 9 znaků.")
    else:
        odjezd = prijezd + datetime.timedelta(days=noci)
        cena_za_noc = osob * 450
        if cena_za_noc > 8000:
            cena_za_noc = 8000
        celkova_cena = cena_za_noc * noci
        if vip:
            celkova_cena *= 0.9

        url = config.script_url

        params = {
            "datum": datetime.datetime.now().strftime("%d.%m.%Y %H:%M"),
            "jmeno": jmeno,
            "email": email,
            "telefon": telefon,
            "osob": osob,
            "prijezd": prijezd.strftime("%d.%m.%Y"),
            "noci": noci,
            "vip": "ANO" if vip else "NE",
            "odjezd": odjezd.strftime("%d.%m.%Y"),
            "cena": f"{int(celkova_cena)} Kč"
        }

        try:
            response = requests.get(url, params=params)
            if response.status_code == 200:
                st.success(f"✅ Rezervace úspěšně odeslána pro: {jmeno}. Celková cena: {int(celkova_cena)} Kč")
                st.balloons()

                st.markdown("""
                    <a href="/" target="_self" style="text-decoration: none;">
                        <div style="background-color: #ff4b4b; color: white; padding: 10px 20px; 
                                    border-radius: 5px; text-align: center; width: 220px; cursor: pointer;
                                    margin-top: 15px; font-weight: bold;">
                            Zadat další rezervaci
                        </div>
                    </a>
                """, unsafe_allow_html=True)
            else:
                st.error("Chyba při komunikaci se serverem.")
        except Exception as e:
            st.error(f"Došlo k chybě: {e}")