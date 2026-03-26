import streamlit as st
import streamlit.components.v1 as components
import pandas as pd

st.set_page_config(
    page_title="TUNAGアルムナイ｜採用費シミュレーター",
    page_icon="📊",
    layout="wide",
)

# ══ Default channel data ═══════════════════════════════════════
DEFAULT_CH = {
    'chuto': [
        {'チャネル名': '人材紹介',   '構成比(%)': 65, '採用単価(円)': 850_000},
        {'チャネル名': '採用媒体',   '構成比(%)': 16, '採用単価(円)': 175_000},
        {'チャネル名': 'スカウト',   '構成比(%)':  0, '採用単価(円)': 300_000},
        {'チャネル名': 'リファラル', '構成比(%)': 19, '採用単価(円)':       0},
    ],
    'shinso': [
        {'チャネル名': '求人媒体（新卒）',    '構成比(%)': 60, '採用単価(円)': 500_000},
        {'チャネル名': 'エージェント（新卒）', '構成比(%)': 20, '採用単価(円)': 600_000},
        {'チャネル名': 'リファラル',          '構成比(%)': 20, '採用単価(円)':       0},
    ],
    'part': [
        {'チャネル名': '採用媒体',   '構成比(%)': 80, '採用単価(円)':  50_000},
        {'チャネル名': 'リファラル', '構成比(%)': 20, '採用単価(円)':       0},
    ],
}
SECTIONS = {
    'chuto':  {'label': '中途（正社員）',     'default_on': True,  'hires': 100, 'leavers': 60},
    'shinso': {'label': '新卒（正社員）',     'default_on': False, 'hires':  30, 'leavers':  5},
    'part':   {'label': 'パート・アルバイト', 'default_on': False, 'hires': 500, 'leavers':400},
}

# ══ Session state init ═════════════════════════════════════════
for sec, m in SECTIONS.items():
    st.session_state.setdefault(f'{sec}_on', m['default_on'])
    st.session_state.setdefault(f'{sec}_hires', m['hires'])
    st.session_state.setdefault(f'{sec}_leavers', m['leavers'])
    st.session_state.setdefault(f'{sec}_reg_rate', 30)
    st.session_state.setdefault(f'{sec}_ret_rate', 10)

st.session_state.setdefault('spot_on', False)
st.session_state.setdefault('spot_workers', 100)
st.session_state.setdefault('spot_wage', 1_200)
st.session_state.setdefault('spot_hours', 8)
st.session_state.setdefault('spot_timee_rate', 30)
st.session_state.setdefault('spot_fulfill_rate', 50)
st.session_state.setdefault('initial_fee', 500_000)
st.session_state.setdefault('monthly_fee', 200_000)

