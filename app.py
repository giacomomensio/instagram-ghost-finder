import streamlit as st
import pandas as pd
import json
import re
from datetime import datetime

st.set_page_config(page_title="Instagram Ghost Finder", layout="wide")

# Funzione per pulire gli username
def clean_username(text):
    if not text:
        return None
    text = str(text).strip().lower()
    text = text.split('?')[0].split('#')[0].rstrip('/')
    match = re.search(r"instagram\.com/([^/]+)", text)
    if match:
        user = match.group(1)
    else:
        user = text.replace('@', '').strip()
    
    blacklist = [
        'about', 'archive', 'developers', 'help', 'legal', 'explore', 'reels', 
        'direct', 'accounts', 'p', 'stories', 'blog', 'meta', 'privacy', 'web'
    ]
    
    if user and user not in blacklist and user != "giacomomensio":
        user = user.split(' ')[0] 
        if not user.endswith(('.com', '.net', '.it')):
            return user
    return None

st.title("🕵️‍♂️ Instagram Ghost Finder & Ranker")
st.caption("Versione 3.4 - Fix Definitivo SyntaxError")

# --- SIDEBAR ---
st.sidebar.title("Configurazione Files")
fol_file = st.sidebar.file_uploader("1. Carica followers_1.json", type="json")
fng_file = st.sidebar.file_uploader("2. Carica following.json (Opzionale)", type="json")

# --- MESSAGGIO DI AVVIO ---
if not fol_file:
    st.info("👈 Per iniziare, carica il file 'followers_1.json' nella barra laterale a sinistra.")
    st.stop() 

# --- SEZIONE SCRIPT ---
with st.expander("🚀 Istruzioni Segnalibri (Scegli il tuo metodo)", expanded=False):
    
    tab1, tab2 = st.tabs(["🖱️ Metodo Rapido (Trascinamento)", "📑 Metodo Classico (Copia-Incolla)"])
    
    js_start = r"""javascript:(function(){window.allProfiles=window.allProfiles||new Set();window.myInterval=setInterval(()=>{document.querySelectorAll('a[role="link"]').forEach(a=>{if(a.href.includes("instagram.com/")&&!a.href.includes("/p/")&&!a.href.includes("/reels/")&&!a.href.includes("/explore/")){window.allProfiles.add(a.href)}});console.log("📊 Profili in memoria: "+window.allProfiles.size)},500);console.log("✅ Script avviato! Scorri la lista.");})();"""
    js_copy = r"""javascript:(function(){clearInterval(window.myInterval);if(window.allProfiles&&window.allProfiles.size>0){const t=[...window.allProfiles].join('\n');const el=document.createElement('textarea');el.value=t;document.body.appendChild(el);el.select();document.execCommand('copy');document.body.removeChild(el);alert("✅ "+window.allProfiles.size+" link copiati!");window.allProfiles=new Set();}else{alert("❌ Nessun profilo catturato.");}})();"""

    with tab1:
        st.markdown("""
        1. Fai **triplo click** sul codice qui sotto per selezionarlo tutto.
        2. **Trascina** il testo evidenziato sulla barra dei segnalibri.
        3. Inserisci il Nome per il segnalibro (es. `1. START` e `2. COPY`).
        """)
        st.code(js_start, language="javascript")
        st.code(js_copy, language="javascript")

    with tab2:
        st.markdown("""
        1. Crea un nuovo segnalibro sulla barra (Tasto destro -> Aggiungi pagina).
        2. Inserisci il nome (es. `1. START` e `2. COPY`).
        3. Incolla il codice corrispondente nel campo **URL**.
        """)
        c1, c2 = st.columns(2)
        with c1:
            st.write("**Codice START**")
            st.code(js_start, language="javascript")
        with c2:
            st.write("**Codice COPY**")
            st.code(js_copy, language="javascript")

# --- LOGICA DATI ---
fol_data = json.load(fol_file)
followers_info = {}
for item in fol_data:
    u = clean_username(item['string_list_data'][0]['value'])
    if u: followers_info[u] = item['string_list_data'][0]['timestamp']

