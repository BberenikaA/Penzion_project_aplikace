import datetime
import requests
import config


def zkontroluj_obsazenost_online():
    try:
        odpoved = requests.get(config.URL_OBSAZENOST, timeout=5)
        if odpoved.status_code == 200:
            return "✅ OK (Synchronizace s e-chalupy.cz je aktivní)"
        else:
            return "❌ CHYBA (Server odpověděl kódem {odpoved.status_code})"
    except Exception:
        return "🌐 CHYBA (Nelze se připojit k internetu nebo chybí config.py)"


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
        if 'current_weather' in odpoved and 'temperature' in odpoved['current_weather']:
            teplota = odpoved['current_weather']['temperature']
            return f"{sezona} (aktuálně v Tanvaldu {teplota}°C). Doporučujeme: {tipy}."
        return f"{sezona} (Teplota momentálně nedostupná). Doporučujeme: {tipy}."
    except Exception:
        return "Informace o počasí nejsou dostupné, ale Tanvald je krásný v každém počasí.😉"


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

    def priprav_zapis(self):
        celkova_cena = self.vypocti_celkovou_cenu()
        typ_hosta = "Věrný host" if isinstance(self.host, Verny_host) else "Běžný host"

        return (
            f"{self.datum_vytvoreni}: {self.host.jmeno_prijmeni} ({self.host.email}), ({self.host.telefon}), {typ_hosta} - "
            f"TERMÍN: {self.datum_prijezdu} až {self.datum_odjezdu} , "
            f"{self.pocet_osob} osob, {self.pocet_noci} nocí, "
            f"Cena: {celkova_cena} Kč\n")


def spustit_system():
    while True:
        print("\n" + "-" * 45)
        print("=== Rezervační systém: Penzion pod Špičákem (Tanvald) ===")
        print("     (Pro ukončení programu napište 'konec')")
        print("\n" + "-" * 45)
        jmeno_prijmeni = input("Jméno a příjmení hosta: ")
        if jmeno_prijmeni.lower() == 'konec':
            print("Vypínám systém. Hezký den! 👋 ")
            break

        while True:
            email = input("Email hosta: ")
            if "@" in email and "." in email:
                break
            print("Chyba: Email musí obsahovat zavináč (@) a tečku (.)")

        while True:
            telefon = input("Telefon hosta (pouze číslice): ")
            if telefon.isdigit():
                break
            print("Chyba: Telefon nesmí obsahovat písmena ani mezery.")

        is_vip = input("Má host věrnostní kartu? (ano/ne): ").lower()
        if is_vip == 'ano':
            cislo_karty = input("Zadejte číslo karty: ")
            host = Verny_host(jmeno_prijmeni, email, telefon, cislo_karty)
        else:
            host = Host(jmeno_prijmeni, email, telefon)

        while True:
            try:
                osob = int(input(f"Počet osob ({config.MIN_KAPACITA}-{config.MAX_KAPACITA}): "))
                if config.MIN_KAPACITA <= osob <= config.MAX_KAPACITA:
                    break
                print(f"Chyba: Kapacita musí být mezi {config.MIN_KAPACITA} a {config.MAX_KAPACITA}.")
            except ValueError:
                print("Chyba: Zadávejte prosím pouze číselné údaje u počtu osob.")

        while True:
            try:
                noci = int(input(f"Počet nocí (min. {config.MIN_NOCI}): "))
                if noci >= config.MIN_NOCI:
                    break
                print(f"Chyba: Minimální délka pobytu jsou {config.MIN_NOCI} noci.")
            except ValueError:
                print("Chyba: Zadávejte prosím pouze číselné údaje u počtu nocí.")

        while True:
            try:
                prijezd_str = input("Zadejte datum příjezdu (např. 15.01.2026): ")
                prijezd_dt = datetime.datetime.strptime(prijezd_str, "%d.%m.%Y")
                break
            except ValueError:
                print("Chyba: Špatný formát data. Zadejte např. 15.01.2026")

        odjezd_str = (prijezd_dt + datetime.timedelta(days=noci)).strftime("%d.%m.%Y")

        rezervace = Rezervace(host, osob, noci, prijezd_str, odjezd_str)

        try:
            with open("rezervace.txt", "a", encoding="utf-8") as f:
                f.write(rezervace.priprav_zapis())
            print("✅ Rezervace byla úspěšně uložena do souboru rezervace.txt")
        except IOError:
            print("❌ Chyba: Do souboru nelze zapisovat. Zkontrolujte, zda není soubor otevřen jinde.")

        print("\n" + "=" * 40)
        print(f"REZERVAČNÍ SYSTÉM PRO: {host.jmeno_prijmeni}")
        print(f"TERMÍN: {prijezd_str} - {odjezd_str}")
        print(f"CELKOVÁ CENA: {rezervace.vypocti_celkovou_cenu()} Kč")
        if isinstance(host, Verny_host):
            print(f"UPLATNĚNA SLEVA: 10 % (Věrnostní karta: {host.cislo_karty}) ")
        print("=" * 40 + "\n")
        print(f"STAV OBSAZENOSTI: {zkontroluj_obsazenost_online()}")
        print(f"Roční období V TANVALDĚ v termínu rezervace: {ziskej_info_o_pobytu(prijezd_str)}")
        print("=" * 40 + "\n")
        print("Rezervace byla úspěšně zpracována. Děkujeme!")


if __name__ == "__main__":
    spustit_system()


