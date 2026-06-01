import streamlit as st
import pandas as pd
import json
import os

# --- 1. CONFIGURATIE & STREAMLIT SETTINGS ---
st.set_page_config(
    page_title="🎯 Dart Toernooi Manager Pro",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Volledig zwarte achtergrond en strakke dart-styling via CSS injection
st.markdown("""
    <style>
    /* Achtergronden naar puur zwart */
    .stApp, [data-testid="stSidebar"], [data-testid="stHeader"] {
        background-color: #000000 !important;
        color: #FFFFFF !important;
    }
    
    /* Alle teksten wit */
    h1, h2, h3, h4, h5, h6, p, label, span, .stMarkdown {
        color: #FFFFFF !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* Aanpassingen voor invoervelden zodat ze leesbaar zijn op zwart */
    .stTextInput input, .stNumberInput input, .stSelectbox div {
        background-color: #111111 !important;
        color: #FFFFFF !important;
        border: 1px solid #333333 !important;
    }
    
    /* Knoppen styling */
    .stButton>button {
        background-color: #1a1a1a !important;
        color: #ffffff !important;
        border: 1px solid #ffcc00 !important;
        border-radius: 4px;
        transition: all 0.3s ease;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #ffcc00 !important;
        color: #000000 !important;
        box-shadow: 0 0 10px #ffcc00;
    }
    
    /* Dataframe styling overschrijven voor donker thema */
    [data-testid="stDataFrame"] {
        background-color: #000000 !important;
        border: 1px solid #222222 !important;
    }
    
    /* Gekleurde succes/info boxen blenden */
    .stAlert {
        background-color: #111111 !important;
        color: #ffffff !important;
        border: 1px solid #333333 !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. DATA OPSLAG & PERSISTENTIE ---
# Slaat spelers op in een lokaal JSON-bestandje zodat ze onthouden worden!
DATA_FILE = "dart_spelers_opslag.json"

def laad_spelers():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as f:
                return json.load(f)
        except:
            return []
    return []

def sla_spelers_op(spelers_lijst):
    with open(DATA_FILE, 'w') as f:
        json.dump(spelers_lijst, f, indent=4)

# Initialiseer session state
if "spelers" not in st.session_state:
    geladen_spelers = laad_spelers()
    if not geladen_spelers:
        # Standaard startdata als het bestand nog leeg is
        st.session_state.spelers = [
            {"naam": "Michael van Gerwen", "byes": 0, "punten": 12, "leg_saldo": 8},
            {"naam": "Raymond van Barneveld", "byes": 0, "punten": 9, "leg_saldo": 4},
            {"naam": "Luke Littler", "byes": 0, "punten": 15, "leg_saldo": 11},
            {"naam": "Luke Humphries", "byes": 0, "punten": 6, "leg_saldo": 1},
            {"naam": "Gerwyn Price", "byes": 1, "punten": 3, "leg_saldo": -3},
            {"naam": "Gary Anderson", "byes": 0, "punten": 0, "leg_saldo": -6}
        ]
        sla_spelers_op(st.session_state.spelers)
    else:
        st.session_state.spelers = geladen_spelers

# --- 3. HOOFDMENU & LAYOUT ---
st.title("🎯 Dart Toernooi Manager Pro")
st.write("Gekoppeld met GitHub & Streamlit Cloud — Volledig dynamisch poulebeheer.")

# --- 4. ZIJBALK (INRICHTING & SPELERSBEHEER) ---
with st.sidebar:
    st.header("⚙️ Toernooi Instellingen")
    aantal_poules = st.number_input("Aantal Poules", min_value=1, value=2, step=1)
    doorgaarders = st.number_input("Aantal door naar afvalronde (per poule)", min_value=1, value=2, step=1)
    
    st.write("---")
    st.header("👥 Spelersbeheer")
    
    # Speler Toevoegen
    with st.form("add_speler_form", clear_on_submit=True):
        nieuwe_speler = st.text_input("Naam Dartspeler:")
        heeft_bye = st.checkbox("Speler heeft een Bye 🛡️")
        submit_add = st.form_submit_button("➕ Voeg Speler Toe")
        
        if submit_add:
            if nieuwe_speler.strip():
                bestaat_al = any(s['naam'].lower() == nieuwe_speler.strip().lower() for s in st.session_state.spelers)
                if not bestaat_al:
                    st.session_state.spelers.append({
                        "naam": nieuwe_speler.strip(),
                        "byes": 1 if heeft_bye else 0,
                        "punten": 0,
                        "leg_saldo": 0
                    })
                    sla_spelers_op(st.session_state.spelers)
                    st.success(f"🎯 {nieuwe_speler} toegevoegd & opgeslagen!")
                    st.rerun()
                else:
                    st.error("Speler bestaat al!")
            else:
                st.warning("Vul een geldige naam in.")

    # Speler Verwijderen
    st.write("---")
    st.subheader("🗑️ Speler Verwijderen")
    if st.session_state.spelers:
        opties_verwijderen = [s["naam"] for s in st.session_state.spelers]
        te_verwijderen = st.selectbox("Kies speler om te wissen:", opties_verwijderen)
        if st.button("❌ Verwijder Speler"):
            st.session_state.spelers = [s for s in st.session_state.spelers if s["naam"] != te_verwijderen]
            sla_spelers_op(st.session_state.spelers)
            st.success(f"{te_verwijderen} succesvol gewist!")
            st.rerun()

# --- 5. POULE-INDELING EN DYNAMISCHE STANDEN ---
st.header("🏆 Live Poule Standen")

if not st.session_state.spelers:
    st.info("Voeg spelers toe in de zijbalk om het toernooi te starten.")
else:
    # Verdeel spelers over poules via slang-volgorde
    poules_dict = {f"Poule {i+1}": [] for i in range(aantal_poules)}
    for index, speler in enumerate(st.session_state.spelers):
        poule_naam = f"Poule {(index % aantal_poules) + 1}"
        poules_dict[poule_naam].append(speler)
        
    poule_kolommen = st.columns(aantal_poules)
    
    for idx, (poule_titel, speler_lijst) in enumerate(poules_dict.items()):
        with poule_kolommen[idx % aantal_poules]:
            st.subheader(f"🥇 {poule_titel}")
            
            if not speler_lijst:
                st.write("_Geen spelers in deze poule_")
                continue
                
            # Sortering op Punten (eerst) en Leg Saldo (tweede als tie-breaker)
            gesorteerd = sorted(speler_lijst, key=lambda x: (x["punten"], x["leg_saldo"]), reverse=True)
            
            tabel_data = []
            for pos, speler in enumerate(gesorteerd):
                weergave_naam = speler["naam"]
                
                # --- DYNAMISCHE ICONEN ---
                if pos == 0:
                    weergave_naam = f"😊⭐ {weergave_naam}"
                elif pos == 1:
                    weergave_naam = f"⭐ {weergave_naam}"
                    
                # Bye Status tonen
                if speler.get("byes", 0) > 0:
                    weergave_naam += " (Bye 🛡️)"
                    
                # Gekwalificeerd status check
                status = "Volgende Ronde ✅" if pos < doorgaarders else "Uitgeschakeld ❌"
                
                tabel_data.append({
                    "Pos": pos + 1,
                    "Naam": weergave_naam,
                    "Punten": speler["punten"],
                    "Leg Saldo": speler["leg_saldo"],
                    "Status": status
                })
                
            df = pd.DataFrame(tabel_data)
            st.dataframe(df, hide_index=True, use_container_width=True)

# --- 6. LIVE WEDSTRIJD / SCORE VERWERKING ---
st.write("---")
st.header("🎯 Scores & Tussenstanden Live Bijwerken")
st.write("Wijzig hieronder de totalen. De poulestand, smileys en sterren veranderen direct live mee bovenin!")

if st.session_state.spelers:
    col_s1, col_s2, col_s3 = st.columns(3)
    
    with col_s1:
        geselecteerde_speler = st.selectbox("Selecteer de dartspeler:", [s["naam"] for s in st.session_state.spelers], key="score_speler")
        
    huidige_speler_data = next(s for s in st.session_state.spelers if s["naam"] == geselecteerde_speler)
    
    with col_s2:
        nieuwe_punten = st.number_input("Totaal aantal Punten:", min_value=0, value=int(huidige_speler_data["punten"]), step=1, key="score_pts")
    with col_s3:
        nieuw_saldo = st.number_input("Totaal Leg Saldo (+/-):", value=int(huidige_speler_data["leg_saldo"]), step=1, key="score_legs")
        
    if st.button("💾 Wijzigingen Opslaan & Berekenen"):
        for s in st.session_state.spelers:
            if s["naam"] == geselecteerde_speler:
                s["punten"] = nieuwe_punten
                s["leg_saldo"] = nieuw_saldo
                break
        sla_spelers_op(st.session_state.spelers)
        st.success(f"Stand voor {geselecteerde_speler} succesvol bijgewerkt!")
        st.rerun()