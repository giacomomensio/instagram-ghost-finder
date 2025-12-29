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
st.caption("Versione 3.1 - Gestione flussi e contatore post")

# --- SIDEBAR ---
st.sidebar.title("Configurazione Files")
fol_file = st.sidebar.file_uploader("1. Carica followers_1.json", type="json")
fng_file = st.sidebar.file_uploader("2. Carica following.json (Opzionale)", type="json")

# --- NUOVO POSIZIONAMENTO MESSAGGIO DI AVVIO ---
if not fol_file:
    st.info("👈 Per iniziare, carica il file 'followers_1.json' nella barra laterale a sinistra.")
    st.stop() 

# --- SEZIONE SCRIPT (Collassata) ---
with st.expander("🚀 Istruzioni e Script per Console Browser", expanded=False):
    st.markdown("""
    1. Apri Instagram da PC e clicca sui 'Mi piace' di un post.
    2. Premi **F12** (o tasto destro -> Ispeziona) e vai in **Console**.
    3. Copia lo **Step 1**, incollalo in console e scorri la lista.
    4. Quando hai finito, copia lo **Step 2** per copiare i link.
    
    *Ricorda: questa app è di terze parti e non è in alcun modo affiliata all'Agenzia delle Entrate.*
    """)
    
    col_a, col_b = st.columns(2)
    
    script_1 = r"""if (window.myInterval) clearInterval(window.myInterval);
window.allProfiles = window.allProfiles || new Set();
window.myInterval = setInterval(() => {
    document.querySelectorAll('a[role="link"]').forEach(a => {
        if(a.href.includes("instagram.com/") && !a.href.includes("/p/") && !a.href.includes("/reels/") && !a.href.includes("/explore/")) {
            window.allProfiles.add(a.href);
        }
    });
    console.log("📊 Profili in memoria: " + window.allProfiles.size);
}, 500);
console.log("✅ Script avviato! Scorri LENTAMENTE la lista.");"""

    script_2 = r"""clearInterval(window.myInterval);
if (window.allProfiles && window.allProfiles.size > 0) {
    copy([...window.allProfiles].join('\n'));
    console.log("✅ " + window.allProfiles.size + " link copiati!");
    window.allProfiles = new Set();
} else {
    console.error("❌ Errore: Nessun profilo catturato.");
}"""

    with col_a:
        st.subheader("Step 1: Avvia Cattura")
        st.code(script_1, language="javascript")
    with col_b:
        st.subheader("Step 2: Copia Risultati")
        st.code(script_2, language="javascript")

