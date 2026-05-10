import streamlit as st
import datetime
import requests
import re
import config


def zkontroluj_obsazenost_online():
    try:
        odpoved = requests.get(config.URL_OBSAZENOST, timeout=5)
        if odpoved.status_code == 200:
            return "✅ OK (Synchronizace s e-chalupy.cz je aktivní)"
        else:
            return f"❌ CHYBA (Server odpověděl kódem {odpoved.status_code})"
    except Exception:
        return "🌐 CHYBA (Nelze se připojit k internetu)"


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
            sezona, tipy = "PODZIM 🍂", "houbaření a podzimní výšlapy"

        odpoved = requests.get(config.API_WEATHER_URL, timeout=5).json()
        if 'current_weather' in odpoved:
            teplota = odpoved['current_weather']['temperature']
            return f"{sezona} (aktuálně v Tanvaldu {teplota}°C). Doporučujeme: {tipy}."
        return f"{sezona}. Doporučujeme: {tipy}."
    except Exception:
        return "Tanvald je krásný v každém počasí.😉"


class Host:
    def __init__(self, jmeno_prijmeni, email, telefon):
        self.jmeno_prijmeni = jmeno_prijmeni
        self.email = email
        self.telefon = telefon

    def ziskej_slevu(self):
        return 0


class Verny_host(Host):
    def __init__(self, jmeno_prijmeni, email, telefon, cislo_karty):
        super().__init__(jmeno_prijmeni, email, telefon)
        self.cislo_karty = cislo_karty

    def ziskej_slevu(self):
        return 0.10


class Rezervace:
    def __init__(self, host, pocet_osob, pocet_noci, datum_prijezdu, datum_odjezdu):
        self.host = host
        self.pocet_osob = pocet_osob
        self.pocet_noci = pocet_noci
        self.datum_prijezdu = datum_prijezdu
        self.datum_odjezdu = datum_odjezdu
        self.datum_vytvoreni = datetime.datetime.now().strftime("%d.%m.%Y %H:%M")

    def vypocti_celkovou_cenu(self):
        cena_za_noc = self.pocet_osob * config.CENA_ZA_OSOBU_NOC
        if cena_za_noc > config.MAX_CENA_ZA_OBJEKT_NOC:
            cena_za_noc = config.MAX_CENA_ZA_OBJEKT_NOC
        zakladni_cena = cena_za_noc * self.pocet_noci
        sleva = zakladni_cena * self.host.ziskej_slevu()
        return int(zakladni_cena - sleva)


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

with st.form("rezervace_form"):
    jmeno = st.text_input("Jméno a příjmení")
    email = st.text_input("Email")
    telefon = st.text_input("Telefon (pouze číslice)")

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
    if not jmeno or not email or not telefon:
        st.error("⚠️ Prosím, vyplňte všechna povinná pole (Jméno, Email a Telefon).")
    elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        st.error("⚠️ Zadejte prosím platný email.")
    elif not telefon.isdigit() or len(telefon) < 9:
        st.error("⚠️ Telefon musí obsahovat pouze číslice a mít alespoň 9 znaků.")
    else:
        if is_vip:
            host = Verny_host(jmeno, email, telefon, cislo_karty)
        else:
            host = Host(jmeno, email, telefon)

        prijezd_str = prijezd.strftime("%d.%m.%Y")
        odjezd_str = (prijezd + datetime.timedelta(days=noci)).strftime("%d.%m.%Y")

        rez = Rezervace(host, osob, noci, prijezd_str, odjezd_str)
        celkova_cena = rez.vypocti_celkovou_cenu()

        params = {
            "datum": rez.datum_vytvoreni,
            "jmeno": host.jmeno_prijmeni,
            "email": host.email,
            "telefon": host.telefon,
            "osob": rez.pocet_osob,
            "prijezd": rez.datum_prijezdu,
            "noci": rez.pocet_noci,
            "vip": "ANO" if is_vip else "NE",
            "odjezd": rez.datum_odjezdu,
            "cena": f"{celkova_cena} Kč"
        }

        try:
            res = requests.get(config.script_url, params=params)
            if res.status_code == 200:
                st.success(f"✅ Rezervace potvrzena pro: {host.jmeno_prijmeni}!")
                st.info(f"💰 Celková cena: {celkova_cena} Kč")
                st.info(f"📊 Stav obsazenosti: {zkontroluj_obsazenost_online()}")
                st.info(f"🌦️ Info k pobytu: {ziskej_info_o_pobytu(prijezd_str)}")
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
                st.error("Chyba při zápisu do tabulky.")
        except Exception as e:
            st.error(f"Došlo k chybě při odesílání: {e}")