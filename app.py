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
st.caption("Version 3.4 - Translation with Original JS Logic")

# --- SIDEBAR ---
st.sidebar.title("File Configuration")
fol_file = st.sidebar.file_uploader("1. Upload followers_1.json", type="json")
fng_file = st.sidebar.file_uploader("2. Upload following.json (Optional)", type="json")

# --- STARTUP MESSAGE ---
if not fol_file:
    st.info("👈 To begin, upload the 'followers_1.json' file in the sidebar on the left.")
    st.stop() 

# --- SECTION: USER GUIDE ---
with st.expander("📖 How to use this tool (Read first)", expanded=True):
    st.markdown("""
    ### 1. Data Collection & Files
    * **Mandatory:** Upload `followers_1.json`. This is required to see your follower list and calculate "Follower since" dates.
    * **Optional:** Upload `following.json`. 
        * *If provided:* The tool will identify "Non-followers" (people you follow who don't follow you back).
        * *If skipped:* You can still analyze Ghost Followers and Rank interactions, but the "Follow Back" column and the "Not Following Back" list will be hidden.
    
    ### 2. Smart Bookmarks
    Use the **Smart Bookmarks** section below while browsing Instagram to collect "Likes" from your posts. Paste those links into the analysis area to see who is interacting and who is a "Ghost."
    
    ### 3. Save Your Results Locally
    Once your analysis is complete, scroll to the bottom and click **"Generate Unified Report File"**. 
    * **Why?** This creates a standalone HTML file containing your full ranking and the list of people not following you back.
    * **Recommendation:** Keep this file on your phone or computer. It works offline and allows you to manage your cleaning process over time without re-uploading everything here.
    
    ### 4. Using the "Copy" Button for Private Profiles
    Instagram often restricts the "Unfollow" action for certain accounts (especially private ones) if you visit their profile directly from a third-party link.
    * **The Solution:** In your downloaded report, use the blue **Copy** button next to any username. 
    * **The Workflow:** Copy the name → Open your **Instagram App** → Go to your **Following list** → **Paste** the name in the search bar. This allows you to find and remove them instantly and safely within the official app.
    """)

# --- SECTION: INSTRUCTIONS ---
with st.expander("🚀 Smart Bookmarks Setup", expanded=False):
    st.markdown("""
    To capture "Likes" and profile links directly from Instagram, use these two smart bookmarks. They work on both Desktop and Mobile browsers.
    """)
    
    tab1, tab2 = st.tabs(["🖥️ Option A: Desktop (Drag & Drop)", "📱 Option B: Mobile (Manual)"])
    
    # --- JAVASCRIPT FIXED CODES ---
    js_start = """javascript:(function(){window.allProfiles=window.allProfiles||new Set();if(window.myInterval)clearInterval(window.myInterval);const t=document.createElement('div');t.innerHTML="✅ Script Started - Scroll Now";t.style="position:fixed;top:20px;left:50%;transform:translateX(-50%);background:#0095f6;color:white;padding:12px 20px;border-radius:25px;z-index:999999;font-family:sans-serif;font-weight:bold;box-shadow:0 4px 12px rgba(0,0,0,0.3);transition:opacity 0.5s;";document.body.appendChild(t);setTimeout(()=>{t.style.opacity='0';setTimeout(()=>{document.body.removeChild(t)},500)},2000);window.myInterval=setInterval(()=>{document.querySelectorAll('a[role="link"]').forEach(a=>{if(a.href.includes("instagram.com/")&&!a.href.includes("/p/")&&!a.href.includes("/reels/")&&!a.href.includes("/explore/")){window.allProfiles.add(a.href)}})},800);})();"""
    js_copy = """javascript:(function(){     clearInterval(window.myInterval);     if(window.allProfiles && window.allProfiles.size > 0){          const t = [...window.allProfiles].join('\\n');          const el = document.createElement('textarea');         el.value = t;         el.style.position = 'fixed';         el.style.left = '-9999px';         document.body.appendChild(el);         el.select();         el.setSelectionRange(0, 99999);         const successful = document.execCommand('copy');         document.body.removeChild(el);          if(successful) {             alert("✅ " + window.allProfiles.size + " links copied to clipboard!");             window.allProfiles = new Set();         } else {             const div = document.createElement('div');             div.style = "position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.9);z-index:999999;display:flex;flex-direction:column;align-items:center;justify-content:center;padding:20px;box-sizing:border-box;font-family:sans-serif;";             const area = document.createElement('textarea');             area.value = t;             area.style = "width:100%;max-width:500px;height:300px;padding:10px;border-radius:8px;font-size:14px;border:none;";             const btnCopy = document.createElement('button');             btnCopy.innerText = "📋 COPY ALL";             btnCopy.style = "width:100%;max-width:500px;margin-top:15px;padding:15px;background:#0095f6;color:white;border:none;border-radius:8px;font-weight:bold;";             btnCopy.onclick = function() { area.select(); if(document.execCommand('copy')) { btnCopy.innerText = "✅ COPIED!"; setTimeout(() => { document.body.removeChild(div); }, 700); } };             const btnClose = document.createElement('button');             btnClose.innerText = "CLOSE";             btnClose.style = "margin-top:15px;background:transparent;color:white;border:none;text-decoration:underline;";             btnClose.onclick = function() { document.body.removeChild(div); };             div.appendChild(area); div.appendChild(btnCopy); div.appendChild(btnClose); document.body.appendChild(div);         }      } else {          alert("❌ No profiles captured.");      } })();"""

    with tab1:
        st.markdown("""
        #### **Setup**
        1. Ensure your browser's **Bookmarks Bar** is visible (`Ctrl+Shift+B`).
        2. **Triple-click** to select the entire code below.
        3. **Drag and drop** the highlighted text directly onto your Bookmarks Bar.
        """)
        st.write("**Code for START:**")
        st.code(js_start, language="javascript")
        st.write("**Code for COPY:**")
        st.code(js_copy, language="javascript")

    with tab2:
        st.markdown("""
        #### **Setup**
        1. Copy the code below.
        2. Create a bookmark and paste the code into the **URL** (Address) field.
        """)
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

