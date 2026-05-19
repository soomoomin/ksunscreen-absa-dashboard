import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(
    page_title='K-Beauty Sunscreen ABSA Dashboard',
    layout='wide',
    initial_sidebar_state='expanded'
)

st.markdown("""
<style>
    .stApp { background-color: #2C2C2A; }
    section[data-testid="stSidebar"] { background-color: #1e1e1c; }
    section[data-testid="stSidebar"] * { color: #B4B2A9 !important; }
    .stApp, .stApp p, .stApp div { color: #D3D1C7; }

    .stTabs [data-baseweb="tab-list"] {
        background-color: #1e1e1c;
        border-radius: 8px;
        padding: 4px;
        gap: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        color: #888780 !important;
        background-color: transparent;
        border-radius: 6px;
        padding: 6px 20px !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: #FF6B35 !important;
        color: #fff !important;
    }

    .insight-card {
        background-color: #1e1e1c;
        border: 0.5px solid #444;
        border-radius: 10px;
        padding: 16px 20px;
        margin-bottom: 12px;
    }
    .insight-title { font-size: 11px; color: #888780; margin-bottom: 8px; letter-spacing: 1px; }
    .insight-text  { font-size: 14px; color: #D3D1C7; line-height: 1.7; }

    .tag-pos {
        display: inline-block;
        background-color: rgba(99,153,34,0.15);
        color: #639922;
        border: 0.5px solid rgba(99,153,34,0.4);
        border-radius: 12px;
        padding: 3px 10px; font-size: 12px; margin: 3px 3px 3px 0;
    }
    .tag-neg {
        display: inline-block;
        background-color: rgba(226,75,74,0.15);
        color: #E24B4A;
        border: 0.5px solid rgba(226,75,74,0.4);
        border-radius: 12px;
        padding: 3px 10px; font-size: 12px; margin: 3px 3px 3px 0;
    }
    .tag-neu {
        display: inline-block;
        background-color: rgba(136,135,128,0.15);
        color: #B4B2A9;
        border: 0.5px solid rgba(136,135,128,0.4);
        border-radius: 12px;
        padding: 3px 10px; font-size: 12px; margin: 3px 3px 3px 0;
    }

    hr { border-color: #444; }

    /* 사이드바 버튼 */
    .stButton > button {
        width: 100%;
        text-align: left;
        background-color: transparent;
        border: 0.5px solid #3a3a38;
        color: #B4B2A9 !important;
        border-radius: 6px;
        padding: 8px 12px;
        margin-bottom: 3px;
        line-height: 1.4;
        white-space: pre-wrap;
    }
    .stButton > button:hover { background-color: #2C2C2A; border-color: #FF6B35; }

    /* 구매 링크 버튼 */
    .link-btn {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background-color: #1e1e1c;
        border: 0.5px solid #555;
        border-radius: 6px;
        padding: 7px 14px;
        color: #D3D1C7;
        font-size: 13px;
        text-decoration: none;
    }
    .link-btn:hover { border-color: #FF6B35; color: #FF6B35; text-decoration: none; }
    .link-arrow { font-size: 11px; color: #888780; }

    /* 구매링크 텍스트 */
    .link-section-label {
        font-size: 11px;
        color: #888780;
        margin-right: 10px;
        white-space: nowrap;
    }
</style>
""", unsafe_allow_html=True)

# ── 속성 확정 ─────────────────────────────────────────
KR_ASPECTS = ['보습력', '발림성', '자극', '자외선차단', '백탁', '유지력', '가성비', '끈적임']
GB_ASPECTS = ['spreadability', 'white_cast', 'hydration',
              'irritation', 'scent', 'price',
              'sun_protection', 'lightweight']

GB_LABELS = {
    'spreadability' : 'spreadability',
    'white_cast'    : 'white cast',
    'hydration'     : 'hydration',
    'irritation'    : 'irritation',
    'scent'         : 'scent',
    'price'         : 'price',
    'sun_protection': 'sun protection',
    'lightweight': 'lightweight'
}

# ── 데이터 로드 ───────────────────────────────────────
@st.cache_data
def load_data():
    kr       = pd.read_csv('absa_product_summary.csv')
    gb       = pd.read_csv('absa_product_summary_gb.csv')
    products = pd.read_csv('product_link.csv')
    products.columns = products.columns.str.strip()
    return kr, gb, products

kr_df, gb_df, products_df = load_data()

