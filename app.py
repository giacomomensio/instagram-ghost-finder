import streamlit as st
import pandas as pd
import json
import re
from datetime import datetime

st.set_page_config(page_title="Instagram Ghost Finder", layout="wide")

# Funzione di pulizia username (Quella che funzionava)
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

# --- BOX ISTRUZIONI (Testo semplice, nessuna funzione che rompe il codice) ---
with st.expander("📄 Copia gli Script per la Console qui"):
    st.subheader("Step 1: Avvia e Scorri")
    st.code("""
var allProfiles = allProfiles || new Set(); 
if (window.myInterval) clearInterval(window.myInterval);
window.myInterval = setInterval(() => {
    document.querySelectorAll('a[role="link"]').forEach(a => {
        if(a.href.includes("instagram.com/") && !a.href.includes("/p/") && !a.href.includes("/reels/")) {
            allProfiles.add(a.href);
        }
    });
    console.log("📊 Profili catturati: " + allProfiles.size);
}, 500);
    """, language="javascript")

    st.subheader("Step 2: Ferma e Copia")
    st.code("""
clearInterval(window.myInterval);
copy([...allProfiles].join('\\n'));
console.log("✅ Copiati: " + allProfiles.size);
allProfiles = new Set();
    """, language="javascript")

# --- SIDEBAR ---
st.sidebar.title("Configurazione")
fol_file = st.sidebar.file_uploader("1. Carica followers_1.json", type="json")
fng_file = st.sidebar.file_uploader("2. Carica following.json (Opzionale)", type="json")

# --- LOGICA DI ANALISI ---
if fol_file:
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
        for entry in fng_data.get('relationships_following', []):
            u = clean_username(entry.get('title')) or clean_username(entry.get('string_list_data', [{}])[0].get('value'))
            if u: following_list.add(u)

    st.divider()
    manual_input = st.text_area("Incolla i link qui:", height=150)
    
    like_counts = {}
    if manual_input:
        for line in manual_input.splitlines():
            u = clean_username(line)
            if u: like_counts[u] = like_counts.get(u, 0) + 1

    # Metriche
    m1, m2, m3 = st.columns(3)
    m1.metric("Followers Totali", len(followers_info))
    m2.metric("Follower Attivi", len([u for u in followers_info if like_counts.get(u, 0) > 0]))
    m3.metric("Ghost Follower", len([u for u in followers_info if like_counts.get(u, 0) == 0]))

    # Tabella Risultati
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

else:
    st.info("👈 Carica il file followers_1.json per iniziare.")