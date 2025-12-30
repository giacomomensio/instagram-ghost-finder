import streamlit as st
import pandas as pd
import json
import re
from datetime import datetime
import streamlit.components.v1 as components

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

# --- SECTION: INSTRUCTIONS ---
with st.expander("🚀 Smart Bookmarks Setup", expanded=False):
    st.markdown("""
    To capture "Likes" and profile links directly from Instagram, use these two smart bookmarks. They work on both Desktop and Mobile browsers.
    """)
    
    tab1, tab2 = st.tabs(["🖥️ Option A: Desktop (Drag & Drop)", "📱 Option B: Mobile (Manual)"])
    
    # Codici JavaScript forniti dall'utente
    js_start = """javascript:(function(){window.allProfiles=window.allProfiles||new Set();window.myInterval=setInterval(()=>{document.querySelectorAll('a[role="link"]').forEach(a=>{if(a.href.includes("instagram.com/")&&!a.href.includes("/p/")&&!a.href.includes("/reels/")&&!a.href.includes("/explore/")){window.allProfiles.add(a.href)}});console.log("📊 Profili in memoria: "+window.allProfiles.size)},500);console.log("✅ Script avviato! Scorri la lista.");})();"""
    js_copy = """javascript:(function(){     clearInterval(window.myInterval);     if(window.allProfiles && window.allProfiles.size > 0){          const t = [...window.allProfiles].join('\\n');                  /* 1. Tentativo di copia silente (Default) */         const el = document.createElement('textarea');         el.value = t;         el.style.position = 'fixed';         el.style.left = '-9999px';         document.body.appendChild(el);         el.select();         el.setSelectionRange(0, 99999);         const successful = document.execCommand('copy');         document.body.removeChild(el);          if(successful) {             /* Funziona su Chrome/Desktop: mostriamo solo l'alert classico */             alert("%E2%9C%85 " + window.allProfiles.size + " link copiati!");             window.allProfiles = new Set();         } else {             /* 2. Fallback: Pannello grafico solo se la copia fallisce (Firefox Mobile) */             const div = document.createElement('div');             div.style = "position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.9);z-index:999999;display:flex;flex-direction:column;align-items:center;justify-content:center;padding:20px;box-sizing:border-box;font-family:sans-serif;";                          const area = document.createElement('textarea');             area.value = t;             area.style = "width:100%;max-width:500px;height:300px;padding:10px;border-radius:8px;font-size:14px;border:none;";                          const btnCopy = document.createElement('button');             btnCopy.innerText = "%F0%9F%93%8B COPIA TUTTO";             btnCopy.style = "width:100%;max-width:500px;margin-top:15px;padding:15px;background:#0095f6;color:white;border:none;border-radius:8px;font-weight:bold;";                            btnCopy.onclick = function() {                   area.select();                   area.setSelectionRange(0, 99999);                   if(document.execCommand('copy')) {                       btnCopy.innerText = "%E2%9C%85 COPIATO!";                       btnCopy.style.background = "#00de7a";                       window.allProfiles = new Set();                       setTimeout(() => { document.body.removeChild(div); }, 700);                   }             };             const btnClose = document.createElement('button');             btnClose.innerText = "CHIUDI";             btnClose.style = "margin-top:15px;background:transparent;color:white;border:none;text-decoration:underline;";             btnClose.onclick = function() { document.body.removeChild(div); };              div.appendChild(area);             div.appendChild(btnCopy);             div.appendChild(btnClose);             document.body.appendChild(div);         }      } else {          alert("%E2%9D%8C Nessun profilo catturato.");      } })();"""

    with tab1:
        st.markdown("""
        #### **Setup**
        1. Ensure your browser's **Bookmarks Bar** is visible (`Ctrl+Shift+B`).
        2. **Triple-click** to select the entire code below.
        3. **Drag and drop** the highlighted text directly onto your Bookmarks Bar.
        4. Rename the bookmarks to `++1 START` and `++2 COPY`.
        
        #### **How to use**
        1. Open Instagram on your PC and go to a **Likes list**.
        2. Click **`++1 START`** in your bar.
        3. Scroll the list to the end.
        4. Click **`++2 COPY`** and paste the links in the box below.
        """)
        st.info("💡 **Tip:** Look for the small **copy icon** that appears in the top-right of the boxes below when you hover or tap.")
        st.write("**Code for START:**")
        st.code(js_start, language="javascript")
        st.write("**Code for COPY:**")
        st.code(js_copy, language="javascript")

    with tab2:
        st.markdown("""
        #### **Setup**
        1. **Tap the icon** in the top-right of the code box below to copy.
        2. **Create a bookmark** for any page in your mobile browser.
        3. Open your **Bookmarks** menu and **Edit** the bookmark.
        4. Change the **Name** to `++1 START` and **Paste** the code into the **URL** (Address) field.
        5. Repeat the process for `++2 COPY`.
        
        #### **How to use (The "++" Trick)**
        1. Open Instagram and go to a **Likes list**.
        2. Tap the **Address Bar** and type **`++`**.
        3. Select **`++1 START`**, then scroll the list.
        4. When done, type **`++`** again and select **`++2 COPY`**.
        """)
        st.info("💡 **Tip:** Look for the small **copy icon** that appears in the top-right of the boxes below when you hover or tap.")
        st.write("**URL for ++1 START:**")
        st.code(js_start, language="javascript")
        st.write("**URL for ++2 COPY:**")
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