# ══ CSS ════════════════════════════════════════════════════════
st.markdown("""
<style>
.stApp { background: #f9fafb; }
.block-container { padding: 28px 32px 48px !important; max-width: 1140px !important; }
body { font-family: "Inter", "Noto Sans JP", "Hiragino Sans", sans-serif; }
footer, #MainMenu, header[data-testid="stHeader"],
[data-testid="stToolbar"], .stDeployButton,
[data-testid="stDecoration"] { display: none !important; }

.pg-title { font-size: 24px; font-weight: 700; color: #0f172a; margin: 0 0 4px 0; }
.pg-sub   { font-size: 14px; color: #94a3b8; margin: 0 0 24px 0; }

/* Left card */
[data-testid="column"]:first-child > div:first-child {
  background: #fff; border: 1px solid #e2e8f0; border-radius: 12px;
  padding: 24px 24px 28px !important; box-shadow: 0 1px 3px rgba(0,0,0,.05);
}

.company-lbl {
  font-size: 11px; font-weight: 500; color: #94a3b8;
  letter-spacing: .08em; text-transform: uppercase; margin: 0 0 6px 0;
}
div[data-testid="stTextInput"] input {
  border-radius: 6px !important; border: 1px solid #e2e8f0 !important;
  font-size: 14px !important; color: #0f172a !important; background: #fff !important;
}
div[data-testid="stTextInput"] input:focus {
  border-color: #2b70ef !important; outline: none !important;
}

/* Section header row */
.sec-row { display: flex; justify-content: space-between; align-items: center; margin: 0 0 10px 0; }
.sec-lbl { font-size: 14px; font-weight: 600; color: #0f172a; margin: 0; }
.sec-divider { border: none; border-top: 1px solid #f1f5f9; margin: 18px 0 14px 0; }

/* Sub label */
.field-lbl {
  font-size: 11px; font-weight: 500; color: #94a3b8;
  letter-spacing: .08em; text-transform: uppercase; margin: 14px 0 6px 0;
}

/* Slider row */
.srow { display: flex; justify-content: space-between; align-items: center; margin: 12px 0 2px 0; }
.slbl { font-size: 13px; color: #64748b; font-weight: 400; }
.sval { font-size: 13px; font-weight: 600; color: #0f172a; font-variant-numeric: tabular-nums; }
.shint { font-size: 11px; color: #94a3b8; margin: -2px 0 4px 0; }
div[data-testid="stSlider"] { margin-top: -2px !important; margin-bottom: 0 !important; }
div[data-testid="stSlider"] p { display: none !important; }

/* Pill */
.pill {
  display: inline-flex; background: #f0f5ff; border: 1px solid #c0d4ff;
  border-radius: 20px; padding: 2px 10px; font-size: 11px; font-weight: 600;
  color: #2b70ef; margin: 4px 0 0 4px;
}

/* Number / checkbox / select */
label[data-testid="stWidgetLabel"] { font-size: 11px !important; color: #94a3b8 !important; }
div[data-testid="stNumberInput"] input {
  border-radius: 6px !important; border: 1px solid #e2e8f0 !important;
  font-size: 13px !important; color: #0f172a !important;
}
div[data-testid="stSelectbox"] > div { font-size: 13px !important; }

/* data_editor */
div[data-testid="stDataFrame"] { border-radius: 8px !important; }

/* Right column cards */
.hero {
  background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 100%);
  border-radius: 12px; padding: 24px 28px; margin-bottom: 12px;
}
.hero-lbl { font-size: 11px; font-weight: 500; color: rgba(255,255,255,.5); letter-spacing: .1em; text-transform: uppercase; margin: 0 0 6px 0; }
.hero-num { font-size: 48px; font-weight: 700; color: #fff; line-height: 1; font-variant-numeric: tabular-nums; margin: 0; }
.hero-sub { font-size: 13px; color: rgba(255,255,255,.6); margin: 10px 0 0 0; }
.hero-sub b { color: rgba(255,255,255,.9); font-weight: 600; }

.kpi-row { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 12px; }
.kpi-box { background: #fff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 18px 20px; box-shadow: 0 1px 3px rgba(0,0,0,.05); }
.kpi-lbl { font-size: 11px; font-weight: 500; color: #94a3b8; letter-spacing: .08em; text-transform: uppercase; margin: 0 0 6px 0; }
.kpi-val   { font-size: 28px; font-weight: 700; color: #0f172a; font-variant-numeric: tabular-nums; margin: 0; }
.kpi-val-r { font-size: 28px; font-weight: 700; color: #ef4444; font-variant-numeric: tabular-nums; margin: 0; }
.kpi-sub   { font-size: 12px; color: #94a3b8; margin: 4px 0 0 0; }

.card { background: #fff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 20px 22px; margin-bottom: 12px; box-shadow: 0 1px 3px rgba(0,0,0,.05); }
.card-lbl { font-size: 11px; font-weight: 500; color: #94a3b8; letter-spacing: .08em; text-transform: uppercase; margin: 0 0 14px 0; }
.card-title { font-size: 15px; font-weight: 600; color: #0f172a; margin: 0 0 14px 0; }

/* Channel table */
.ch-table { width: 100%; border-collapse: collapse; font-size: 12px; margin-bottom: 8px; }
.ch-table th { text-align: left; font-size: 10px; font-weight: 500; color: #94a3b8; text-transform: uppercase; letter-spacing: .06em; padding: 0 8px 8px 8px; border-bottom: 1px solid #e2e8f0; }
.ch-table td { padding: 7px 8px; border-bottom: 1px solid #f8fafc; color: #475569; }
.ch-table tr:last-child td { border-bottom: none; }
.ch-table .num { text-align: right; font-variant-numeric: tabular-nums; }
.ch-table .bold { font-weight: 700; color: #0f172a; }
.ch-highlight td { background: #f0f5ff; color: #2b70ef; font-weight: 600; }

/* Detail rows */
.dr { display: flex; justify-content: space-between; align-items: center; padding: 7px 0; font-size: 13px; color: #475569; border-bottom: 1px solid #f8fafc; }
.dr.sep  { border-top: 1px solid #e2e8f0; margin-top: 4px; padding-top: 10px; }
.dr.bold { font-weight: 700; font-size: 14px; color: #0f172a; }
.dr.last { border-bottom: none; }
.dv   { font-variant-numeric: tabular-nums; white-space: nowrap; }
.dv-g { color: #059669; font-variant-numeric: tabular-nums; white-space: nowrap; }
.dv-r { color: #ef4444; font-variant-numeric: tabular-nums; white-space: nowrap; }

/* Spot comparison */
.spot-grid { display: grid; grid-template-columns: 1fr 32px 1fr; align-items: center; gap: 4px; margin-bottom: 12px; }
.spot-box { border: 1px solid #f1f5f9; border-radius: 8px; padding: 12px 14px; background: #f8fafc; }
.spot-box.after { border-color: #c0d4ff; background: #f0f5ff; }
.spot-tag { font-size: 10px; font-weight: 600; color: #94a3b8; text-transform: uppercase; margin: 0 0 4px 0; }
.spot-val { font-size: 18px; font-weight: 700; color: #0f172a; font-variant-numeric: tabular-nums; }
.spot-box.after .spot-val { color: #2b70ef; }
.spot-note { font-size: 11px; color: #94a3b8; margin: 3px 0 0 0; }
.arrow-c { text-align: center; color: #cbd5e1; font-size: 20px; }

.save-badge { display: inline-flex; align-items: center; gap: 4px; background: #f0fdf4; color: #166534; border: 1px solid #bbf7d0; border-radius: 6px; padding: 4px 12px; font-size: 12px; font-weight: 600; }

.warn { font-size: 11px; color: #78350f; background: #fffbeb; border: 1px solid #fde68a; border-radius: 8px; padding: 8px 12px; margin-top: 12px; }

.stButton > button { background: #0f172a !important; color: #fff !important; border: none !important; border-radius: 6px !important; padding: 8px 20px !important; font-size: 13px !important; font-weight: 500 !important; }
.stButton > button:hover { background: #334155 !important; }

/* Print */
.print-header { display: none; }
@media print {
  .stApp { background: white !important; }
  .block-container { padding: 0 !important; max-width: 100% !important; }
  [data-testid="stHorizontalBlock"] > div:first-child { display: none !important; }
  [data-testid="stHorizontalBlock"] > div:last-child { width: 100% !important; max-width: 100% !important; flex: none !important; }
  .print-header { display: block !important; margin-bottom: 20px; }
  .ph-title { font-size: 11px; color: #94a3b8; letter-spacing: .08em; text-transform: uppercase; margin: 0; }
  .ph-name  { font-size: 22px; font-weight: 700; color: #0f172a; margin: 4px 0 0 0; }
  .ph-line  { border: none; border-top: 2px solid #2b70ef; margin: 10px 0 0 0; }
  .hero { background: #0f172a !important; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  @page { margin: 12mm 15mm; size: A4; }
}
</style>
""", unsafe_allow_html=True)

