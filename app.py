import streamlit as st
import pandas as pd

# ダークテーマとページ設定
st.set_page_config(page_title="プロセカdle", layout="wide", initial_sidebar_state="collapsed")

# カスタムCSS（ダークテーマ・マジミラdle風）
st.markdown("""
<style>
.stApp {
    background-color: #12181b;
    color: #e0e0e0;
}
.grid-container {
    display: grid;
    /* 左から: 曲名, 作曲者, ユニット, 歌唱バチャシン, MASTER難易度, APPEND有無, 実装日時 */
    grid-template-columns: 1.5fr 1fr 1fr 1.2fr 1fr 1fr 1.2fr;
    gap: 8px;
    margin-bottom: 8px;
}
.grid-item {
    padding: 5px;
    border-radius: 6px;
    color: white;
    text-align: center;
    font-weight: bold;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    font-size: 13px;
    height: 70px;
    line-height: 1.2;
}
.header-container {
    display: grid;
    grid-template-columns: 1.5fr 1fr 1fr 1.2fr 1fr 1fr 1.2fr;
    gap: 8px;
    margin-bottom: 12px;
    text-align: center;
    font-weight: bold;
    color: #aaa;
    font-size: 12px;
    border-bottom: 1px solid #444;
    padding-bottom: 5px;
}
/* 結果表示カード */
.result-card {
    background-color: #1c252a;
    border: 1px solid #2a4b5c;
    border-radius: 12px;
    padding: 24px;
    margin-top: 20px;
    box-shadow: 0 8px 16px rgba(0,0,0,0.5);
}
.result-card h2 {
    color: #64ffda;
    margin-top: 0;
    border-bottom: 1px solid #333;
    padding-bottom: 10px;
}
.result-p {
    font-size: 15px;
    color: #ccc;
    line-height: 1.6;
    margin: 4px 0;
}
.btn-container {
    display: flex;
    gap: 15px;
    margin-top: 20px;
}
.yt-btn {
    background-color: #cc0000;
    color: white !important;
    text-decoration: none;
    padding: 12px 24px;
    border-radius: 8px;
    font-weight: bold;
    display: inline-block;
    flex: 1;
    text-align: center;
}
.yt-btn:hover { background-color: #ff0000; }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    df = pd.read_csv("pjsk_dle_最新.csv")
    df = df.rename(columns={'製作者': '作曲者'})
    df['歌唱バチャシン'] = df['歌唱バチャシン'].fillna("")
    df['実装日時'] = pd.to_datetime(df['実装日時'], errors='coerce')
    return df

df = load_data()

# セッション管理（ゲーム状態の保持）
if 'target_song' not in st.session_state:
    st.session_state.target_song = df.sample(1).iloc[0]
    
    # 復活：目標曲以外の曲から最初のヒント曲を1曲選出して初期入力とする
    candidates = df[df['曲名'] != st.session_state.target_song['曲名']]
    first_hint = candidates.sample(1).iloc[0]
    st.session_state.guesses = [first_hint]
    
    st.session_state.game_over = False
    st.session_state.win = False

def reset_game():
    del st.session_state.target_song
    st.rerun()

def get_vs_set(vs_str):
    if not vs_str or str(vs_str) == "nan":
        return set()
    vs_str = str(vs_str).replace('、', ',').replace('・', ',')
    return set([e.strip() for e in vs_str.split(',') if e.strip()])

def render_row(guess, target):
    html = '<div class="grid-container">'
    
    # 1. 曲名
    bg_color = "#4caf50" if guess['曲名'] == target['曲名'] else "#444444"
    html += f'<div class="grid-item" style="background-color: {bg_color};">{guess["曲名"]}</div>'
    
    # 2. 作曲者
    bg_color = "#4caf50" if guess['作曲者'] == target['作曲者'] else "#444444"
    html += f'<div class="grid-item" style="background-color: {bg_color};">{guess["作曲者"]}</div>'
    
    # 3. ユニット
    bg_color = "#4caf50" if guess['ユニット'] == target['ユニット'] else "#444444"
    html += f'<div class="grid-item" style="background-color: {bg_color};">{guess["ユニット"]}</div>'
    
    # 4. 歌唱バチャシン
    guess_vs = get_vs_set(guess['歌唱バチャシン'])
    target_vs = get_vs_set(target['歌唱バチャシン'])
    if guess_vs == target_vs and guess_vs:
        bg_color = "#4caf50"
    elif guess_vs.intersection(target_vs):
        bg_color = "#e6c229"
    elif not guess_vs and not target_vs: 
        bg_color = "#4caf50"
    else:
        bg_color = "#444444"
    disp_vs = guess['歌唱バチャシン'] if guess['歌唱バチャシン'] else "なし"
    html += f'<div class="grid-item" style="background-color: {bg_color}; font-size:11px;">{disp_vs}</div>'
    
    # 5. MASTER難易度
    g_diff = int(guess['MASTER難易度'])
    t_diff = int(target['MASTER難易度'])
    if g_diff == t_diff:
        bg_color = "#4caf50"
        text = f"MAS {g_diff}"
    elif g_diff > t_diff:
        bg_color = "#444444"
        text = f"MAS {g_diff}<br><span style='font-size:11px;color:#ff9999;'>🔻もっと下</span>"
    else:
        bg_color = "#444444"
        text = f"MAS {g_diff}<br><span style='font-size:11px;color:#99ff99;'>🔺もっと上</span>"
    html += f'<div class="grid-item" style="background-color: {bg_color};">{text}</div>'
    
    # 6. APPEND有無
    bg_color = "#4caf50" if str(guess['APPEND有無']) == str(target['APPEND有無']) else "#444444"
    html += f'<div class="grid-item" style="background-color: {bg_color};">APP<br>{guess["APPEND有無"]}</div>'
    
    # 7. 実装日時
    g_date = guess['実装日時']
    t_date = target['実装日時']
    date_str = g_date.strftime('%Y-%m-%d')
    if g_date == t_date:
        bg_color = "#4caf50"
        text = f"{date_str}"
    elif g_date > t_date:
        bg_color = "#444444"
        text = f"{date_str}<br><span style='font-size:11px;color:#ff9999;'>🔻前</span>"
    else:
        bg_color = "#444444"
        text = f"{date_str}<br><span style='font-size:11px;color:#99ff99;'>🔺後</span>"
    html += f'<div class="grid-item" style="background-color: {bg_color};">{text}</div>'
    
    html += '</div>'
    return html

# メインUI
st.markdown("<h2 style='text-align: center; color: #fff;'>プロセカdle</h2>", unsafe_allow_html=True)
target = st.session_state.target_song
max_attempts = 8

# ヘッダー表示
st.markdown("""
<div class="header-container">
    <div>曲名</div>
    <div>作曲者</div>
    <div>ユニット</div>
    <div>バチャシン</div>
    <div>MASTER</div>
    <div>APPEND</div>
    <div>実装日時</div>
</div>
""", unsafe_allow_html=True)

# 履歴の描画
for guess in st.session_state.guesses:
    st.markdown(render_row(guess, target), unsafe_allow_html=True)

# 入力フォーム
if not st.session_state.game_over:
    # 最初の1曲が自動入力されるため、残り回数は guessesの数から1引いて計算
    remaining = max_attempts - (len(st.session_state.guesses) - 1)
    st.markdown(f"<p style='color: #888; text-align: center;'>残り入力可能回数: {remaining} 回</p>", unsafe_allow_html=True)
    
    used_songs = [g['曲名'] for g in st.session_state.guesses]
    available_options = []
    song_to_row = {} 
    
    for idx, row in df.iterrows():
        if row['曲名'] not in used_songs:
            disp_name = f"{row['曲名']} (作曲者: {row['作曲者']})"
            available_options.append(disp_name)
            song_to_row[disp_name] = row
            
    # 候補を名前順にソート
    available_options.sort()
    search_options = [""] + available_options
    
    selected_disp = st.selectbox("曲名または作曲者を入力して検索:", search_options)
    
    if st.button("回答する", type="primary"):
        if selected_disp:
            new_guess = song_to_row[selected_disp]
            st.session_state.guesses.append(new_guess)
            
            if new_guess['曲名'] == target['曲名']:
                st.session_state.win = True
                st.session_state.game_over = True
            elif (len(st.session_state.guesses) - 1) >= max_attempts:
                st.session_state.game_over = True
            st.rerun()
        else:
            st.warning("曲を選択してください。")

# 結果表示
if st.session_state.game_over:
    if st.session_state.win:
        # 最初から入っているヒント分の1回を引いて正解数を計算
        attempts_taken = len(st.session_state.guesses) - 1
        title_text = f"🎉 正解！ {attempts_taken}/8回"
    else:
        title_text = "❌ ゲームオーバー (正解は以下の楽曲でした)"

    url = target['楽曲URL'] if '楽曲URL' in df.columns and pd.notna(target['楽曲URL']) else "https://www.youtube.com/"
    vs_disp = target['歌唱バチャシン'] if target['歌唱バチャシン'] else "なし"
    date_disp = target['実装日時'].strftime('%Y年%m月%d日')

    st.markdown(f"""
<div class="result-card">
<h3 style="color: {'#4caf50' if st.session_state.win else '#ff6b6b'}; margin-top: 0;">{title_text}</h3>
<h2>{target['曲名']}</h2>
<p class="result-p"><strong>作曲者：</strong> {target['作曲者']}</p>
<p class="result-p"><strong>ユニット：</strong> {target['ユニット']}</p>
<p class="result-p"><strong>歌唱バチャシン：</strong> {vs_disp}</p>
<p class="result-p"><strong>MASTER難易度：</strong> {target['MASTER難易度']}</p>
<p class="result-p"><strong>実装日時：</strong> {date_disp}</p>
<div class="btn-container">
<a href="{url}" target="_blank" class="yt-btn">▶ YouTubeで聴く</a>
</div>
</div>
""", unsafe_allow_html=True)
    
    st.write("") 
    if st.button("もう一回プレイする"):
        reset_game()
