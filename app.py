import streamlit as st
import pandas as pd
import json
import re
from datetime import datetime

def clean_username(url):
    url = str(url).split('?')[0].rstrip('/')
    match = re.search(r"instagram\.com/([^/]+)", url)
    if match:
        user = match.group(1)
        blacklist = ['about', 'developers', 'help', 'legal', 'explore', 'reels', 'direct', 'accounts']
        if user not in blacklist:
            return user
    return None

st.set_page_config(page_title="InstaRanker", layout="wide")
st.title("📊 Analisi Avanzata Follower")

# Caricamento file
fol_file = st.sidebar.file_uploader("1. Carica followers_1.json", type="json")
csv_files = st.sidebar.file_uploader("2. Carica i CSV dei Like (anche multipli)", type="csv", accept_multiple_files=True)

if fol_file and csv_files:
    # --- 1. Elaborazione Followers (JSON) ---
    fol_data = json.load(fol_file)
    # Creiamo un dizionario {username: data_di_follow}
    followers_info = {}
    for item in fol_data:
        username = item['string_list_data'][0]['value']
        timestamp = item['string_list_data'][0]['timestamp']
        followers_info[username] = timestamp

    # --- 2. Conteggio Like (CSV) ---
    like_counts = {}
    for uploaded_csv in csv_files:
        df = pd.read_csv(uploaded_csv)
        if 'Link' in df.columns:
            # Troviamo utenti unici per QUESTO post (un utente non può mettere 2 like allo stesso post)
            users_in_this_post = set()
            for link in df['Link']:
                user = clean_username(link)
                if user:
                    users_in_this_post.add(user)
            
            # Aggiorniamo il conteggio totale
            for user in users_in_this_post:
                like_counts[user] = like_counts.get(user, 0) + 1

    # --- 3. Unione e Ordinamento ---
    results = []
    for user, follow_time in followers_info.items():
        likes = like_counts.get(user, 0)
        results.append({
            "Username": user,
            "Link": f"https://www.instagram.com/{user}/",
            "Like Totali": likes,
            "Data Follow": datetime.fromtimestamp(follow_time),
            "Timestamp": follow_time # Ci serve per l'ordinamento numerico
        })

    # Trasformiamo in DataFrame per ordinare facilmente
    df_final = pd.DataFrame(results)
    
    # REGOLA: Like decrescenti, poi Timestamp decrescente (più grande = più recente)
    df_final = df_final.sort_values(by=['Like Totali', 'Timestamp'], ascending=[False, False])

    # --- 4. Visualizzazione ---
    st.subheader("Classifica Follower (dai più attivi ai Ghost)")
    
    # Formattazione per rendere i link cliccabili in Streamlit
    st.dataframe(
        df_final[["Username", "Like Totali", "Data Follow", "Link"]],
        column_config={
            "Link": st.column_config.LinkColumn("Profilo Instagram")
        },
        use_container_width=True,
        hide_index=True
    )

    # Download dei risultati
    csv_out = df_final.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Scarica Report Completo", csv_out, "analisi_follower.csv", "text/csv")