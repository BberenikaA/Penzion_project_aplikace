# Rezervační systém pro Penzion pod Špičákem (Tanvald)

Projekt pro vytvoření rezervačního systému pro reálný objekt: **Penzion pod Špičákem (Pod Špičákem 336, Tanvald)**.
Web: www.penzionpodspicakem.cz

## Funkce systému
* **Využití externích a interních knihoven:** 
  * Knihovna `requests` pro komunikaci s internetovými servery (stahování počasí a kontrola kalendáře).
  * Knihovna `datetime` pro práci s daty, časem a výpočty termínů.
* **Objektově orientované programování (OOP):** Využití tříd `Host` a `Rezervace` pro přehlednou správu dat.
  * Dědičnost a slevový systém: Implementace mateřské třídy `Host` a dceřiné třídy `Verny_host`. Využití dědičnosti pro automatické uplatnění 10% slevy u věrných zákazníků. Dynamické ověřování typu instance pomocí `isinstance`.
* **Validace vstupů:** Automatická kontrola formátu e-mailu a telefonního čísla.
* **Kontrola kapacity:** Hlídání kapacity penzionu (12-22 osob) a minimální délky pobytu (2 noci).
* **Chytrý výpočet termínu:** Po zadání data příjezdu a počtu nocí systém sám automaticky dopočítá přesné datum odjezdu.
* **Ošetření chyb (Try-Except):** Použití cyklu `while` a bloku `try-except` pro ošetření chybných uživatelských vstupů (ValueError).
  * Ošetření chyb při zápisu do souboru pomocí `IOError` (např. při nedostatku práv k zápisu nebo uzamčení souboru jiným programem).
* **Správa dat:** Rezervace jsou automaticky ukládány do souboru `rezervace.txt`.

## Implementované (původně plánované) funkce
* **Správa rezervací:** Výpočet ceny na základě počtu osob (450 Kč/osoba) a délky pobytu (se stropem 8000 Kč za noc za celý penzion).
* Rozšířená logika zpracování: Podmíněné větvení programu na základě vlastnictví věrnostní karty. Zapouzdření výpočtu slevy přío do metod tříd hosta. Centralizovaná konfigurace sazeb a limitů v externím modulu `config.py`.
* **iCal Synchronizace:** Automatické hlídání obsazenosti propojením s utajenou adresou kalendáře z e-chalupy.cz. Tato adresa je z důvodu bezpečnosti uložena v souboru `config.py` a kód je ošetřen pro případ výpadku sítě.
* **Počasí pro hosty:** Integrace aktuální předpovědi (Open-Meteo API) přímo pro lokalitu **Tanvald** a automatické doporučení aktivit podle měsíce příjezdu. Zpracování dat pomocí funkce `.json()`.

## Ignorované soubory (.gitignore)
Projekt využívá soubor `.gitignore` pro vyloučení systémových a osobních souborů z verzování na GitHubu:
* `.idea/` – lokální konfigurační složka vývojového prostředí PyCharm.
* `__pycache__/` – automaticky generované mezipaměti Pythonu pro rychlejší běh.
* `.venv/` – složka virtuálního prostředí se staženými knihovnami.
* `config.py` – soubor s citlivou URL adresou kalendáře z důvodu bezpečnosti.
* `rezervace.txt` – lokální databáze rezervací (aby se na GitHub v budoucnu nepřenášela reálná data hostů, pro současnou potřebu jsou data fiktivní).

## Technické informace
* Projekt je vyvíjen v jazyce Python 3.14.0
* Použití knihoven `datetime` (interní) a `requests` a `icalevents` (externí).
* Kódování souborů:** `UTF-8` (pro správné zobrazení českých znaků v souboru `rezervace.txt`)

## Instalace a spuštění
Projekt vyžaduje ke svému běhu instalaci externích knihoven viz. výše. V terminálu spusťte následující příkaz: `pip install requests icalevents`

## Aktualizace projektu (Propojení s tabulkou)
Propojení přes **Google Apps Script**.

### Novinky v kódu:
- Knihovna **Requests:** je využívána pro zápis dat do tabulky ve spojení s **Google Apps Script**.
- **Google Apps Script:** Funkce `doGet(e)` přijímá data z aplikace a zapisuje je do prvního volného řádku v tabulce.
- **Bezpečnost:** Data jsou odesílána na soukromý endpoint (Web App URL) běžící v rámci Google.
- **Stabilita** Výše uvedený systém obchází knihovny `st-gsheets-connection` a umožňuje zápis dat i bez aktivace placených služeb v Google Cloud Console.

### Jak to funguje nyní:
1. Uživatel odešle formulář.
2. Streamlit vytvoří balíček dat (params).
3. Pomocí `requests.get` se data pošlou do Google Apps Scriptu.
4. Skript provede zápis do Google Tabulky.
5. 
