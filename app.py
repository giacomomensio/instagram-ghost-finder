import streamlit as st
import pandas as pd
import json
import re
from datetime import datetime

# Configurazione Pagina
st.set_page_config(page_title="Instagram Ghost Finder", layout="wide")

def clean_username(url):
    """Estrae lo username da link profili, post, o stringhe semplici."""
    url = str(url).strip().lower()
    # Rimuove parametri ? e #
    url = url.split('?')[0].split('#')[0].rstrip('/')
    
    # Cerca il pattern del profilo instagram.com/username
    match = re.search(r"instagram\.com/([^/]+)", url)
    if match:
        user = match.group(1)
    else:
        # Se non è un URL, proviamo a vedere se è uno username pulito
        user = url.replace('@', '')

    # Lista nera di parole di sistema da ignorare
    blacklist = [
        'about', 'developers', 'help', 'legal', 'explore', 'reels', 
        'direct', 'accounts', 'p', 'stories', 'blog', 'meta', 'privacy'
    ]
    
    if user and user not in blacklist and user != "giacomomensio":
        # Se lo user contiene un punto alla fine o è un dominio lo scartiamo
        if not user.endswith(('.com', '.net', '.it')):
            return user
    return None

st.title("🕵️‍♂️ Instagram Ghost Finder & Ranker")
st.sidebar.title("Configurazione")
st.sidebar.info("Carica i dati estratti da Instagram per analizzare chi ti segue ma non interagisce.")

# --- 1. CARICAMENTO FOLLOWERS (JSON) ---
fol_file = st.sidebar.file_uploader("1. Carica followers_1.json", type="json")

# --- 2. CARICAMENTO INTERAZIONI ---
st.subheader("2. Carica le Interazioni (Like)")
col_a, col_b = st.columns(2)

with col_a:
    csv_files = st.file_uploader("Trascina i CSV qui (opzionale)", type="csv", accept_multiple_files=True)

with col_b:
    manual_input = st.text_area("Oppure incolla i link dalla Console (uno per riga):", 
                               placeholder="Incolla qui i link ottenuti con lo script JS...", 
                               height=150)

# --- LOGICA DI ELABORAZIONE ---
if fol_file:
    # Elaborazione Followers
    try:
        fol_data = json.load(fol_file)
        followers_info = {}
        for item in fol_data:
            username = item['string_list_data'][0]['value']
            timestamp = item['string_list_data'][0]['timestamp']
            followers_info[username] = timestamp
    except Exception as e:
        st.error(f"Errore nella lettura del file JSON: {e}")
        st.stop()

    # Elaborazione Interazioni (Like)
    like_counts = {}
    
    # A. Processa CSV
    if csv_files:
        for uploaded_csv in csv_files:
            df = pd.read_csv(uploaded_csv)
            if 'Link' in df.columns:
                users_in_post = {clean_username(l) for l in df['Link'] if clean_username(l)}
                for u in users_in_post:
                    like_counts[u] = like_counts.get(u, 0) + 1

    # B. Processa Input Manuale
    if manual_input:
        # Consideriamo ogni blocco di testo incollato come riferito a post diversi? 
        # Per semplicità ora contiamo i like totali unici incollati.
        lines = manual_input.splitlines()
        users_manual = {clean_username(line) for line in lines if clean_username(line)}
        for u in users_manual:
            like_counts[u] = like_counts.get(u, 0) + 1

    # Creazione Risultati
    if followers_info:
        results = []
        for user, follow_time in followers_info.items():
            likes = like_counts.get(user, 0)
            results.append({
                "Username": user,
                "Profilo": f"https://www.instagram.com/{user}/",
                "Like Totali": likes,
                "Data Follow": datetime.fromtimestamp(follow_time),
                "Timestamp": follow_time
            })

        df_final = pd.DataFrame(results)
        # Ordinamento: più Like, poi più Recenti (Timestamp alto)
        df_final = df_final.sort_values(by=['Like Totali', 'Timestamp'], ascending=[False, False])

        # --- VISUALIZZAZIONE ---
        st.divider()
        m1, m2, m3 = st.columns(3)
        m1.metric("Followers Totali", len(followers_info))
        m2.metric("Attivi (almeno 1 like)", len([l for l in like_counts.values() if l > 0]))
        m3.metric("Ghost (0 like)", len(df_final[df_final["Like Totali"] == 0]))

        st.subheader("Classifica Attività")
        st.dataframe(
            df_final[["Username", "Like Totali", "Data Follow", "Profilo"]],
            column_config={"Profilo": st.column_config.LinkColumn("Link Profilo")},
            use_container_width=True,
            hide_index=True
        )

        # Download
        csv_out = df_final.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Scarica Report Completo CSV", csv_out, "analisi_follower.csv", "text/csv")
else:
    st.warning("👈 Carica il file followers_1.json nella barra laterale per iniziare.")