# --- SET VISUALIZATION AND CALCULATION ---
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
m4.metric("Analyzed Sets", len(st.session_state.sets_di_like))

# --- RANKING ---
all_users = set(followers_info.keys()).union(set(like_counts.keys()))
results = []
for user in all_users:
    row = {
        "Username": user,
        "Likes": like_counts.get(user, 0),
        "Follower since": datetime.fromtimestamp(followers_info[user]).strftime('%d/%m/%Y') if user in followers_info else "-",
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

# --- REPORT GENERATION (FINAL VERSION - OPTIMIZED HEADERS & DATE FONT) ---
def generate_unified_html(df_full, unfollowers_list=None):
    now = datetime.now().strftime("%m/%d/%Y %H:%M")
    df_export = df_full.copy()
    
    # Conditional visibility for Follow Back? column (show only NO)
    if 'Follow Back?' in df_export.columns:
        df_export['Follow Back?'] = df_export['Follow Back?'].apply(
            lambda x: x if x == "NO ⚠️" else ""
        )
    
    # Process Username: clickable link + copy button
    df_export['Username'] = df_export.apply(
        lambda row: f'<div class="user-cell"><a class="user-link" href="{row["Profile"]}" target="_blank">@{row["Username"]}</a><button class="copy-btn" onclick="copyToClipboard(\'{row["Username"]}\', this)">Copy</button></div>', 
        axis=1
    )
    
    df_export = df_export.drop(columns=['Timestamp', 'Profile'], errors='ignore')
    
    cols_to_show = ['Username', 'Likes', 'Follower since']
    if 'Follow Back?' in df_export.columns:
        cols_to_show.append('Follow Back?')
    
    df_export = df_export[cols_to_show]
    
    # Generate table
    table_html = df_export.to_html(index=False, escape=False, border=0, classes='main-table', justify='unset')

    html = f"""
    <html>
    <head>
        <meta charset='UTF-8'>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{ font-family: -apple-system, system-ui, sans-serif; padding: 10px; background: #ffffff; color: #262626; }}
            .container {{ max-width: 98%; margin: auto; }}
            h2 {{ font-weight: 600; font-size: 1.2rem; margin: 20px 0 10px 0; }}

            .table-wrapper {{ width: 100%; max-height: 70vh; overflow: auto; border: 1px solid #eeeeee; border-radius: 8px; }}
            .main-table {{ border-collapse: collapse; width: 100%; table-layout: fixed; font-size: 0.85rem; }}
            
            /* Column Widths & Dividers */
            .main-table th:nth-child(1), .main-table td:nth-child(1) {{ width: 58%; text-align: left; padding-left: 10px; }}
            
            .main-table th:nth-child(2), .main-table td:nth-child(2) {{ width: 10%; text-align: center; border-left: 1px solid #eeeeee; }}
            
            /* Date Column: Header wraps, Data stays on one line */
            .main-table th:nth-child(3) {{ 
                width: 20%; text-align: center; border-left: 1px solid #eeeeee; 
                white-space: normal !important; /* Title can wrap */
                padding: 10px 2px;
            }}
            .main-table td:nth-child(3) {{ 
                text-align: center; border-left: 1px solid #eeeeee; 
                font-size: 0.75rem; white-space: nowrap; /* Date stays single line */
                padding: 8px 2px !important;
            }}
            
            /* Follow Back Header: Centered with equal padding */
            .main-table th:nth-child(4) {{ 
                width: 12%; text-align: center; border-left: 1px solid #eeeeee; 
                padding: 10px 0px !important; 
            }}
            .main-table td:nth-child(4) {{ 
                text-align: center; border-left: 1px solid #eeeeee; 
                padding: 8px 0px !important;
            }}

            .main-table th {{ position: sticky; top: 0; background: #fafafa; border-bottom: 1px solid #eeeeee; color: #8e8e8e; font-size: 0.7rem; text-transform: uppercase; z-index: 2; }}
            .main-table td {{ border-bottom: 1px solid #f5f5f5; vertical-align: middle; }}
            
            .user-cell {{ display: flex; align-items: center; justify-content: space-between; white-space: nowrap; overflow: hidden; }}
            .user-link {{ color: #0095f6; text-decoration: none; font-weight: 600; text-overflow: ellipsis; overflow: hidden; }}
            
            .copy-btn {{ 
                background-color: #0095f6; color: white; border: none; border-radius: 4px; 
                padding: 4px 8px; font-size: 0.65rem; cursor: pointer; font-weight: bold; margin-left: 5px; flex-shrink: 0;
            }}
            .copy-btn.copied {{ background-color: #262626; }}

            .unfollow-list {{ border-top: 1px solid #eeeeee; margin-top: 10px; }}
            .unfollow-item {{ padding: 10px; border-bottom: 1px solid #f9f9f9; display: flex; justify-content: space-between; align-items: center; text-decoration: none; }}
        </style>
        <script>
            function copyToClipboard(text, btn) {{
                navigator.clipboard.writeText(text).then(() => {{
                    const oldText = btn.innerText;
                    btn.innerText = 'Copied!';
                    btn.classList.add('copied');
                    setTimeout(() => {{ btn.innerText = oldText; btn.classList.remove('copied'); }}, 1200);
                }});
            }}
        </script>
    </head>
    <body>
        <div class="container">
            <h2>📊 Interaction Ranking</h2>
            <div class="table-wrapper">{table_html}</div>
    """

    if unfollowers_list:
        html += f"<h2>🚫 Not Following Back ({len(unfollowers_list)})</h2><div class='unfollow-list'>"
        for u in unfollowers_list:
            html += f'<div class="unfollow-item"><a class="user-link" href="https://www.instagram.com/{u}/" target="_blank">@{u}</a><button class="copy-btn" onclick="copyToClipboard(\'{u}\', this)">Copy</button></div>'
        html += "</div>"
    
    html += "</div></body></html>"
    return html

# --- DOWNLOAD LOGIC ---
st.divider()
if st.button("Generate Unified Report File 📄", use_container_width=True):
    unf_list = not_following_back if 'not_following_back' in locals() else []
    full_report = generate_unified_html(df, unf_list)
    
    st.download_button(
        label="📥 Click here to Download HTML Report",
        data=full_report,
        file_name="instagram_report.html",
        mime="text/html",
        use_container_width=True
    )