# --- ESPORTAZIONE UNIFICATA OTTIMIZZATA PER MOBILE (CON FIX CRASH) ---
def generate_unified_html(df_full, unfollowers=None):
    now = datetime.now().strftime("%d/%m/%Y %H:%M")
    if unfollowers is None:
        unfollowers = []
    
    # Prepariamo i dati
    df_export = df_full.copy()
    df_export['Username'] = df_export.apply(
        lambda row: f'<a class="user-link" href="{row["Profilo"]}" target="_blank">@{row["Username"]}</a>', 
        axis=1
    )
    
    # Pulizia colonne
    df_export = df_export.drop(columns=['Timestamp', 'Profilo'], errors='ignore')
    cols = ['Username'] + [c for c in df_export.columns if c != 'Username']
    df_export = df_export[cols]
    
    table_html = df_export.to_html(index=False, escape=False, render_links=True, classes='main-table')

    html = f"""
    <html>
    <head>
        <meta charset='UTF-8'>
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <style>
            body {{ 
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; 
                margin: 0; padding: 10px; background-color: #fafafa; color: #262626;
            }}
            .container {{ max-width: 100%; margin: auto; }}
            header {{ border-bottom: 1px solid #dbdbdb; margin-bottom: 15px; padding-bottom: 5px; }}
            h1 {{ font-weight: 300; font-size: 1.2rem; margin: 0; }}
            h2 {{ font-size: 0.95rem; margin: 15px 0 8px 0; }}
            
            .table-wrapper {{ 
                width: 100%; 
                max-height: 380px; 
                overflow-y: auto; 
                overflow-x: hidden; 
                background: white;
                border: 1px solid #dbdbdb; 
                border-radius: 8px;
                -webkit-overflow-scrolling: touch;
            }}
            
            .main-table {{ 
                border-collapse: collapse; 
                width: 100%; 
                font-size: 0.85rem; /* Font leggermente aumentato */
                table-layout: fixed;
            }}
            
            .main-table th {{
                position: sticky; 
                top: 0;
                background: #f8f8f8;
                z-index: 1;
                border-bottom: 2px solid #dbdbdb;
                font-size: 0.75rem;
                text-transform: uppercase;
            }}

            .main-table th, .main-table td {{ 
                padding: 10px 4px; 
                border-bottom: 1px solid #eee; 
                text-align: center;
                vertical-align: middle;
            }}
            
            /* GESTIONE COLONNE */
            /* 1. Username: Più spazio ora che i Like sono stretti */
            .main-table th:nth-child(1), .main-table td:nth-child(1) {{ 
                width: 45%; 
                text-align: left; 
                padding-left: 8px;
            }}
            
            /* 2. Like: Colonna molto stretta */
            .main-table th:nth-child(2), .main-table td:nth-child(2) {{ 
                width: 15%; 
            }}
            
            /* Altre colonne (Data Follow, Lo segui?) */
            .main-table th:nth-of-type(n+3), .main-table td:nth-of-type(n+3) {{ 
                width: 20%; 
                font-size: 0.75rem;
            }}

            .user-link {{ 
                color: #0095f6 !important; 
                text-decoration: none; 
                font-weight: 600;
                display: block; 
                white-space: nowrap; 
                overflow: hidden; 
                text-overflow: ellipsis;
            }}
            
            .unfollow-section {{ 
                background: white; border: 1px solid #dbdbdb; border-radius: 8px; padding: 8px;
            }}
            .unfollow-item {{ 
                display: inline-block; padding: 6px 8px; margin: 2px;
                background: #fdfdfd; border: 1px solid #efefef; border-radius: 4px; 
                font-size: 0.8rem;
            }}
            .unfollow-item a {{ color: #262626; text-decoration: none; font-weight: 500; }}
            .meta-info {{ color: #8e8e8e; font-size: 0.65rem; }}
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <h1>Instagram Report</h1>
                <p class="meta-info">Generato il: {now}</p>
            </header>

            <h2>📊 Classifica ({len(df_export)})</h2>
            <div class="table-wrapper">
                {table_html}
            </div>
    """

    if unfollowers:
        html += f"""
            <h2>🚫 Non Ricambiano ({len(unfollowers)})</h2>
            <div class="unfollow-section">
        """
        for u in sorted(unfollowers):
            html += f"""
                <div class="unfollow-item">
                    <a href="https://www.instagram.com/{u}/" target="_blank">@{u}</a>
                </div>
            """
        html += "</div>"
    
    html += """
        </div>
    </body>
    </html>
    """
    return html

