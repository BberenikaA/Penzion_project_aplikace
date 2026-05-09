import streamlit as st
from streamlit_gsheets import GSheetsConnection
import datetime
import pandas as pd

st.set_page_config(page_title="Penzion pod Špičákem")
st.header("🏨 Rezervační systém pro Penzion pod Špičákem")

conn = st.connection("gsheets", type=GSheetsConnection)

with st.form("rezervace_form"):
    jmeno = st.text_input("Jméno a příjmení")
    email = st.text_input("Email")
    telefon = st.text_input("Telefon")

    col1, col2 = st.columns(2)
    with col1:
        osob = st.number_input("Počet osob", min_value=12, max_value=22, value=12)
        prijezd = st.date_input("Datum příjezdu", min_value=datetime.date.today())
    with col2:
        noci = st.number_input("Počet nocí", min_value=2, value=2)
        vip = st.checkbox("Mám věrnostní kartu")

    submit = st.form_submit_button("Odeslat rezervaci")

if submit:
    odjezd = prijezd + datetime.timedelta(days=noci)
    cena_za_noc = osob * 450
    if cena_za_noc > 8000:
        cena_za_noc = 8000
    celkova_cena = cena_za_noc * noci
    if vip:
        celkova_cena *= 0.9

    nova_data = pd.DataFrame([{
        "Datum vytvoření": datetime.datetime.now().strftime("%d.%m.%Y %H:%M"),
        "Jméno": jmeno,
        "Email": email,
        "Telefon": telefon,
        "Příjezd": prijezd.strftime("%d.%m.%Y"),
        "Odjezd": odjezd.strftime("%d.%m.%Y"),
        "Osob": osob,
        "Nocí": noci,
        "Cena": f"{int(celkova_cena)} Kč"
    }])

    try:
        stavajici_data = conn.read()
        aktualizovana_data = pd.concat([stavajici_data, nova_data], ignore_index=True)
        conn.update(data=aktualizovana_data)

        st.success(f"✅ Rezervace potvrzena. Cena: {int(celkova_cena)} Kč")
        st.balloons()
    except Exception as e:
        st.error(f"Chyba: {e}")
