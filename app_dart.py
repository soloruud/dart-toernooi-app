import streamlit as st
import pandas as pd
import json
import os
import itertools

# --- 1. CONFIGURATIE & STYLING ---
st.set_page_config(
    page_title="🎯 Dart Toernooi Manager Ultra",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Volledig zwarte achtergrond en strakke dart-styling via CSS
st.markdown("""
    <style>
    .stApp, [data-testid="stSidebar"], [data-testid="stHeader"] {
        background-color: #000000 !important;
        color: #FFFFFF !important;
    }
    h1, h2, h3, h4, p, label, span, .stMarkdown {
        color: #FFFFFF !important;
        font-family: 'Segoe UI', Tahoma, sans-serif;
    }
    .stTextInput input, .stNumberInput input, .stSelectbox div {
        background-color: #111111 !important;
        color: #FFFFFF !important;
        border: 1px solid #333333 !important;
    }
    .stButton>button {
        background-color: #1a1a1a !important;
        color: #ffffff !important;
        border: 1px solid #ffcc00 !important;
        border-radius: 4px;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #ffcc00 !important;
        color: #000000 !important;
        box-shadow: 0 0 10px #ffcc00;
    }
    [data-testid="stDataFrame"] {
        background-color: #000000 !important;
    }
    .stAlert {
        background-color: #111111 !important;
        color: #ffffff !important;
        border: 1px solid #333333 !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. DATA OPSLAG & STATE ---
DATA_FILE = "dart_toernooi_data.json"

def laad_toernooi_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def sla_toernooi_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

# Initialiseer alle benodigde variabelen in de session state
saved_data = laad_toernooi_data()

if "spelers" not in st.session_state:
    st.session_state.spelers = saved_data.get("spelers", [
        {"naam": "Michael van Gerwen"}, {"naam": "Raymond van Barneveld"},
        {"naam": "Luke Littler"}, {"naam": "Luke Humphries"},
        {"naam": "Gerwyn Price"}, {"naam": "Gary Anderson"}
    ])
if "fase" not in st.session_state:
    st.session_state.fase = saved_data.get("fase", "Instellingen")
if "poule_wedstrijden" not in st.session_state:
    st.session_state.poule_wedstrijden = saved_data.get("poule_wedstrijden", [])
if "ko_wedstrijden" not in st.session_state:
    st.session_state.ko_wedstrijden = saved_data.get("ko_wedstrijden", [])
if "aantal_poules" not in st.session_state:
    st.session_state.aantal_poules = saved_data.get("aantal_poules", 2)
if "doorgaarders" not in st.session_state:
    st.session_state.doorgaarders = saved_data.get("doorgaarders", 2)
if "gekozen_ko_byes" not in st.session_state:
    st.session_state.gekozen_ko_byes = saved_data.get("gekozen_ko_byes", [])

def archiveer_en_save():
    sync_data = {
        "spelers": st.session_state.spelers,
        "fase": st.session_state.fase,
        "poule_wedstrijden": st.session_state.poule_wedstrijden,
        "ko_wedstrijden": st.session_state.ko_wedstrijden,
        "aantal_poules": st.session_state.aantal_poules,
        "doorgaarders": st.session_state.doorgaarders,
        "gekozen_ko_byes": st.session_state.gekozen_ko_byes
    }
    sla_toernooi_data(sync_data)

# --- 3. LOGICA VOOR GENEREREN SCHEMA'S ---
def genereer_poule_schema(poules):
    wedstrijden = []
    id_counter = 1
    for poule_naam, speler_lijst in poules.items():
        # Maak alle unieke combinaties binnen de poule (Round Robin)
        for s1, s2 in itertools.combinations(speler_lijst, 2):
            wedstrijden.append({
                "id": id_counter,
                "poule": poule_naam,
                "speler1": s1["naam"],
                "speler2": s2["naam"],
                "score1": 0,
                "score2": 0,
                "gespeeld": False
            })
            id_counter += 1
    return wedstrijden

# --- 4. ZIJBALK (ALTIJD ZICHTBAAR VOOR BEHEER) ---
with st.sidebar:
    st.header("🎯 Toernooi Beheer")
    st.write(f"**Huidige Fase:** {st.session_state.fase}")
    
    if st.session_state.fase == "Instellingen":
        st.session_state.aantal_poules = st.number_input("Aantal Poules", min_value=1, value=st.session_state.aantal_poules)
        st.session_state.doorgaarders = st.number_input("Doorgaarders per poule", min_value=1, value=st.session_state.doorgaarders)
        
        st.write("---")
        st.subheader("👥 Spelers Toevoegen")
        nieuwe_speler = st.text_input("Naam speler:")
        if st.button("➕ Voeg Toe"):
            if nieuwe_speler.strip() and not any(s['naam'].lower() == nieuwe_speler.strip().lower() for s in st.session_state.spelers):
                st.session_state.spelers.append({"naam": nieuwe_speler.strip()})
                archiveer_en_save()
                st.rerun()
                
        st.write("---")
        st.subheader("🗑️ Speler Wissen")
        if st.session_state.spelers:
            wissen = st.selectbox("Kies:", [s["naam"] for s in st.session_state.spelers])
            if st.button("❌ Verwijder"):
                st.session_state.spelers = [s for s in st.session_state.spelers if s["naam"] != wissen]
                archiveer_en_save()
                st.rerun()
                
        if len(st.session_state.spelers) >= 2:
            st.write("---")
            if st.button("🚀 Start Poulefase & Schema"):
                # Verdeel spelers over poules
                poules = {f"Poule {i+1}": [] for i in range(st.session_state.aantal_poules)}
                for idx, speler in enumerate(st.session_state.spelers):
                    p_naam = f"Poule {(idx % st.session_state.aantal_poules) + 1}"
                    poules[p_naam].append(speler)
                
                st.session_state.poule_wedstrijden = genereer_poule_schema(poules)
                st.session_state.fase = "Poulefase"
                archiveer_en_save()
                st.rerun()
    else:
        if st.button("🔄 Reset Toernooi (Wis Alles)"):
            st.session_state.fase = "Instellingen"
            st.session_state.poule_wedstrijden = []
            st.session_state.ko_wedstrijden = []
            st.session_state.gekozen_ko_byes = []
            archiveer_en_save()
            st.rerun()

# --- 5. HOOFDSCHERM LOGICA PER FASE ---

# --- FASE 1: POULEFASE ---
if st.session_state.fase == "Poulefase":
    st.title("🏆 Poulefase & Speelschema")
    
    # Bereken de actuele standen live op basis van handmatig ingevulde wedstrijden
    standen = {s["naam"]: {"punten": 0, "legs_voor": 0, "legs_tegen": 0} for s in st.session_state.spelers}
    for w in st.session_state.poule_wedstrijden:
        if w["gespeeld"]:
            s1, s2 = w["speler1"], w["speler2"]
            standen[s1]["legs_voor"] += w["score1"]
            standen[s1]["legs_tegen"] += w["score2"]
            standen[s2]["legs_voor"] += w["score2"]
            standen[s2]["legs_tegen"] += w["score1"]
            if w["score1"] > w["score2"]:
                standen[s1]["punten"] += 3
            elif w["score2"] > w["score1"]:
                standen[s2]["punten"] += 3
            else:
                standen[s1]["punten"] += 1
                standen[s2]["punten"] += 1

    # Poules Dict bouwen voor weergave
    poules_dict = {f"Poule {i+1}": [] for i in range(st.session_state.aantal_poules)}
    for idx, speler in enumerate(st.session_state.spelers):
        p_naam = f"Poule {(idx % st.session_state.aantal_poules) + 1}"
        s_naam = speler["naam"]
        st_data = standen.get(s_naam, {"punten": 0, "legs_voor": 0, "legs_tegen": 0})
        poules_dict[p_naam].append({
            "naam": s_naam,
            "punten": st_data["punten"],
            "saldo": st_data["legs_voor"] - st_data["legs_tegen"]
        })

    # Toon de dynamische Poule Standen bovenin
    st.header("📊 Live Tussenstanden")
    poule_kolommen = st.columns(st.session_state.aantal_poules)
    gekwalificeerde_spelers = []
    
    for idx, (p_titel, s_lijst) in enumerate(poules_dict.items()):
        with poule_kolommen[idx]:
            st.subheader(f"🟩 {p_titel}")
            # Sorteer op punten, daarna op leg-saldo
            gesorteerd = sorted(s_lijst, key=lambda x: (x["punten"], x["saldo"]), reverse=True)
            
            tabel_data = []
            for pos, speler in enumerate(gesorteerd):
                naam_weergave = speler["naam"]
                if pos == 0:
                    naam_weergave = f"😊⭐ {naam_weergave}"
                elif pos == 1:
                    naam_weergave = f"⭐ {naam_weergave}"
                
                is_door = pos < st.session_state.doorgaarders
                if is_door:
                    gekwalificeerde_spelers.append(speler["naam"])
                
                tabel_data.append({
                    "Pos": pos + 1,
                    "Naam": naam_weergave,
                    "Punten": speler["punten"],
                    "Saldo": speler["saldo"],
                    "Status": "Door ✅" if is_door else "Afgevallen ❌"
                })
            st.dataframe(pd.DataFrame(tabel_data), hide_index=True, use_container_width=True)

    # Invulbaar Speelschema Poule
    st.write("---")
    st.header("📝 Speelschema Poule Invullen")
    st.write("Pas de scores aan en vink 'Gespeeld' aan om de stand hierboven direct live te updaten.")
    
    for w in st.session_state.poule_wedstrijden:
        col_p, col_w1, col_sc1, col_vs, col_sc2, col_w2, col_ok = st.columns([1, 2, 1, 0.5, 1, 2, 1])
        with col_p:
            st.write(f"_{w['poule']}_")
        with col_w1:
            st.write(f"**{w['speler1']}**")
        with col_sc1:
            s1_val = st.number_input("Score S1", min_value=0, value=w["score1"], step=1, key=f"s1_{w['id']}", label_visibility="collapsed")
        with col_vs:
            st.write("vs")
        with col_sc2:
            s2_val = st.number_input("Score S2", min_value=0, value=w["score2"], step=1, key=f"s2_{w['id']}", label_visibility="collapsed")
        with col_w2:
            st.write(f"**{w['speler2']}**")
        with col_ok:
            gespeeld_val = st.checkbox("Gespeeld", value=w["gespeeld"], key=f"chk_{w['id']}")
            
        # Update waarden direct in state als er iets verandert
        if s1_val != w["score1"] or s2_val != w["score2"] or gespielt_val != w["gespeeld"]:
            w["score1"] = s1_val
            w["score2"] = s2_val
            w["gespeeld"] = gespielt_val
            archiveer_en_save()
            st.rerun()

    st.write("---")
    if st.button("🔥 Poulefase Sluiten & Naar Afvalronde"):
        st.session_state.fase = "Bye Selectie"
        archiveer_en_save()
        st.rerun()

# --- FASE 2: BYE SELECTIE VOOR DE AFVALRONDE ---
elif st.session_state.fase == "Bye Selectie":
    st.title("🛡️ Afvalronde Inrichten & Byes")
    
    # Haal de geplaatste spelers opnieuw op uit de poulestanden
    standen = {s["naam"]: {"punten": 0, "legs_voor": 0, "legs_tegen": 0} for s in st.session_state.spelers}
    for w in st.session_state.poule_wedstrijden:
        if w["gespeeld"]:
            standen[w["speler1"]]["legs_voor"] += w["score1"]
            standen[w["speler1"]]["legs_tegen"] += w["score2"]
            standen[w["speler2"]]["legs_voor"] += w["score2"]
            standen[w["speler2"]]["legs_tegen"] += w["score1"]
            if w["score1"] > w["score2"]: standen[w["speler1"]]["punten"] += 3
            elif w["score2"] > w["score1"]: standen[w["wplayer2"] if "wplayer2" in w else "speler2"]["punten"] += 3
    
    poules_dict = {f"Poule {i+1}": [] for i in range(st.session_state.aantal_poules)}
    for idx, speler in enumerate(st.session_state.spelers):
        p_naam = f"Poule {(idx % st.session_state.aantal_poules) + 1}"
        poules_dict[p_naam].append({"naam": speler["naam"], "punten": standen[speler["naam"]]["punten"], "saldo": standen[speler["naam"]]["legs_voor"] - standen[speler["naam"]]["legs_tegen"]})
    
    door_spelers = []
    for p_titel, s_lijst in poules_dict.items():
        gesorteerd = sorted(s_lijst, key=lambda x: (x["punten"], x["saldo"]), reverse=True)
        for pos, speler in enumerate(gesorteerd):
            if pos < st.session_state.doorgaarders:
                door_spelers.append(speler["naam"])

    st.subheader(f"Gekwalificeerde spelers uit de poule ({len(door_spelers)} totaal):")
    st.write(", ".join(door_spelers))
    
    # Berekening van het dichtstbijzijnde macht van 2 (2, 4, 8, 16) schema
    aantal_gekwalificeerd = len(door_spelers)
    volgende_macht_van_2 = 2**((aantal_gekwalificeerd - 1).bit_length()) if aantal_gekwalificeerd > 1 else 2
    benodigde_byes = volgende_macht_van_2 - aantal_gekwalificeerd
    
    st.info(f"Voor een perfect afvalschema hebben we een bracket van **{volgende_macht_van_2}** nodig. Dit betekent dat er **{benodigde_byes}** speler(s) een **Bye** moeten krijgen.")
    
    if benodigde_byes > 0:
        st.write("Selecteer wie een Bye krijgt voor de eerste ronde:")
        gekozen_byes = st.multiselect("Kies de spelers voor een Bye:", door_spelers, max_selections=benodigde_byes)
        st.session_state.gekozen_ko_byes = gekozen_byes
    else:
        st.write("Aantal deelnemers komt perfect uit! Geen Byes nodig.")
        st.session_state.gekozen_ko_byes = []

    if st.button("🔨 Genereer Knock-out Schema"):
        # Matchmaking: Spelers die GEEN bye hebben moeten tegen elkaar dartsen
        spelers_met_wedstrijd = [s for s in door_spelers if s not in st.session_state.gekozen_ko_byes]
        
        ko_wedstrijden = []
        id_ko = 1
        # Koppel ze per twee aan elkaar
        for i in range(0, len(spelers_met_wedstrijd), 2):
            if i+1 < len(spelers_met_wedstrijd):
                ko_wedstrijden.append({
                    "id": id_ko,
                    "speler1": spelers_met_wedstrijd[i],
                    "speler2": spelers_met_wedstrijd[i+1],
                    "score1": 0,
                    "score2": 0,
                    "winnaar": "",
                    "gespeeld": False
                })
                id_ko += 1
        
        st.session_state.ko_wedstrijden = ko_wedstrijden
        st.session_state.fase = "Afvalronde"
        archiveer_en_save()
        st.rerun()

# --- FASE 3: AFVALRONDE (KNOCK-OUT) ---
elif st.session_state.fase == "Afvalronde":
    st.title("⚡ De Afvalronde (Knock-out)")
    
    if st.session_state.gekozen_ko_byes:
        st.subheader("🛡️ Spelers met een Bye (stroomt automatisch door naar volgende ronde):")
        st.write(", ".join(st.session_state.gekozen_ko_byes))
        
    st.write("---")
    st.header("🎯 Live Knock-out Schema")
    
    if not st.session_state.ko_wedstrijden:
        st.success("Alle knock-out rondes zijn verwerkt!")
    else:
        for kw in st.session_state.ko_wedstrijden:
            col_w1, col_sc1, col_vs, col_sc2, col_w2, col_chk = st.columns([2, 1, 0.5, 1, 2, 1])
            with col_w1:
                st.write(f"**{kw['speler1']}**")
            with col_sc1:
                s1_val = st.number_input("Score S1", min_value=0, value=kw["score1"], step=1, key=f"ko_s1_{kw['id']}", label_visibility="collapsed")
            with col_vs:
                st.write("vs")
            with col_sc2:
                s2_val = st.number_input("Score S2", min_value=0, value=kw["score2"], step=1, key=f"ko_s2_{kw['id']}", label_visibility="collapsed")
            with col_w2:
                st.write(f"**{kw['speler2']}**")
            with col_chk:
                gespeeld_val = st.checkbox("Match Klaar", value=kw["gespeeld"], key=f"ko_chk_{kw['id']}")
                
            if s1_val != kw["score1"] or s2_val != kw["score2"] or gespielt_val != kw["gespeeld"]:
                kw["score1"] = s1_val
                kw["score2"] = s2_val
                kw["gespeeld"] = gespielt_val
                if gespielt_val:
                    kw["winnaar"] = kw["speler1"] if s1_val > s2_val else kw["speler2"]
                else:
                    kw["winnaar"] = ""
                archiveer_en_save()
                st.rerun()

    # Knop om de winnaars te verzamelen en de volgende knock-out ronde (bijv. de finale) te starten
    st.write("---")
    alle_ko_gespeeld = all(kw["gespeeld"] for kw in st.session_state.ko_wedstrijden) if st.session_state.ko_wedstrijden else False
    
    if alle_ko_gespeeld:
        if st.button("🏆 Volgende Knock-out Ronde Genereren"):
            # Pak de winnaars van de net gespeelde wedstrijden + de spelers die een Bye hadden
            winnaars = [kw["winnaar"] for kw in st.session_state.ko_wedstrijden]
            volgende_ronde_spelers = winnaars + st.session_state.gekozen_ko_byes
            
            # Reset de Byes voor de volgende ronde (iedereen speelt nu)
            st.session_state.gekozen_ko_byes = []
            
            if len(volgende_ronde_spelers) == 1:
                st.balloons()
                st.success(f"🎉 we hebben een toernooiwinnaar: **{volgende_ronde_spelers[0]}**!")
                st.session_state.ko_wedstrijden = []
            else:
                nieuwe_ko = []
                id_ko = 1
                for i in range(0, len(volgende_ronde_spelers), 2):
                    if i+1 < len(volgende_ronde_spelers):
                        nieuwe_ko.append({
                            "id": id_ko,
                            "speler1": volgende_ronde_spelers[i],
                            "speler2": volgende_ronde_spelers[i+1],
                            "score1": 0,
                            "score2": 0,
                            "winnaar": "",
                            "gespeeld": False
                        })
                        id_ko += 1
                st.session_state.ko_wedstrijden = nieuwe_ko
            archiveer_en_save()
            st.rerun()
            
else:
    # Opstartscherm / Instellingenfase
    st.title("⚙️ Welkom bij het Dart Toernooi")
    st.write("Vul in het linkermenu de inst
