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

# --- ESPORTAZIONE UNIFICATA OTTIMIZZATA PER MOBILE ---
def generate_unified_html(df_full, unfollowers):
    now = datetime.now().strftime("%d/%m/%Y %H:%M")
    
    # Prepariamo i dati: creiamo la colonna con lo username cliccabile
    df_export = df_full.copy()
    df_export['Username'] = df_export.apply(
        lambda row: f'<a class="user-link" href="{row["Profilo"]}" target="_blank">@{row["Username"]}</a>', 
        axis=1
    )
    
    # Rimuoviamo le colonne ridondanti o tecniche
    df_export = df_export.drop(columns=['Timestamp', 'Profilo'], errors='ignore')
    
    # Riordiniamo le colonne per mettere lo Username all'inizio
    cols = ['Username'] + [c for c in df_export.columns if c != 'Username']
    df_export = df_export[cols]
    
    table_html = df_export.to_html(index=False, escape=False, render_links=True, classes='main-table')

    html = f"""
    <html>
    <head>
        <meta charset='UTF-8'>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{ 
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; 
                margin: 0; padding: 20px; background-color: #fafafa; color: #262626;
            }}
            .container {{ max-width: 800px; margin: auto; }}
            header {{ border-bottom: 1px solid #dbdbdb; margin-bottom: 20px; padding-bottom: 10px; }}
            h1 {{ font-weight: 300; font-size: 1.8rem; margin: 0; }}
            h2 {{ font-size: 1.1rem; margin-top: 30px; display: flex; align-items: center; justify-content: space-between; }}
            .status-tag {{ font-size: 0.75rem; background: #e0e0e0; padding: 3px 10px; border-radius: 15px; font-weight: normal; }}
            
            /* Tabella Scorrevole */
            .table-wrapper {{ 
                max-height: 500px; overflow-y: auto; background: white;
                border: 1px solid #dbdbdb; border-radius: 8px;
            }}
            .main-table {{ border-collapse: collapse; width: 100%; font-size: 0.95rem; }}
            .main-table th {{ 
                background-color: #ffffff; position: sticky; top: 0; z-index: 10; 
                padding: 12px; border-bottom: 2px solid #dbdbdb; text-align: left;
            }}
            .main-table td {{ padding: 12px; border-bottom: 1px solid #f0f0f0; }}
            
            /* Link Username Cliccabile */
            .user-link {{ 
                color: #0095f6 !important; 
                text-decoration: none; 
                font-weight: 600;
                display: block; /* Aumenta l'area cliccabile su mobile */
            }}
            
            /* Sezione Non Ricambiano */
            .unfollow-section {{ 
                background: white; border: 1px solid #dbdbdb; border-radius: 8px; padding: 15px;
            }}
            .unfollow-item {{ 
                display: inline-block; padding: 8px 12px; margin: 4px;
                background: #fdfdfd; border: 1px solid #efefef; border-radius: 6px;
            }}
            .unfollow-item a {{ color: #262626; text-decoration: none; font-size: 0.9rem; }}
            
            .meta-info {{ color: #8e8e8e; font-size: 0.8rem; }}
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <h1>Instagram Report</h1>
                <p class="meta-info">Generato il: {now}</p>
            </header>

            <h2>📊 Classifica Followers <span class="status-tag">{len(df_export)} totali</span></h2>
            <div class="table-wrapper">
                {table_html}
            </div>

            <h2>🚫 Non Ricambiano <span class="status-tag">{len(unfollowers)} utenti</span></h2>
            <div class="unfollow-section">
    """
    for u in sorted(unfollowers):
        html += f"""
            <div class="unfollow-item">
                <a href="https://www.instagram.com/{u}/" target="_blank"><strong>@{u}</strong></a>
            </div>
        """
    
    html += """
            </div>
            <footer style="margin-top: 40px; text-align: center; color: #dbdbdb; font-size: 0.7rem;">
                Creato con Instagram Ghost Finder
            </footer>
        </div>
    </body>
    </html>
    """
    return html

st.divider()
if st.button("Genera File Report Unificato 📄", use_container_width=True):
    full_html = generate_unified_html(df, not_following_back)
    st.download_button(
        label="Scarica Report Completo (HTML)",
        data=full_html,
        file_name="report_instagram.html",
        mime="text/html",
        use_container_width=True
    )