# --- LOGICA PRINCIPALE ---
if fol_file:
    fol_data = json.load(fol_file)
    followers_info = {}
    for item in fol_data:
        u = clean_username(item['string_list_data'][0]['value'])
        if u:
            followers_info[u] = item['string_list_data'][0]['timestamp']
    
    following_list = set()
    has_following = False
    if fng_file:
        has_following = True
        fng_data = json.load(fng_file)
        raw_fng = fng_data.get('relationships_following', [])
        for entry in raw_fng:
            u_title = clean_username(entry.get('title'))
            if u_title:
                following_list.add(u_title)
            elif 'string_list_data' in entry and entry['string_list_data']:
                u_val = clean_username(entry['string_list_data'][0].get('value'))
                if u_val:
                    following_list.add(u_val)

    st.divider()
    st.subheader("Analisi Interazioni")
    
    if 'sets_di_like' not in st.session_state:
        st.session_state.sets_di_like = []
    
    if 'input_counter' not in st.session_state:
        st.session_state.input_counter = 0

    testarea_key = f"input_area_{st.session_state.input_counter}"
    manual_input = st.text_area("Incolla qui i link (Step 2):", height=150, key=testarea_key)
    
    nome_set_input = st.text_input("Titolo del set (es: Post 12/11) - Opzionale:", 
                                   key=f"nome_set_{st.session_state.input_counter}",
                                   placeholder="Lascia vuoto per nome automatico")

    if st.button("Aggiungi questi Like ➕", use_container_width=True):
        if manual_input.strip():
            lines = manual_input.splitlines()
            nuovi_utenti = {clean_username(line) for line in lines if clean_username(line)}
            nuovi_utenti.discard(None)
            
            if nuovi_utenti:
                if not nome_set_input.strip():
                    titolo_finale = f"Set {len(st.session_state.sets_di_like) + 1} ({len(nuovi_utenti)} profili)"
                else:
                    titolo_finale = f"{nome_set_input.strip()} ({len(nuovi_utenti)} profili)"
                
                st.session_state.sets_di_like.append({'nome': titolo_finale, 'utenti': nuovi_utenti})
                st.session_state.input_counter += 1
                st.success(f"'{titolo_finale}' aggiunto!")
                st.rerun()
        else:
            st.warning("Il box è vuoto!")

    # --- CALCOLO E VISUALIZZAZIONE SET ---
    like_counts = {}
    if st.session_state.sets_di_like:
        st.write("### 📦 Elenco Set Caricati:")
        sets_visualizzati = list(enumerate(st.session_state.sets_di_like))[::-1]

        for original_index, set_data in sets_visualizzati:
            for u in set_data['utenti']:
                like_counts[u] = like_counts.get(u, 0) + 1
            
            col_info, col_expand, col_del = st.columns([3, 2, 0.5])
            with col_info:
                st.info(f"📍 {set_data['nome']}")
            with col_expand:
                lista_alfabetica = sorted(list(set_data['utenti']))
                with st.expander(f"🔍 {len(lista_alfabetica)} profili"):
                    st.caption(", ".join([f"@{u}" for u in lista_alfabetica]))
            with col_del:
                if st.button("🗑️", key=f"del_{original_index}"):
                    st.session_state.sets_di_like.pop(original_index)
                    st.rerun()
        st.divider()
    else:
        st.info("Nessun set di like aggiunto.")
        
    # --- METRICHE FINALI ---
    follower_attivi = [u for u in followers_info if like_counts.get(u, 0) > 0]
    ghost_follower = [u for u in followers_info if like_counts.get(u, 0) == 0]

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Followers Totali", len(followers_info))
    m2.metric("Follower Attivi", len(follower_attivi))
    m3.metric("Ghost Follower", len(ghost_follower))
    m4.metric("Post Analizzati", len(st.session_state.sets_di_like))

    # --- TABELLA CLASSIFICA ---
    all_users = set(followers_info.keys()).union(set(like_counts.keys()))
    results = []
    for user in all_users:
        likes = like_counts.get(user, 0)
        follow_time = followers_info.get(user)
        row = {
            "Username": user,
            "Like": likes,
            "Data Follow": datetime.fromtimestamp(follow_time) if follow_time else None,
            "Timestamp": follow_time if follow_time else 9999999999,
            "Profilo": f"https://www.instagram.com/{user}/"
        }
        if has_following:
            row["Lo segui?"] = "Sì" if user in following_list else "NON LO SEGUI ⚠️"
        results.append(row)

    df = pd.DataFrame(results).sort_values(by=['Like', 'Timestamp'], ascending=[False, False])
    df['Data Follow'] = df['Data Follow'].dt.strftime('%d/%m/%Y').fillna("-")
    
    cols_to_show = ["Username", "Like"]
    if has_following: cols_to_show.append("Lo segui?")
    cols_to_show.extend(["Data Follow", "Profilo"])
    
    st.subheader("Classifica Dettagliata")
    st.dataframe(df[cols_to_show], column_config={"Profilo": st.column_config.LinkColumn("Link")}, use_container_width=True, hide_index=True)

    if has_following:
        not_following_back = [user for user in following_list if user not in followers_info]
        with st.expander(f"🚫 Chi non ti ricambia ({len(not_following_back)})"):
            for user in sorted(not_following_back):
                st.markdown(f"- [@{user}](https://www.instagram.com/{user}/)")