# ══ Helpers ════════════════════════════════════════════════════
def sldr(label, key, mn, mx, step, fmt_fn, hint=""):
    v = st.session_state.get(key, mn)
    st.markdown(
        f'<div class="srow"><span class="slbl">{label}</span>'
        f'<span class="sval">{fmt_fn(v)}</span></div>',
        unsafe_allow_html=True,
    )
    if hint:
        st.markdown(f'<p class="shint">{hint}</p>', unsafe_allow_html=True)
    return st.slider("", mn, mx, int(v), step, key=key, label_visibility="collapsed")

def man(n):
    if n >= 1_0000_0000:
        return f"{n/1_0000_0000:.1f}億円"
    return f"{n/10_000:.0f}万円"

def dr(label, val, cls="dv", bold=False, sep=False, last=False):
    rc = "dr" + (" bold" if bold else "") + (" sep" if sep else "") + (" last" if last else "")
    return f'<div class="{rc}"><span>{label}</span><span class="{cls}">{val}</span></div>'

def section_header(sec, label):
    c1, c2 = st.columns([5, 1])
    with c1:
        st.markdown(f'<p class="sec-lbl">{label}</p>', unsafe_allow_html=True)
    with c2:
        st.toggle('', key=f'{sec}_on', label_visibility='collapsed')

