import streamlit as st
import pandas as pd
import json
import re
from datetime import datetime

st.set_page_config(page_title="Instagram Ghost Finder", layout="wide")

def clean_username(url):
    url = str(url).strip().lower()
    url = url.split('?')[0].split('#')[0].rstrip('/')
    match = re.search(r"instagram\.com/([^/]+)", url)
    if match:
        user = match.group(1)
    else:
        user = url.replace('@', '')
    
    blacklist = [
        'about', 'developers', 'help', 'legal', 'explore', 'reels', 
        'direct', 'accounts', 'p', 'stories', 'blog', 'meta', 'privacy', 'web'
    ]
    
    if user and user not in blacklist and user != "giacomomensio":
        if not user.endswith(('.com', '.net', '.it')):
            return user
    return None

st.title("🕵️‍♂️ Instagram Ghost Finder & Ranker")
st.caption("Versione 2.7 - Colonna 'Lo segui' condizionale")

# --- SIDEBAR ---
st.sidebar.title("Configurazione")
fol_file = st.sidebar.file_uploader("1. Carica followers_1.json", type="json")
fng_file = st.sidebar.file_uploader("2. Carica following.json (Opzionale)", type="json")

# --- LOGICA PRINCIPALE ---
if fol_file:
    # 1. Carica Followers
    fol_data = json.load(fol_file)
    followers_info = {item['string_list_data'][0]['value']: item['string_list_data'][0]['timestamp'] for item in fol_data}
    
    # 2. Carica Following (solo se il file esiste)
    following_list = set()
    has_following = False
    if fng_file:
        has_following = True
        fng_data = json.load(fng_file)
        raw_fng = fng_data.get('relationships_following', [])
        for entry in raw_fng:
            if 'string_list_data' in entry and entry['string_list_data']:
                user_val = entry['string_list_data'][0].get('value')
                if user_val:
                    following_list.add(user_val)

    # --- SEZIONE INPUT LIKE ---
    st.divider()
    st.subheader("Analisi Interazioni")
    manual_input = st.text_area("Incolla qui i link ottenuti dalla console (uno per riga):", height=200)
    
    like_counts = {}
    if manual_input:
        lines = manual_input.splitlines()
        unique_users_in_input = {clean_username(line) for line in lines if clean_username(line)}
        for u in unique_users_in_input:
            like_counts[u] = like_counts.get(u, 0) + 1

    # --- CALCOLO METRICHE ---
    follower_attivi = [u for u in followers_info if like_counts.get(u, 0) > 0]
    ghost_follower = [u for u in followers_info if like_counts.get(u, 0) == 0]

    st.divider()
    m1, m2, m3 = st.columns(3)
    m1.metric("Followers Totali", len(followers_info))
    m2.metric("Follower Attivi", len(follower_attivi))
    m3.metric("Ghost Follower", len(ghost_follower))

    # --- PREPARAZIONE DATI TABELLA ---
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
        
        # Aggiungiamo l'informazione sul ricambio solo se abbiamo caricato il file
        if has_following:
            row["Lo segui?"] = "Sì" if user in following_list else "NON LO SEGUI ⚠️"
            
        results.append(row)

    df = pd.DataFrame(results).sort_values(by=['Like', 'Timestamp'], ascending=[False, False])
    df['Data Follow'] = df['Data Follow'].dt.strftime('%d/%m/%Y').fillna("-")
    
    # Definiamo le colonne da mostrare dinamicamente
    cols_to_show = ["Username", "Like"]
    if has_following:
        cols_to_show.append("Lo segui?")
    cols_to_show.extend(["Data Follow", "Profilo"])
    
    st.subheader("Classifica Dettagliata")
    st.dataframe(
        df[cols_to_show],
        column_config={"Profilo": st.column_config.LinkColumn("Link")},
        use_container_width=True, hide_index=True
    )

    # --- SEZIONE UNFOLLOWERS (Solo se file caricato) ---
    if has_following:
        not_following_back = [user for user in following_list if user not in followers_info]
        with st.expander(f"🚫 Chi non ti ricambia il follow ({len(not_following_back)})"):
            for user in sorted(not_following_back):
                st.markdown(f"- [@{user}](https://www.instagram.com/{user}/)")

else:
    st.info("👈 Carica il file followers_1.json nella sidebar per iniziare.")