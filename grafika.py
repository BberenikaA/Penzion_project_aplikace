import datetime
import requests
import streamlit as st


class Host:

    def __init__(self, jmeno_prijmeni, email, telefon):
        self.jmeno_prijmeni = jmeno_prijmeni
        self.email = email
        self.telefon = telefon


class Rezervace:

    def __init__(
        self, host, pocet_osob, pocet_noci, datum_prijezdu, datum_odjezdu
    ):
        self.host = host
        self.pocet_osob = pocet_osob
        self.pocet_noci = pocet_noci
        self.datum_prijezdu = datum_prijezdu
        self.datum_odjezdu = datum_odjezdu
        self.datum_vytvoreni = datetime.datetime.now().strftime(
            "%d.%m.%Y %H:%M"
        )

    def vypocti_celkovou_cenu(self):
        cena_za_noc = self.pocet_osob * 450
        if cena_za_noc > 8000:
            cena_za_noc = 8000
        return cena_za_noc * self.pocet_noci

    def uloz_do_souboru(self):
        celkova_cena = self.vypocti_celkovou_cenu()
        zapis_hosta = (
            f"{self.datum_vytvoreni}: {self.host.jmeno_prijmeni} ({self.host.email}), ({self.host.telefon}) - "
            f"TERMÍN: {self.datum_prijezdu} až {self.datum_odjezdu} , "
            f"{self.pocet_osob} osob, {self.pocet_noci} nocí, "
            f"Cena: {celkova_cena} Kč\n"
        )
        try:
            with open("rezervace.txt", "a", encoding="utf-8") as soubor:
                soubor.write(zapis_hosta)
            return True
        except IOError:
            return False


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

        url = "https://api.open-meteo.com/v1/forecast?latitude=50.7383&longitude=15.3082&current_weather=true"
        odpoved = requests.get(url).json()
        teplota = odpoved["current_weather"]["temperature"]

        return (
            f"{sezona} (aktuálně v Tanvaldu {teplota}°C). Doporučujeme: {tipy}."
        )
    except:
        return "Informace o počasí a aktivitách nejsou dostupné."


st.title("Penzion pod Špičákem (Tanvald)")

vstup_jmeno = st.text_input("Jméno a příjmení hosta")
vstup_email = st.text_input("Email hosta")
vstup_telefon = st.text_input("Telefon (pouze číslice)")
vstup_osob = st.number_input(
    "Počet osob (12-22)", min_value=12, max_value=22, value=12
)
vstup_noci = st.number_input(
    "Počet nocí (min. 2)", min_value=2, value=2
)
vstup_datum = st.text_input("Datum příjezdu (např. 15.01.2026)")

if st.button("Vytvořit rezervaci"):

    if "@" not in vstup_email or "." not in vstup_email:
        st.error("❌ Chyba: Email musí obsahovat zavináč (@) a tečku (.)")
    elif not vstup_telefon.isdigit():
        st.error("❌ Chyba: Telefon nesmí obsahovat písmena ani mezery.")
    elif not (12 <= vstup_osob <= 22):
        st.error("❌ Chyba: Počet osob musí být mezi 12 a 22.")
    elif vstup_noci < 2:
        st.error("❌ Chyba: Minimální délka pobytu jsou 2 noci.")
    else:
        try:
            prijezd_dt = datetime.datetime.strptime(vstup_datum, "%d.%m.%Y")
            odjezd_dt = prijezd_dt + datetime.timedelta(days=vstup_noci)
            odjezd_str = odjezd_dt.strftime("%d.%m.%Y")

            novy_host = Host(vstup_jmeno, vstup_email, vstup_telefon)
            nova_rezervace = Rezervace(
                novy_host, vstup_osob, vstup_noci, vstup_datum, odjezd_str
            )

            celkova_cena = nova_rezervace.vypocti_celkovou_cenu()
            soubor_ok = nova_rezervace.uloz_do_souboru()
            pocasí_info = ziskej_info_o_pobytu(vstup_datum)

            st.success("✅ Rezervace byla úspěšně zpracována!")
            st.write(f"**REZERVAČNÍ SYSTÉM PRO:** {novy_host.jmeno_prijmeni}")
            st.write(f"**TERMÍN:** {vstup_datum} - {odjezd_str}")
            st.write(f"**CELKOVÁ CENA:** {celkova_cena} Kč")
            st.write(f"**INFO K TERMÍNU:** {pocasí_info}")

            if not soubor_ok:
                st.warning("⚠️ Chyba: Nepodařilo se zapsat do souboru.")

        except ValueError:
            st.error("❌ Chyba: Špatný formát data. Zadejte např. 15.01.2026")