def render_ch_editor(sec, hires):
    st.markdown('<p class="field-lbl">採用チャネル</p>', unsafe_allow_html=True)
    df0 = pd.DataFrame(DEFAULT_CH[sec])
    edited = st.data_editor(
        df0,
        num_rows='dynamic',
        column_config={
            'チャネル名':   st.column_config.TextColumn('チャネル名', width='medium'),
            '構成比(%)':    st.column_config.NumberColumn('構成比 (%)', min_value=0, max_value=100, step=1),
            '採用単価(円)': st.column_config.NumberColumn('採用単価 (円)', min_value=0, step=10_000, format='¥%d'),
        },
        hide_index=True,
        key=f'{sec}_ch_editor',
        use_container_width=True,
    )
    # Clean NaN
    edited = edited.fillna({'チャネル名': '', '構成比(%)': 0, '採用単価(円)': 0})
    edited['構成比(%)']    = edited['構成比(%)'].astype(int)
    edited['採用単価(円)'] = edited['採用単価(円)'].astype(int)
    # Computed
    edited['採用人数']       = (edited['構成比(%)'] / 100 * hires).round().astype(int)
    edited['年間コスト(万円)'] = ((edited['採用人数'] * edited['採用単価(円)']) / 10_000).round().astype(int)

    total_ratio = int(edited['構成比(%)'].sum())
    if total_ratio > 100:
        st.markdown(f'<p style="color:#ef4444;font-size:12px;margin:4px 0">⚠️ 合計 {total_ratio}%（100%を超えています）</p>', unsafe_allow_html=True)
    else:
        color = "#059669" if total_ratio == 100 else "#94a3b8"
        st.markdown(f'<p style="color:{color};font-size:11px;margin:4px 0">合計 {total_ratio}%</p>', unsafe_allow_html=True)

    return edited

# ══ Page header ════════════════════════════════════════════════
st.markdown("""
<p class="pg-title">TUNAGアルムナイ　採用費シミュレーター</p>
<p class="pg-sub">採用コスト・離職データを入力すると、TUNAGアルムナイ導入による削減効果をリアルタイムで算出します</p>
""", unsafe_allow_html=True)

left, right = st.columns([1, 1.55], gap="large")

# ══ Left column ════════════════════════════════════════════════
results = {}      # sec -> result dict
spot_result = {}

