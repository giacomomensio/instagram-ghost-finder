import streamlit as st
import pandas as pd
import json
import re
from datetime import datetime
import streamlit.components.v1 as components

st.set_page_config(page_title="Instagram Ghost Finder", layout="wide")

# Function to clean usernames
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
st.caption("Version 3.5 - Stability Fix")

# --- SIDEBAR ---
st.sidebar.title("File Configuration")
fol_file = st.sidebar.file_uploader("1. Upload followers_1.json", type="json")
fng_file = st.sidebar.file_uploader("2. Upload following.json (Optional)", type="json")

# --- STARTUP MESSAGE ---
if not fol_file:
    st.info("👈 To begin, upload the 'followers_1.json' file in the sidebar on the left.")
    st.stop() 

# --- SECTION: INSTRUCTIONS ---
with st.expander("🚀 Smart Bookmarks Setup", expanded=False):
    st.markdown("""
    To capture "Likes" and profile links directly from Instagram, use these two smart bookmarks. They work on both Desktop and Mobile browsers.
    """)
    
    tab1, tab2 = st.tabs(["🖥️ Option A: Desktop (Drag & Drop)", "📱 Option B: Mobile (Manual)"])
    
    js_start = """javascript:(function(){window.allProfiles=window.allProfiles||new Set();window.myInterval=setInterval(()=>{document.querySelectorAll('a[role="link"]').forEach(a=>{if(a.href.includes("instagram.com/")&&!a.href.includes("/p/")&&!a.href.includes("/reels/")&&!a.href.includes("/explore/")){window.allProfiles.add(a.href)}});console.log("📊 Profiles in memory: "+window.allProfiles.size)},500);alert("✅ Script started! Scroll the list.");})();"""
    js_copy = """javascript:(function(){clearInterval(window.myInterval);if(window.allProfiles&&window.allProfiles.size>0){const t=[...window.allProfiles].join('\\n');const el=document.createElement('textarea');el.value=t;document.body.appendChild(el);el.select();document.execCommand('copy');document.body.removeChild(el);alert("✅ "+window.allProfiles.size+" links copied!");window.allProfiles=new Set();}else{alert("❌ No profiles captured.");}})();"""

    with tab1:
        st.markdown("#### **Setup**\n1. Triple-click to select code.\n2. Drag to your Bookmark Bar.")
        st.write("**Code for START:**")
        st.code(js_start, language="javascript")
        st.write("**Code for COPY:**")
        st.code(js_copy, language="javascript")

    with tab2:
        st.markdown("#### **Setup**\n1. Copy the code.\n2. Create a bookmark and paste the code in the URL field.")
        st.write("**URL for ++1 START:**")
        st.code(js_start, language="javascript")
        st.write("**URL for ++2 COPY:**")
        st.code(js_copy, language="javascript")

# --- DATA LOGIC ---
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

# --- INTERACTION ANALYSIS ---
st.divider()
st.subheader("Interaction Analysis")

if 'sets_di_like' not in st.session_state:
    st.session_state.sets_di_like = []
if 'input_counter' not in st.session_state:
    st.session_state.input_counter = 0

manual_input = st.text_area("Paste links here:", height=150, key=f"in_{st.session_state.input_counter}")
nome_set_input = st.text_input("Set Title (Optional):", key=f"nm_{st.session_state.input_counter}")

if st.button("Add these Likes ➕", use_container_width=True):
    if manual_input.strip():
        nuovi = {clean_username(l) for l in manual_input.splitlines() if clean_username(l)}
        nuovi.discard(None)
        if nuovi:
            titolo = nome_set_input.strip() or f"Set {len(st.session_state.sets_di_like) + 1} ({len(nuovi)} profiles)"
            st.session_state.sets_di_like.append({'nome': titolo, 'utenti': nuovi})
            st.session_state.input_counter += 1
            st.rerun()