# --- SEZIONE PULSANTE (UPDATE) ---
st.divider()
if st.button("Genera File Report Unificato 📄", use_container_width=True):
    # Passiamo la lista solo se esiste, altrimenti passiamo None o lista vuota
    lista_unfollowers = not_following_back if has_following else []
    full_html = generate_unified_html(df, lista_unfollowers)
    
    st.download_button(
        label="Scarica Report Completo (HTML)",
        data=full_html,
        file_name="report_instagram.html",
        mime="text/html",
        use_container_width=True
    )

# --- FINAL LINE OF APP.PY ---
components.html(
    """
    <script>
    const styleButtons = () => {
        const mainDoc = window.parent.document;
        const copyButtons = mainDoc.querySelectorAll('button[title="Copy to clipboard"]');
        
        copyButtons.forEach(btn => {
            // 1. Style the button directly (natural position)
            btn.style.opacity = "1";
            btn.style.visibility = "visible";
            btn.style.display = "flex";
            btn.style.alignItems = "center";
            btn.style.justifyContent = "center";
            
            // 2. Background and Border
            btn.style.backgroundColor = "#d1d5db"; // Darker grey
            btn.style.border = "1px solid #9ca3af";
            btn.style.borderRadius = "4px";
            
            // 3. Fixed size to keep it neat
            btn.style.width = "32px";
            btn.style.height = "32px";
            
            // 4. Inject static icon if missing
            if (!btn.querySelector('.custom-copy-icon')) {
                // Remove any existing SVG first to avoid overlap
                const existingSvg = btn.querySelector('svg');
                if (existingSvg) existingSvg.style.display = 'none';

                const iconSvg = `
                    <svg class="custom-copy-icon" viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="#1f2937" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="pointer-events: none;">
                        <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                        <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
                    </svg>
                `;
                btn.innerHTML = iconSvg;
            }
        });
    };

    setInterval(styleButtons, 1000);
    </script>
    """,
    height=0,
)