product_info = {}
for _, row in products_df.iterrows():
    product_info[row['product_name']] = {
        'brand'   : row['brand'],
        'name_kr' : row['name_kr'],
        'name_gb' : row['name_gb'],
        'link_kr' : row['link_kr'],
        'link_gb' : row['link_gb'],
    }

PRODUCT_CODES = list(product_info.keys())

# ── 헬퍼 함수 ─────────────────────────────────────────
def hex_to_rgba(hex_color, alpha=0.15):
    h = hex_color.lstrip('#')
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f'rgba({r},{g},{b},{alpha})'

def get_scores(df, product, aspects):
    sub = df[df['product_name'] == product]
    scores = []
    for asp in aspects:
        row = sub[sub['aspect'] == asp]
        scores.append(float(row['avg_score'].values[0]) if len(row) > 0 else 0.0)
    return scores

def make_insight(df, product, aspects, labels, market_name):
    sub  = df[df['product_name'] == product]
    rows = []
    for asp in aspects:
        row   = sub[sub['aspect'] == asp]
        score = float(row['avg_score'].values[0]) if len(row) > 0 else 0.0
        rows.append({'aspect': asp, 'label': labels.get(asp, asp), 'score': score})

    ranked = sorted(rows, key=lambda x: x['score'], reverse=True)
    top2   = [r for r in ranked if r['score'] > 0.1][:2]
    bot2   = [r for r in ranked if r['score'] < -0.05][:2]

    if top2 and bot2:
        top_str  = ' · '.join([r['label'] for r in top2])
        bot_str  = ' · '.join([r['label'] for r in bot2])
        sentence = (f"{market_name} 소비자는 <b>{top_str}</b>을 강점으로 평가했으며, "
                    f"<b>{bot_str}</b>에 부정적인 반응을 보였어요.")
    elif top2:
        top_str  = ' · '.join([r['label'] for r in top2])
        sentence = f"{market_name} 소비자는 <b>{top_str}</b>을 강점으로 평가했어요."
    else:
        sentence = f"{market_name} 소비자 리뷰에서 두드러진 긍정/부정 반응이 없었어요."

    tags_html = ''
    for r in ranked:
        if r['score'] > 0.1:
            tags_html += f'<span class="tag-pos">✅ {r["label"]}</span>'
        elif r['score'] < -0.05:
            tags_html += f'<span class="tag-neg">❌ {r["label"]}</span>'
        else:
            tags_html += f'<span class="tag-neu">— {r["label"]}</span>'

    return sentence, tags_html

def draw_radar_chart(aspects, scores, color):
    aspects_c = aspects + [aspects[0]]
    scores_c  = scores  + [scores[0]]
    fig = go.Figure(go.Scatterpolar(
        r=scores_c, theta=aspects_c,
        fill='toself',
        line=dict(color=color, width=2),
        fillcolor=hex_to_rgba(color, 0.15),
    ))
    fig.update_layout(
        polar=dict(
            bgcolor='#1e1e1c',
            radialaxis=dict(
                visible=True, range=[-0.5, 0.8],
                tickfont=dict(color='#888780', size=9),
                gridcolor='#444', linecolor='#444',
            ),
            angularaxis=dict(
                tickfont=dict(color='#D3D1C7', size=11),
                gridcolor='#444', linecolor='#444',
            )
        ),
        paper_bgcolor='#1e1e1c',
        plot_bgcolor='#1e1e1c',
        font=dict(color='#D3D1C7'),
        showlegend=False,
        margin=dict(t=30, b=30, l=40, r=40),
        height=340,
    )
    return fig

def draw_bar_chart(aspects, scores, labels):
    colors         = ['#639922' if s > 0.1 else '#E24B4A' if s < -0.05 else '#888780' for s in scores]
    display_labels = [labels.get(a, a) for a in aspects]
    fig = go.Figure(go.Bar(
        x=scores, y=display_labels,
        orientation='h',
        marker=dict(color=colors),
        text=[f'{s:+.3f}' for s in scores],
        textposition='outside',
        textfont=dict(color='#D3D1C7', size=11),
    ))
    fig.add_vline(x=0, line_color='#555', line_width=1)
    fig.update_layout(
        paper_bgcolor='#1e1e1c', plot_bgcolor='#1e1e1c',
        font=dict(color='#D3D1C7'),
        xaxis=dict(range=[-0.6, 0.9], gridcolor='#333',
                   zerolinecolor='#555', tickfont=dict(color='#888780', size=10)),
        yaxis=dict(tickfont=dict(color='#D3D1C7', size=12), autorange='reversed'),
        margin=dict(t=10, b=10, l=10, r=60),
        height=300, bargap=0.3,
    )
    return fig