# --- SET VISUALIZATION ---
like_counts = {}
if st.session_state.sets_di_like:
    st.write("### 📦 Uploaded Sets List:")
    sets_visualizzati = list(enumerate(st.session_state.sets_di_like))[::-1]
    for i, data in sets_visualizzati:
        for u in data['utenti']: 
            like_counts[u] = like_counts.get(u, 0) + 1
        c1, c2, c3 = st.columns([3, 2, 0.5])
        c1.info(f"📍 {data['nome']}")
        with c2:
            with st.expander(f"🔍 {len(data['utenti'])} profiles"):
                st.caption(", ".join([f"@{u}" for u in sorted(list(data['utenti']))]))
        if c3.button("🗑️", key=f"del_{i}"):
            st.session_state.sets_di_like.pop(i)
            st.rerun()
    st.divider()

# --- METRICS ---
follower_attivi = [u for u in followers_info if like_counts.get(u, 0) > 0]
ghost_follower = [u for u in followers_info if like_counts.get(u, 0) == 0]

m1, m2, m3, m4 = st.columns(4)
m1.metric("Total Followers", len(followers_info))
m2.metric("Active Followers", len(follower_attivi))
m3.metric("Ghost Followers", len(ghost_follower))
m4.metric("Analyzed Posts", len(st.session_state.sets_di_like))

# --- RANKING ---
all_users = set(followers_info.keys()).union(set(like_counts.keys()))
results = []
for user in all_users:
    row = {
        "Username": user,
        "Likes": like_counts.get(user, 0),
        "Follow Date": datetime.fromtimestamp(followers_info[user]).strftime('%d/%m/%Y') if user in followers_info else "-",
        "Timestamp": followers_info.get(user, 9999999999),
        "Profile": f"https://www.instagram.com/{user}/"
    }
    if has_following: row["Follow Back?"] = "Yes" if user in following_list else "NO ⚠️"
    results.append(row)

df = pd.DataFrame(results).sort_values(by=['Likes', 'Timestamp'], ascending=[False, False])
st.subheader("Detailed Ranking")
st.dataframe(df.drop(columns=['Timestamp']), column_config={"Profile": st.column_config.LinkColumn("Link")}, use_container_width=True, hide_index=True)

if has_following:
    not_following_back = [user for user in following_list if user not in followers_info]
    with st.expander(f"🚫 Not Following Back ({len(not_following_back)})"):
        for user in sorted(not_following_back):
            st.markdown(f"- [@{user}](https://www.instagram.com/{user}/)")

# --- REPORT GENERATION ---
def generate_unified_html(df_full, unfollowers=None):
    now = datetime.now().strftime("%d/%m/%Y %H:%M")
    df_export = df_full.copy()
    df_export['Username'] = df_export.apply(lambda row: f'<a class="user-link" href="{row["Profile"]}" target="_blank">@{row["Username"]}</a>', axis=1)
    df_export = df_export.drop(columns=['Timestamp', 'Profile'], errors='ignore')
    table_html = df_export.to_html(index=False, escape=False, classes='main-table')

    html = f"""
    <html><head><meta charset='UTF-8'><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{ font-family: sans-serif; padding: 10px; background: #fafafa; }}
        .table-wrapper {{ overflow-x: auto; background: white; border-radius: 8px; border: 1px solid #dbdbdb; }}
        .main-table {{ width: 100%; border-collapse: collapse; font-size: 0.9rem; }}
        .main-table th, .main-table td {{ padding: 12px; border-bottom: 1px solid #eee; text-align: left; }}
        .user-link {{ color: #0095f6; text-decoration: none; font-weight: bold; }}
    </style></head>
    <body>
        <h1>Instagram Report</h1><p>Date: {now}</p>
        <div class="table-wrapper">{table_html}</div>
    </body></html>
    """
    return html

st.divider()
if st.button("Generate Unified Report File 📄", use_container_width=True):
    lista_unf = not_following_back if has_following else []
    full_html = generate_unified_html(df, lista_unf)
    st.download_button("Download Report", data=full_html, file_name="instagram_report.html", mime="text/html", use_container_width=True)