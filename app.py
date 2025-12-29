import streamlit as st
import pandas as pd
import json
import re
from datetime import datetime

# Configurazione Pagina
st.set_page_config(page_title="Instagram Ghost Finder", layout="wide")

def clean_username(url):
    """Estrae lo username da link profili o stringhe semplici."""
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

# --- 1. CARICAMENTO FOLLOWERS (SIDEBAR) ---
fol_file = st.sidebar.file_uploader("1. Carica followers_1.json", type="json")

# --- 2. CARICAMENTO INTERAZIONI ---
st.subheader("2. Carica le Interazioni (Like)")
col_a, col_b = st.columns(2)

with col_a:
    csv_files = st.file_uploader("Trascina i CSV qui (opzionale)", type="csv", accept_multiple_files=True)

with col_b:
    manual_input = st.text_area("Incolla i link dalla Console (uno per riga):", 
                               placeholder="Incolla qui i link ottenuti con lo script JS...", 
                               height=150)

# --- LOGICA DI ELABORAZIONE ---
if fol_file:
    try:
        fol_data = json.load(fol_file)
        followers_info = {item['string_list_data'][0]['value']: item['string_list_data'][0]['timestamp'] for item in fol_data}
    except Exception as e:
        st.error(f"Errore JSON: {e}")
        st.stop()

    like_counts = {}
    
    # Processa CSV
    if csv_files:
        for uploaded_csv in csv_files:
            df = pd.read_csv(uploaded_csv)
            if 'Link' in df.columns:
                users_in_post = {clean_username(l) for l in df['Link'] if clean_username(l)}
                for u in users_in_post:
                    like_counts[u] = like_counts.get(u, 0) + 1

    # Processa Input Manuale
    if manual_input:
        lines = manual_input.splitlines()
        users_manual = {clean_username(line) for line in lines if clean_username(line)}
        for u in users_manual:
            like_counts[u] = like_counts.get(u, 0) + 1

    # CREAZIONE RISULTATI
    all_users = set(followers_info.keys()).union(set(like_counts.keys()))
    results = []

    for user in all_users:
        likes = like_counts.get(user, 0)
        follow_time = followers_info.get(user)
        
        results.append({
            "Username": user,
            "Like Totali": likes,
            "Data Follow": datetime.fromtimestamp(follow_time) if follow_time else None,
            "Timestamp": follow_time if follow_time else 9999999999, # In cima se non follower
            "Profilo": f"https://www.instagram.com/{user}/"
        })

    df_final = pd.DataFrame(results)
    df_final = df_final.sort_values(by=['Like Totali', 'Timestamp'], ascending=[False, False])

    # --- VISUALIZZAZIONE ---
    st.divider()
    m1, m2, m3 = st.columns(3)
    m1.metric("Followers Totali", len(followers_info))
    m2.metric("Utenti Attivi", len([l for l in like_counts.values() if l > 0]))
    m3.metric("Ghost Follower", len([u for u in followers_info if like_counts.get(u, 0) == 0]))

    # Formattazione per la tabella
    df_display = df_final.copy()
    df_display['Data Follow'] = df_display['Data Follow'].dt.strftime('%d/%m/%Y').fillna("-")
    
    st.dataframe(
        df_display[["Username", "Like Totali", "Data Follow", "Profilo"]],
        column_config={"Profilo": st.column_config.LinkColumn("Profilo Instagram")},
        use_container_width=True,
        hide_index=True
    )

    csv_out = df_final.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Scarica Report CSV", csv_out, "analisi_follower.csv", "text/csv")
else:
    st.warning("👈 Carica il file followers_1.json nella barra laterale per iniziare.")