# ── 사이드바 ──────────────────────────────────────────
with st.sidebar:
    st.markdown(
        '<p style="color:#FF6B35;font-size:15px;font-weight:500;margin-bottom:16px;">'
        '🌞 K-Beauty ABSA</p>',
        unsafe_allow_html=True
    )
    st.markdown(
        '<p style="font-size:10px;color:#666;letter-spacing:1px;margin-bottom:8px;">PRODUCT</p>',
        unsafe_allow_html=True
    )

    if 'selected_product' not in st.session_state:
        st.session_state.selected_product = PRODUCT_CODES[0]

    for code in PRODUCT_CODES:
        info  = product_info[code]
        # 브랜드(작게, 회색) + 줄바꿈 + 제품명
        label = f"{info['brand']}\n{info['name_kr']}"
        if st.button(label, key=f'btn_{code}'):
            st.session_state.selected_product = code
            st.rerun()

# ── 메인 영역 ─────────────────────────────────────────
product = st.session_state.selected_product
info    = product_info[product]

# 제품 헤더
st.markdown(
    f'<p style="font-size:22px;font-weight:500;color:#fff;margin-bottom:2px;">'
    f'{info["brand"]} — {info["name_kr"]}</p>'
    f'<p style="font-size:13px;color:#888780;margin-bottom:12px;">{info["name_gb"]}</p>',
    unsafe_allow_html=True
)

# 구매링크 텍스트 + 링크 버튼 나란히
st.markdown(
    f'<div style="display:flex;align-items:center;gap:10px;margin-bottom:14px;">'
    f'<span class="link-section-label">구매 링크</span>'
    f'<a href="{info["link_kr"]}" target="_blank" class="link-btn">'
    f'🇰🇷 Olive Young KR <span class="link-arrow">↗</span>'
    f'</a>'
    f'<a href="{info["link_gb"]}" target="_blank" class="link-btn">'
    f'🌍 Olive Young Global <span class="link-arrow">↗</span>'
    f'</a>'
    f'</div>',
    unsafe_allow_html=True
)

st.markdown('<hr style="border-color:#444;margin:0 0 14px 0;">', unsafe_allow_html=True)

# ── KR / GB 탭 ────────────────────────────────────────
tab_kr, tab_gb = st.tabs(['🇰🇷  국내 KR', '🌍  글로벌 GB'])

with tab_kr:
    kr_scores = get_scores(kr_df, product, KR_ASPECTS)
    kr_labels = {a: a for a in KR_ASPECTS}

    sentence, tags_html = make_insight(kr_df, product, KR_ASPECTS, kr_labels, '국내')
    st.markdown(
        f'<div class="insight-card">'
        f'<div class="insight-title">💡 INSIGHT</div>'
        f'<div class="insight-text">{sentence}</div>'
        f'<div style="margin-top:10px;">{tags_html}</div>'
        f'</div>',
        unsafe_allow_html=True
    )
    col_r, col_b = st.columns(2)
    with col_r:
        st.plotly_chart(draw_radar_chart(KR_ASPECTS, kr_scores, '#FF6B35'),
                        use_container_width=True)
    with col_b:
        st.plotly_chart(draw_bar_chart(KR_ASPECTS, kr_scores, kr_labels),
                        use_container_width=True)

with tab_gb:
    gb_scores = get_scores(gb_df, product, GB_ASPECTS)

    sentence_gb, tags_html_gb = make_insight(gb_df, product, GB_ASPECTS, GB_LABELS, '글로벌')
    st.markdown(
        f'<div class="insight-card">'
        f'<div class="insight-title">💡 INSIGHT</div>'
        f'<div class="insight-text">{sentence_gb}</div>'
        f'<div style="margin-top:10px;">{tags_html_gb}</div>'
        f'</div>',
        unsafe_allow_html=True
    )
    col_r2, col_b2 = st.columns(2)
    with col_r2:
        gb_display = [GB_LABELS.get(a, a) for a in GB_ASPECTS]
        st.plotly_chart(draw_radar_chart(gb_display, gb_scores, '#5BB8E6'),
                        use_container_width=True)
    with col_b2:
        st.plotly_chart(draw_bar_chart(GB_ASPECTS, gb_scores, GB_LABELS),
                        use_container_width=True)

st.markdown(
    '<p style="text-align:center;font-size:11px;color:#444;margin-top:40px;">'
    'K-Beauty Sunscreen ABSA Dashboard · Data source: Olive Young KR / Global</p>',
    unsafe_allow_html=True
)
