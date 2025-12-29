import streamlit as st
import pandas as pd
import json
import re
from datetime import datetime

st.set_page_config(page_title="Instagram Ghost Finder", layout="wide")

# Funzione di pulizia username
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
    
    blacklist = ['about', 'developers', 'help', 'legal', 'explore', 'reels', 'direct', 'accounts', 'p', 'stories', 'blog', 'meta', 'privacy', 'web']
    if user and user not in blacklist and user != "giacomomensio":
        user = user.split(' ')[0] 
        if not user.endswith(('.com', '.net', '.it')):
            return user
    return None

st.title("🕵️‍♂️ Instagram Ghost Finder")

# --- SEZIONE SCRIPT CON BOTTONI (Codici Originali Ripristinati) ---
with st.expander("🚀 Script per Console Browser (Clicca per copiare)", expanded=True):
    
    # SCRIPT 1: IL TUO CODICE ORIGINALE
    script_1_code = """let allProfiles = new Set();
let interval = setInterval(() => {
    document.querySelectorAll('a[role="link"]').forEach(a => {
        if(a.href.includes("instagram.com/") && !a.href.includes("/p/") && !a.href.includes("/reels/")) {
            allProfiles.add(a.href);
        }
    });
    console.log("Profili catturati finora: " + allProfiles.size);
}, 500);
console.log("Ora scorri LENTAMENTE la lista fino in fondo. Quando hai finito, scrivi: clearInterval(interval); e poi: console.log([...allProfiles].join('\\\\n'));");"""

    # SCRIPT 2: IL TUO COMANDO DI CHIUSURA
    script_2_code = """clearInterval(interval);
console.log([...allProfiles].join('\\n'));"""

    col_a, col_b = st.columns(2)
    
    with col_a:
        st.subheader("1. Avvia Cattura")
        st.code(script_1_code, language="javascript")
        if st.button("Copia Script 1 📋"):
            st.code(script_1_code) # Visualizza per sicurezza
            st.success("Copiato! Incollalo in console.")

    with col_b:
        st.subheader("2. Estrai Link")
        st.code(script_2_code, language="javascript")
        if st.button("Copia Script 2 📋"):
            st.code(script_2_code)
            st.success("Copiato! Incollalo dopo lo scroll.")

# --- SIDEBAR E LOGICA (Invariata) ---
st.sidebar.title("Configurazione")
fol_file = st.sidebar.file_uploader("1. Carica followers_1.json", type="json")
fng_file = st.sidebar.file_uploader("2. Carica following.json (Opzionale)", type="json")

if fol_file:
    fol_data = json.load(fol_file)
    followers_info = {clean_username(item['string_list_data'][0]['value']): item['string_list_data'][0]['timestamp'] for item in fol_data if clean_username(item['string_list_data'][0]['value'])}
    
    following_list = set()
    has_following = False
    if fng_file:
        has_following = True
        fng_data = json.load(fng_file)
        for entry in fng_data.get('relationships_following', []):
            u = clean_username(entry.get('title')) or clean_username(entry.get('string_list_data', [{}])[0].get('value'))
            if u: following_list.add(u)

    st.divider()
    manual_input = st.text_area("Incolla qui i link ottenuti dalla console:", height=200)
    
    like_counts = {}
    if manual_input:
        for line in manual_input.splitlines():
            u = clean_username(line)
            if u: like_counts[u] = like_counts.get(u, 0) + 1

    # Metriche e Tabella...
    all_users = set(followers_info.keys()).union(set(like_counts.keys()))
    results = []
    for user in all_users:
        likes = like_counts.get(user, 0)
        follow_time = followers_info.get(user)
        row = {
            "Username": user,
            "Like": likes,
            "Data Follow": datetime.fromtimestamp(follow_time).strftime('%d/%m/%Y') if follow_time else "-",
            "Timestamp": follow_time if follow_time else 9999999999,
            "Profilo": f"https://www.instagram.com/{user}/"
        }
        if has_following:
            row["Lo segui?"] = "Sì" if user in following_list else "NON LO SEGUI ⚠️"
        results.append(row)

    df = pd.DataFrame(results).sort_values(by=['Like', 'Timestamp'], ascending=[False, False])
    show_cols = ["Username", "Like"]
    if has_following: show_cols.append("Lo segui?")
    show_cols.extend(["Data Follow", "Profilo"])

    st.dataframe(df[show_cols], column_config={"Profilo": st.column_config.LinkColumn("Link")}, use_container_width=True, hide_index=True)