with left:
    # 社名
    st.markdown('<p class="company-lbl">顧客企業名</p>', unsafe_allow_html=True)
    company_name = st.text_input("", placeholder="例）〇〇株式会社", label_visibility="collapsed")

    for sec, meta in SECTIONS.items():
        st.markdown('<hr class="sec-divider">', unsafe_allow_html=True)
        section_header(sec, meta['label'])

        if not st.session_state.get(f'{sec}_on', False):
            continue

        # 年間採用数
        max_h = 5000 if sec == 'part' else 500
        step_h = 50  if sec == 'part' else 10
        hires = sldr('年間採用数', f'{sec}_hires', 0, max_h, step_h, lambda v: f'{v:,}名')

        # Channel editor
        edited = render_ch_editor(sec, hires)
        current_cost = int((edited['採用人数'] * edited['採用単価(円)']).sum())

        st.markdown('<hr class="sec-divider" style="margin:14px 0">', unsafe_allow_html=True)

        # Alumni
        st.markdown('<p class="field-lbl">アルムナイ復職（OB/OG採用）</p>', unsafe_allow_html=True)
        max_l = 5000 if sec == 'part' else 500
        leavers  = sldr('年間離職者数',  f'{sec}_leavers', 0, max_l, step_h, lambda v: f'{v:,}名')
        reg_rate = sldr('アルムナイ登録率', f'{sec}_reg_rate', 0, 100, 1, lambda v: f'{v}%',
                         hint='退職者のうちTUNAGに登録する割合（実績: 20〜40%）')
        ret_rate = sldr('復帰率', f'{sec}_ret_rate', 0, 50, 1, lambda v: f'{v}%',
                         hint='登録者のうち実際に復帰する割合（実績: 5〜15%）')

        # 代替チャネル
        ch_names = [r for r in edited['チャネル名'].tolist() if str(r).strip()]
        if not ch_names:
            ch_names = ['（チャネルなし）']
        replace_ch = st.selectbox(
            '復帰者が代替するチャネル',
            options=ch_names,
            key=f'{sec}_replace_ch',
        )
        matched = edited[edited['チャネル名'] == replace_ch]
        replace_unit = int(matched.iloc[0]['採用単価(円)']) if not matched.empty else 0

        alumni_returns = leavers * reg_rate / 100 * ret_rate / 100
        saving = alumni_returns * replace_unit

        results[sec] = {
            'label': meta['label'],
            'hires': hires,
            'current_cost': current_cost,
            'edited': edited,
            'alumni_returns': alumni_returns,
            'replace_ch': replace_ch,
            'replace_unit': replace_unit,
            'saving': saving,
        }

    # ── スポットワーク ──
    st.markdown('<hr class="sec-divider">', unsafe_allow_html=True)
    section_header('spot', 'スポットワーク手数料削減（タイミー代替）')

    if st.session_state.get('spot_on', False):
        st.markdown('<p class="field-lbl">現状（タイミー利用）</p>', unsafe_allow_html=True)
        workers    = sldr('月間スポットワーカー数', 'spot_workers', 0, 1000, 10, lambda v: f'{v:,}人')
        wage       = sldr('平均時給',               'spot_wage',    800, 3000, 50, lambda v: f'¥{v:,}')
        hours      = sldr('平均勤務時間 / 件',       'spot_hours',   1,   12,   1, lambda v: f'{v}h')
        timee_rate = sldr('タイミー手数料率',         'spot_timee_rate', 5, 50, 1, lambda v: f'{v}%')

        st.markdown('<hr class="sec-divider" style="margin:14px 0">', unsafe_allow_html=True)
        st.markdown('<p class="field-lbl">TUNAGアルムナイでの充足</p>', unsafe_allow_html=True)
        fulfill_rate = sldr(
            'スポットワーク充足率',
            'spot_fulfill_rate', 0, 100, 1, lambda v: f'{v}%',
            hint='スポットワーク需要のうちTUNAGアルムナイで充足できる割合',
        )

        tunag_workers  = workers * fulfill_rate / 100
        timee_workers  = workers - tunag_workers
        monthly_wages  = workers * wage * hours
        current_annual = monthly_wages * timee_rate / 100 * 12
        new_annual     = (tunag_workers * wage * hours * 0.10 + timee_workers * wage * hours * timee_rate / 100) * 12
        spot_saving    = current_annual - new_annual

        spot_result = {
            'workers': workers, 'wage': wage, 'hours': hours,
            'timee_rate': timee_rate, 'fulfill_rate': fulfill_rate,
            'tunag_workers': tunag_workers, 'timee_workers': timee_workers,
            'current_annual': current_annual, 'new_annual': new_annual,
            'saving': spot_saving,
        }

    # ── TUNAG利用料 ──
    st.markdown('<hr class="sec-divider">', unsafe_allow_html=True)
    with st.expander('詳細設定（TUNAG利用料）'):
        c1, c2 = st.columns(2)
        with c1:
            initial_fee = st.number_input('初期費用（円）', min_value=0, value=500_000, step=50_000, format='%d', key='initial_fee')
        with c2:
            monthly_fee = st.number_input('月額利用料（円）', min_value=0, value=200_000, step=10_000, format='%d', key='monthly_fee')

