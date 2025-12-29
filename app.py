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
    blacklist = ['about', 'developers', 'help', 'legal', 'explore', 'reels', 'direct', 'accounts', 'p', 'stories', 'blog', 'meta', 'privacy']
    if user and user not in blacklist and user != "giacomomensio":
        if not user.endswith(('.com', '.net', '.it')):
            return user
    return None

st.title("🕵️‍♂️ Instagram Ghost Finder & Ranker")
st.caption("Versione 2.1 - Analisi Interazioni e Unfollowers")

# --- SIDEBAR: CARICAMENTO FILE ---
st.sidebar.title("Configurazione")
fol_file = st.sidebar.file_uploader("1. Carica followers_1.json", type="json")
fng_file = st.sidebar.file_uploader("2. Carica following.json (Opzionale)", type="json")

# --- MAIN: CARICAMENTO INTERAZIONI ---
st.subheader("Carica le Interazioni (Like)")
col_a, col_b = st.columns(2)
with col_a:
    csv_files = st.file_uploader("Trascina i CSV qui", type="csv", accept_multiple_files=True)
with col_b:
    manual_input = st.text_area("Incolla i link dalla Console:", placeholder="Incolla i link qui...", height=150)

# --- LOGICA DI ELABORAZIONE ---
if fol_file:
    # 1. Processa Followers
    fol_data = json.load(fol_file)
    followers_info = {item['string_list_data'][0]['value']: item['string_list_data'][0]['timestamp'] for item in fol_data}
    
    # 2. Processa Following (se presente)
    following_list = []
    if fng_file:
        fng_data = json.load(fng_file)
        # Instagram a volte incapsula following in una chiave 'relationships_following'
        actual_fng = fng_data.get('relationships_following', fng_data)
        following_list = [item['string_list_data'][0]['value'] for item in actual_fng]

    # 3. Conta Like
    like_counts = {}
    if csv_files:
        for f in csv_files:
            df = pd.read_csv(f)
            if 'Link' in df.columns:
                for u in {clean_username(l) for l in df['Link'] if clean_username(l)}:
                    like_counts[u] = like_counts.get(u, 0) + 1
    if manual_input:
        for u in {clean_username(line) for line in manual_input.splitlines() if clean_username(line)}:
            like_counts[u] = like_counts.get(u, 0) + 1

    # 4. Unfollowers (Chi segui ma non ti segue)
    not_following_back = [user for user in following_list if user not in followers_info]

    # --- VISUALIZZAZIONE ---
    st.divider()
    
    # Sezione Unfollowers
    if fng_file:
        with st.expander(f"🚫 Chi non ti ricambia il follow ({len(not_following_back)})", expanded=False):
            if not_following_back:
                st.write("Questi utenti non compaiono nella tua lista follower:")
                for user in sorted(not_following_back):
                    st.markdown(f"- [{user}](https://www.instagram.com/{user}/)")
            else:
                st.success("Grande! Tutti quelli che segui ti ricambiano il follow.")

    # Metriche classiche
    m1, m2, m3 = st.columns(3)
    m1.metric("Followers Totali", len(followers_info))
    m2.metric("Utenti Attivi", len([l for l in like_counts.values() if l > 0]))
    m3.metric("Ghost Follower", len([u for u in followers_info if like_counts.get(u, 0) == 0]))

    # Tabella Principale
    all_users = set(followers_info.keys()).union(set(like_counts.keys()))
    results = []
    for user in all_users:
        likes = like_counts.get(user, 0)
        follow_time = followers_info.get(user)
        results.append({
            "Username": user,
            "Like Totali": likes,
            "Data Follow": datetime.fromtimestamp(follow_time) if follow_time else None,
            "Timestamp": follow_time if follow_time else 9999999999,
            "Profilo": f"https://www.instagram.com/{user}/"
        })

    df_final = pd.DataFrame(results).sort_values(by=['Like Totali', 'Timestamp'], ascending=[False, False])
    df_display = df_final.copy()
    df_display['Data Follow'] = df_display['Data Follow'].dt.strftime('%d/%m/%Y').fillna("-")
    
    st.subheader("Classifica Attività")
    st.dataframe(
        df_display[["Username", "Like Totali", "Data Follow", "Profilo"]],
        column_config={"Profilo": st.column_config.LinkColumn("Profilo Instagram")},
        use_container_width=True, hide_index=True
    )
else:
    st.warning("👈 Carica i file JSON nella barra laterale per iniziare.")