following_list = set()
has_following = False
if fng_file:
    has_following = True
    fng_data = json.load(fng_file)
    raw_fng = fng_data.get('relationships_following', [])
    for entry in raw_fng:
        u = clean_username(entry.get('title')) or (clean_username(entry['string_list_data'][0].get('value')) if 'string_list_data' in entry else None)
        if u: following_list.add(u)

# --- ANALISI INTERAZIONI ---
st.divider()
st.subheader("Analisi Interazioni")

if 'sets_di_like' not in st.session_state:
    st.session_state.sets_di_like = []
if 'input_counter' not in st.session_state:
    st.session_state.input_counter = 0

manual_input = st.text_area("Incolla qui i link:", height=150, key=f"in_{st.session_state.input_counter}")
nome_set_input = st.text_input("Titolo set (Opzionale):", key=f"nm_{st.session_state.input_counter}")

if st.button("Aggiungi questi Like ➕", use_container_width=True):
    if manual_input.strip():
        nuovi = {clean_username(l) for l in manual_input.splitlines() if clean_username(l)}
        nuovi.discard(None)
        if nuovi:
            titolo = nome_set_input.strip() or f"Set {len(st.session_state.sets_di_like) + 1} ({len(nuovi)} profili)"
            st.session_state.sets_di_like.append({'nome': titolo, 'utenti': nuovi})
            st.session_state.input_counter += 1
            st.rerun()

# --- VISUALIZZAZIONE SET E CALCOLO ---
like_counts = {}
if st.session_state.sets_di_like:
    st.write("### 📦 Elenco Set Caricati:")
    sets_visualizzati = list(enumerate(st.session_state.sets_di_like))[::-1]
    for i, data in sets_visualizzati:
        for u in data['utenti']: 
            like_counts[u] = like_counts.get(u, 0) + 1
        c1, c2, c3 = st.columns([3, 2, 0.5])
        c1.info(f"📍 {data['nome']}")
        with c2:
            with st.expander(f"🔍 {len(data['utenti'])} profili"):
                st.caption(", ".join([f"@{u}" for u in sorted(list(data['utenti']))]))
        if c3.button("🗑️", key=f"del_{i}"):
            st.session_state.sets_di_like.pop(i)
            st.rerun()
    st.divider()

# --- METRICHE ---
follower_attivi = [u for u in followers_info if like_counts.get(u, 0) > 0]
ghost_follower = [u for u in followers_info if like_counts.get(u, 0) == 0]

m1, m2, m3, m4 = st.columns(4)
m1.metric("Followers Totali", len(followers_info))
m2.metric("Follower Attivi", len(follower_attivi))
m3.metric("Ghost Follower", len(ghost_follower))
m4.metric("Post Analizzati", len(st.session_state.sets_di_like))

# --- CLASSIFICA ---
all_users = set(followers_info.keys()).union(set(like_counts.keys()))
results = []
for user in all_users:
    row = {
        "Username": user,
        "Like": like_counts.get(user, 0),
        "Data Follow": datetime.fromtimestamp(followers_info[user]).strftime('%d/%m/%Y') if user in followers_info else "-",
        "Timestamp": followers_info.get(user, 9999999999),
        "Profilo": f"https://www.instagram.com/{user}/"
    }
    if has_following: row["Lo segui?"] = "Sì" if user in following_list else "NO ⚠️"
    results.append(row)

df = pd.DataFrame(results).sort_values(by=['Like', 'Timestamp'], ascending=[False, False])
st.subheader("Classifica Dettagliata")
st.dataframe(df.drop(columns=['Timestamp']), column_config={"Profilo": st.column_config.LinkColumn("Link")}, use_container_width=True, hide_index=True)

if has_following:
    not_following_back = [user for user in following_list if user not in followers_info]
    with st.expander(f"🚫 Chi non ti ricambia ({len(not_following_back)})"):
        for user in sorted(not_following_back):
            st.markdown(f"- [@{user}](https://www.instagram.com/{user}/)")