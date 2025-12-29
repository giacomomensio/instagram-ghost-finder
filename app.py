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
        'about', 'developers', 'help', 'legal', 'explore', 'reels', 
        'direct', 'accounts', 'p', 'stories', 'blog', 'meta', 'privacy', 'web'
    ]
    
    if user and user not in blacklist and user != "giacomomensio":
        user = user.split(' ')[0] 
        if not user.endswith(('.com', '.net', '.it')):
            return user
    return None

st.title("🕵️‍♂️ Instagram Ghost Finder & Ranker")
st.caption("Versione 2.9 - Script integrati con pulsanti di copia")

# --- SEZIONE SCRIPT (Novità) ---
with st.expander("🚀 Istruzioni e Script per Console Browser", expanded=False):
    st.markdown("""
    1. Apri Instagram da PC e clicca sui 'Mi piace' di un post.
    2. Premi **F12** (o tasto destro -> Ispeziona) e vai in **Console**.
    3. Copia e incolla lo **Step 1**, poi scorri la lista fino in fondo.
    4. Copia e incolla lo **Step 2** per ottenere i link da inserire qui sotto.
    """)
    
    col_a, col_b = st.columns(2)
    
    script_1 = """// Rimuove conflitti con sessioni precedenti
if (window.myInterval) clearInterval(window.myInterval);
window.allProfiles = window.allProfiles || new Set();

window.myInterval = setInterval(() => {
    document.querySelectorAll('a[role="link"]').forEach(a => {
        // Filtra solo i profili utente validi
        if(a.href.includes("instagram.com/") && !a.href.includes("/p/") && !a.href.includes("/reels/") && !a.href.includes("/explore/")) {
            window.allProfiles.add(a.href);
        }
    });
    console.log("📊 Profili in memoria: " + window.allProfiles.size);
}, 500);

console.log("✅ Script avviato! Scorri LENTAMENTE la lista. Quando hai finito, usa il secondo comando.");"""

    script_2 = """clearInterval(window.myInterval);
if (window.allProfiles && window.allProfiles.size > 0) {
    copy([...window.allProfiles].join('\n'));
    console.log("✅ " + window.allProfiles.size + " link copiati! Incollali nell'app.");
    // Svuota la memoria per il prossimo post
    window.allProfiles = new Set();
} else {
    console.error("❌ Errore: Nessun profilo catturato.");
}"""

    with col_a:
        st.code(script_1, language="javascript")
        if st.button("Copia Step 1 📋"):
            st.write('<script>navigator.clipboard.writeText(`' + script_1 + '`)</script>', unsafe_allow_html=True)
            st.success("Copiato! Incollalo in console.")

    with col_b:
        st.code(script_2, language="javascript")
        if st.button("Copia Step 2 📋"):
            st.write('<script>navigator.clipboard.writeText(`' + script_2 + '`)</script>', unsafe_allow_html=True)
            st.success("Copiato! Incollalo per copiare i link.")

# --- SIDEBAR ---
st.sidebar.title("Configurazione Files")
fol_file = st.sidebar.file_uploader("1. Carica followers_1.json", type="json")
fng_file = st.sidebar.file_uploader("2. Carica following.json (Opzionale)", type="json")

# --- LOGICA PRINCIPALE ---
if fol_file:
    # Caricamento Followers
    fol_data = json.load(fol_file)
    followers_info = {}
    for item in fol_data:
        u = clean_username(item['string_list_data'][0]['value'])
        if u:
            followers_info[u] = item['string_list_data'][0]['timestamp']
    
    # Caricamento Following
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

    # Input Like
    st.divider()
    st.subheader("Analisi Interazioni")
    manual_input = st.text_area("Incolla qui i link (Step 2):", height=150)
    
    like_counts = {}
    if manual_input:
        lines = manual_input.splitlines()
        unique_users_in_input = {clean_username(line) for line in lines if clean_username(line)}
        for u in unique_users_in_input:
            if u:
                like_counts[u] = like_counts.get(u, 0) + 1

    # Metriche
    follower_attivi = [u for u in followers_info if like_counts.get(u, 0) > 0]
    ghost_follower = [u for u in followers_info if like_counts.get(u, 0) == 0]

    st.divider()
    m1, m2, m3 = st.columns(3)
    m1.metric("Followers Totali", len(followers_info))
    m2.metric("Follower Attivi", len(follower_attivi))
    m3.metric("Ghost Follower", len(ghost_follower))

    # Tabella
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
    if has_following:
        cols_to_show.append("Lo segui?")
    cols_to_show.extend(["Data Follow", "Profilo"])
    
    st.subheader("Classifica Dettagliata")
    st.dataframe(df[cols_to_show], column_config={"Profilo": st.column_config.LinkColumn("Link")}, use_container_width=True, hide_index=True)

    if has_following:
        not_following_back = [user for user in following_list if user not in followers_info]
        with st.expander(f"🚫 Chi non ti ricambia ({len(not_following_back)})"):
            for user in sorted(not_following_back):
                st.markdown(f"- [@{user}](https://www.instagram.com/{user}/)")
else:
    st.info("👈 Carica il file followers_1.json per iniziare.")