# ══ Calculations ═══════════════════════════════════════════════
recruit_saving = sum(r['saving'] for r in results.values())
spot_saving    = spot_result.get('saving', 0)
total_saving   = recruit_saving + spot_saving

initial_fee = st.session_state.get('initial_fee', 500_000)
monthly_fee = st.session_state.get('monthly_fee', 200_000)
tunag_y1    = initial_fee + monthly_fee * 12
tunag_y2    = monthly_fee * 12
net_y1      = total_saving - tunag_y1
net_y2      = total_saving - tunag_y2
roi         = total_saving / tunag_y2 if tunag_y2 > 0 else 0
pb_months   = tunag_y1 / (total_saving / 12) if total_saving > 0 else float('inf')
monthly_sav = total_saving / 12

# ══ Right column ═══════════════════════════════════════════════
with right:
    pb_str       = f'{pb_months:.0f}ヶ月' if pb_months != float('inf') else '—'
    display_name = company_name.strip() if company_name and company_name.strip() else '貴社'

    st.markdown(f"""
    <div class="print-header">
      <p class="ph-title">TUNAGアルムナイ 費用対効果試算書</p>
      <p class="ph-name">{display_name} 御中</p>
      <hr class="ph-line">
    </div>
    """, unsafe_allow_html=True)

    # ── Hero ──
    sub_parts = [f'毎月 <b>約{man(monthly_sav)}</b> の節約']
    if pb_months != float('inf'):
        sub_parts.append(f'初期費用は <b>{pb_str}</b> で回収')
    st.markdown(f"""
    <div class="hero">
      <p class="hero-lbl">年間コスト削減効果（合計）</p>
      <p class="hero-num">約&thinsp;{man(total_saving)}</p>
      <p class="hero-sub">{'　/　'.join(sub_parts)}</p>
    </div>
    """, unsafe_allow_html=True)

    # ── KPI ──
    roi_cls = 'kpi-val' if roi >= 1 else 'kpi-val-r'
    st.markdown(f"""
    <div class="kpi-row">
      <div class="kpi-box">
        <p class="kpi-lbl">ROI（2年目以降）</p>
        <p class="{roi_cls}">{roi:.1f}倍</p>
        <p class="kpi-sub">TUNAG費用1円あたり {roi:.1f}円の削減</p>
      </div>
      <div class="kpi-box">
        <p class="kpi-lbl">初期費用回収期間</p>
        <p class="kpi-val">{pb_str}</p>
        <p class="kpi-sub">月次削減額に基づく試算</p>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── 採用セクション別: チャネル表 + アルムナイ削減 ──
    for sec, r in results.items():
        edited = r['edited']

        # Build channel table rows
        ch_rows = ''
        for _, row in edited.iterrows():
            name = str(row['チャネル名']).strip()
            if not name:
                continue
            is_replace = (name == r['replace_ch'])
            tr_cls = ' class="ch-highlight"' if is_replace else ''
            cost_man = f"{row['年間コスト(万円)']:,}万円"
            ch_rows += f"""
            <tr{tr_cls}>
              <td>{name}{'&nbsp;<span style="font-size:10px;color:#2b70ef">★代替</span>' if is_replace else ''}</td>
              <td class="num">{row['構成比(%)']:.0f}%</td>
              <td class="num">{row['採用人数']:,}名</td>
              <td class="num">¥{row['採用単価(円)']:,}</td>
              <td class="num bold">{cost_man}</td>
            </tr>"""

        alumni_n = r['alumni_returns']
        save     = r['saving']

        st.markdown(f"""
        <div class="card">
          <p class="card-title">{r['label']}</p>
          <table class="ch-table">
            <thead>
              <tr>
                <th>チャネル</th><th style="text-align:right">構成比</th>
                <th style="text-align:right">採用人数</th><th style="text-align:right">採用単価</th>
                <th style="text-align:right">年間コスト</th>
              </tr>
            </thead>
            <tbody>{ch_rows}</tbody>
          </table>
          <div style="margin-top:10px;padding-top:10px;border-top:1px solid #f1f5f9">
            <span style="font-size:12px;color:#64748b">アルムナイ復職: <b style="color:#0f172a">{alumni_n:.1f}名/年</b>
            &nbsp;×&nbsp;{r['replace_ch']}単価 ¥{r['replace_unit']:,}</span>
            <span class="save-badge" style="margin-left:10px">削減　{man(save)} / 年</span>
          </div>
        </div>
        """, unsafe_allow_html=True)

    # ── スポットワーク ──
    if spot_result:
        sr = spot_result
        st.markdown(f"""
        <div class="card">
          <p class="card-title">スポットワーク手数料削減</p>
          <div class="spot-grid">
            <div class="spot-box">
              <p class="spot-tag">現状（タイミー {sr['timee_rate']}%）</p>
              <p class="spot-val">{man(sr['current_annual'])}</p>
              <p class="spot-note">{sr['workers']}人/月 × ¥{sr['wage']:,} × {sr['hours']}h × {sr['timee_rate']}% × 12</p>
            </div>
            <div class="arrow-c">→</div>
            <div class="spot-box after">
              <p class="spot-tag">導入後（TUNAG {sr['fulfill_rate']:.0f}%充足）</p>
              <p class="spot-val">{man(sr['new_annual'])}</p>
              <p class="spot-note">TUNAG {sr['tunag_workers']:.0f}人（10%）＋ タイミー {sr['timee_workers']:.0f}人（{sr['timee_rate']}%）</p>
            </div>
          </div>
          <span class="save-badge">削減　{man(sr['saving'])} / 年</span>
        </div>
        """, unsafe_allow_html=True)

    # ── 費用対効果まとめ ──
    s1c = 'dv-g' if net_y1 >= 0 else 'dv-r'
    s2c = 'dv-g' if net_y2 >= 0 else 'dv-r'
    sec_rows = ''.join(
        dr(f'　{r["label"]}　採用コスト削減', '＋' + man(r['saving']), 'dv-g')
        for r in results.values()
    )
    spot_row = dr('　スポットワーク手数料削減', '＋' + man(spot_saving), 'dv-g') if spot_result else ''

    st.markdown(f"""
    <div class="card">
      <p class="card-lbl">費用対効果まとめ</p>
      {sec_rows}
      {spot_row}
      {dr('合計削減効果', '＋' + man(total_saving), 'dv-g', bold=True, sep=True)}
      {dr('TUNAG年間費用（初年度: 初期＋月額×12）', '−' + man(tunag_y1), 'dv-r', sep=True)}
      {dr('TUNAG年間費用（2年目以降: 月額×12）', '−' + man(tunag_y2), 'dv-r')}
      {dr('純削減額（初年度）', man(abs(net_y1)), s1c, bold=True, sep=True)}
      {dr('純削減額（2年目以降）', man(abs(net_y2)), s2c, bold=True, last=True)}
      <div class="warn">※ アルムナイ採用単価はゼロで試算（TUNAGアルムナイ経由の1名あたり追加コストは発生しないため）。登録率・復職率はTUNAGアルムナイ導入企業の実績値に基づく参考値です。</div>
    </div>
    """, unsafe_allow_html=True)

    # ── PDF ──
    st.markdown('<div style="margin-top:16px">', unsafe_allow_html=True)
    if st.button('PDF保存 / 印刷', use_container_width=False):
        components.html('<script>window.print();</script>', height=0)
    st.markdown('</div>', unsafe_allow_html=True)
