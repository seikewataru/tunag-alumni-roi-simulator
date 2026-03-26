import streamlit as st
import streamlit.components.v1 as components
import pandas as pd

st.set_page_config(
    page_title="TUNAGアルムナイ｜採用費シミュレーター",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ══ Constants ══════════════════════════════════════════════════
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
    'part':   {'label': 'パート・アルバイト', 'default_on': False, 'hires': 500, 'leavers': 400},
}

# ══ Session state ══════════════════════════════════════════════
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
st.session_state.setdefault('company_name', '')
st.session_state.setdefault('results_cache', {})
st.session_state.setdefault('spot_cache', {})

# ══ CSS ════════════════════════════════════════════════════════
st.markdown("""
<style>
/* ── Design tokens (melta design system + 5 designers) ── */
:root {
  --p:          #2b70ef;   /* primary-500 */
  --p-hover:    #1d5fd4;   /* primary-600 */
  --p-surface:  #f0f5ff;   /* primary-50  */
  --p-border:   #c0d4ff;   /* primary-200 */

  --success:         #059669;
  --success-surface: #ecfdf5;
  --success-border:  #a7f3d0;
  --warning:         #d97706;
  --warning-surface: #fffbeb;
  --warning-border:  #fde68a;
  --danger:          #ef4444;
  --danger-surface:  #fef2f2;
  --danger-border:   #fecaca;
  --neutral:         #64748b;

  --text-1: #0f172a;   /* headings */
  --text-2: #3d4b5f;   /* body (melta) */
  --text-3: #64748b;   /* secondary */
  --text-4: #94a3b8;   /* muted / labels */

  --bg-page:    #f8fafc;
  --bg-surface: #ffffff;
  --bd:         #e2e8f0;
  --bd-sub:     #f1f5f9;
}

/* ── Global ── */
.stApp { background: var(--bg-page); }
.block-container { padding: 28px 32px 48px !important; max-width: 1100px !important; }
body {
  font-family: "Inter", "Noto Sans JP", "Hiragino Sans", sans-serif;
  font-feature-settings: "cv02", "cv03", "cv04", "cv11";
  -webkit-font-smoothing: antialiased;
  color: var(--text-2);
}
footer, #MainMenu, header[data-testid="stHeader"],
[data-testid="stToolbar"], .stDeployButton,
[data-testid="stDecoration"] { display: none !important; }


/* ── Sidebar ── */
[data-testid="stSidebar"] {
  background: var(--bg-surface) !important;
  border-right: 1px solid var(--bd) !important;
  min-width: 220px !important;
  max-width: 240px !important;
}
[data-testid="stSidebarContent"] { padding: 24px 12px 20px !important; }

.nav-brand {
  display: flex; align-items: center; gap: 10px;
  padding: 0 8px 18px 8px; margin-bottom: 12px;
  border-bottom: 1px solid var(--bd-sub);
}
.nav-brand-icon {
  width: 30px; height: 30px; border-radius: 8px;
  background: var(--p); color: #fff;
  font-size: 14px; font-weight: 700;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.nav-logo { font-size: 13px; font-weight: 600; color: var(--text-1); margin: 0; line-height: 1.3; }
.nav-sub  { font-size: 11px; color: var(--text-4); margin: 0; line-height: 1.4; }

/* Radio → nav item */
[data-testid="stSidebar"] [data-testid="stRadio"] label {
  display: flex !important; align-items: center !important;
  width: 100% !important; padding: 8px 12px !important;
  border-radius: 8px !important; cursor: pointer !important;
  transition: background 120ms ease, color 120ms ease !important;
  color: var(--text-3) !important; font-size: 13px !important;
  font-weight: 500 !important; margin-bottom: 2px !important;
  background: transparent !important; border: 1px solid transparent !important;
  line-height: 1 !important;
}
[data-testid="stSidebar"] [data-testid="stRadio"] label > div:first-child { display: none !important; }
[data-testid="stSidebar"] [data-testid="stRadio"] label p {
  color: inherit !important; font-size: 13px !important; font-weight: inherit !important; margin: 0 !important;
}
[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
  background: var(--bg-page) !important; color: var(--text-1) !important;
}
[data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) {
  background: var(--p-surface) !important; color: var(--p) !important;
  font-weight: 600 !important; border-color: var(--p-border) !important;
}

/* ── Page title ── */
.pg-title { font-size: 28px; font-weight: 700; color: var(--text-1); margin: 0 0 4px 0; letter-spacing: -0.015em; line-height: 1.25; }
.pg-sub   { font-size: 14px; color: var(--text-4); margin: 0 0 20px 0; line-height: 1.6; }

/* ── Input form ── */
.company-lbl { font-size: 12px; font-weight: 500; color: var(--text-2); margin: 0 0 6px 0; }
.field-lbl   { font-size: 12px; font-weight: 500; color: var(--text-2); margin: 14px 0 6px 0; }

div[data-testid="stTextInput"] input {
  border-radius: 8px !important; border: 1px solid var(--bd) !important;
  font-size: 14px !important; color: var(--text-1) !important; background: var(--bg-surface) !important;
  transition: border-color 0.15s, box-shadow 0.15s !important;
}
div[data-testid="stTextInput"] input:focus {
  border-color: var(--p) !important;
  box-shadow: 0 0 0 3px rgba(43,112,239,.12) !important; outline: none !important;
}

/* Section header with ON/OFF state */
.sec-header {
  display: flex; justify-content: space-between; align-items: center;
  padding: 10px 0 8px 14px; margin-left: -14px;
  border-left: 3px solid var(--bd); transition: border-color 0.2s ease;
}
.sec-header.is-on  { border-left-color: var(--p); }
.sec-lbl     { font-size: 14px; font-weight: 600; color: var(--text-1); margin: 0; line-height: 1.3; }
.sec-lbl.off { color: var(--text-4); font-weight: 500; }
.sec-status     { font-size: 11px; font-weight: 600; margin-right: 8px; letter-spacing: .02em; }
.sec-status.on  { color: var(--p); }
.sec-status.off { color: var(--text-4); }
.sec-divider { border: none; border-top: 1px solid var(--bd-sub); margin: 20px 0 16px 0; }

/* Slider */
.srow { display: flex; justify-content: space-between; align-items: center; margin: 12px 0 2px 0; }
.slbl { font-size: 13px; color: var(--text-3); font-weight: 400; line-height: 1.5; }
.sval {
  font-size: 12px; font-weight: 600; color: var(--p);
  background: var(--p-surface); border: 1px solid var(--p-border);
  border-radius: 20px; padding: 2px 10px;
  font-variant-numeric: tabular-nums; white-space: nowrap;
}
.shint { font-size: 11px; color: var(--text-4); margin: -2px 0 4px 0; line-height: 1.5; }
div[data-testid="stSlider"] { margin-top: -2px !important; margin-bottom: 0 !important; }
div[data-testid="stSlider"] p { display: none !important; }

label[data-testid="stWidgetLabel"] { font-size: 12px !important; color: var(--text-3) !important; }
div[data-testid="stNumberInput"] input {
  border-radius: 8px !important; border: 1px solid var(--bd) !important; font-size: 13px !important;
}
div[data-testid="stSelectbox"] > div { font-size: 13px !important; }

/* Validation indicator */
.val-ind {
  display: flex; align-items: center; gap: 6px;
  padding: 5px 10px; border-radius: 6px; font-size: 12px; font-weight: 500; margin: 6px 0 0 0;
}
.val-ind.ok    { background: var(--success-surface); color: #15803d; border: 1px solid var(--success-border); }
.val-ind.warn  { background: var(--warning-surface); color: #92400e; border: 1px solid var(--warning-border); }
.val-ind.error { background: var(--danger-surface);  color: #dc2626; border: 1px solid var(--danger-border); }

/* ── Result: Hero ── */
.hero {
  background: linear-gradient(135deg, #0c1628 0%, #0f172a 45%, #0d2340 100%);
  border-radius: 14px; padding: 30px 34px 26px; margin-bottom: 14px;
  position: relative; overflow: hidden;
  border: 1px solid rgba(255,255,255,.05);
}
.hero::before {
  content: ''; position: absolute; top: -60px; right: -60px;
  width: 240px; height: 240px; border-radius: 50%;
  background: radial-gradient(circle, rgba(43,112,239,.18) 0%, transparent 65%);
  pointer-events: none;
}
.hero::after {
  content: ''; position: absolute; bottom: -40px; left: 20%;
  width: 180px; height: 180px; border-radius: 50%;
  background: radial-gradient(circle, rgba(16,185,129,.10) 0%, transparent 65%);
  pointer-events: none;
}
.hero-lbl {
  font-size: 10px; font-weight: 600; color: rgba(148,163,184,.7);
  letter-spacing: .14em; text-transform: uppercase; margin: 0 0 10px 0;
  display: flex; align-items: center; gap: 8px;
}
.hero-lbl::before {
  content: ''; display: inline-block; width: 16px; height: 2px;
  background: var(--p); border-radius: 2px;
}
.hero-num {
  font-size: 56px; font-weight: 800; line-height: 1; letter-spacing: -0.025em;
  font-variant-numeric: tabular-nums; margin: 0;
  background: linear-gradient(130deg, #34d399 0%, #10b981 55%, #059669 100%);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
}
.hero-divider { border: none; border-top: 1px solid rgba(255,255,255,.07); margin: 16px 0 14px 0; }
.hero-sub {
  font-size: 13px; color: rgba(148,163,184,.8); margin: 0;
  display: flex; gap: 20px; flex-wrap: wrap; line-height: 1.6;
}
.hero-sub b { color: rgba(226,232,240,.9); font-weight: 600; }

/* ── KPI 4-col ── */
.kpi-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 14px; }
.kpi-box {
  background: var(--bg-surface); border: 1px solid var(--bd);
  border-left: 3px solid var(--p);
  border-radius: 12px; padding: 20px 18px 18px;
  box-shadow: 0 1px 2px rgba(0,0,0,.04), 0 4px 12px rgba(0,0,0,.04);
}
.kpi-box.k-saving  { border-left-color: var(--success); }
.kpi-box.k-roi     { border-left-color: var(--p); }
.kpi-box.k-payback { border-left-color: var(--warning); }
.kpi-box.k-cost    { border-left-color: var(--neutral); }

.kpi-lbl { font-size: 10px; font-weight: 600; color: var(--text-4); letter-spacing: .10em; text-transform: uppercase; margin: 0 0 8px 0; }
.kpi-val           { font-size: 26px; font-weight: 800; color: var(--text-1); font-variant-numeric: tabular-nums; margin: 0; letter-spacing: -0.015em; line-height: 1.15; }
.kpi-val.k-saving  { color: var(--success); }
.kpi-val.k-roi     { color: var(--p); }
.kpi-val.k-payback { color: var(--warning); }
.kpi-val.k-cost    { color: var(--neutral); }
.kpi-sub { font-size: 11px; color: var(--text-4); margin: 5px 0 0 0; line-height: 1.5; }

/* ── Cards ── */
.card { background: var(--bg-surface); border: 1px solid var(--bd); border-radius: 12px; padding: 22px 24px; margin-bottom: 12px; box-shadow: 0 1px 2px rgba(0,0,0,.04), 0 4px 12px rgba(0,0,0,.03); }
.card-lbl   { font-size: 10px; font-weight: 600; color: var(--text-4); letter-spacing: .10em; text-transform: uppercase; margin: 0 0 12px 0; }
.card-title { font-size: 17px; font-weight: 600; color: var(--text-1); margin: 0 0 14px 0; line-height: 1.35; }

/* ── Channel table ── */
.ch-table { width: 100%; border-collapse: separate; border-spacing: 0; font-size: 12px; margin-bottom: 8px; }
.ch-table th {
  text-align: left; font-size: 10px; font-weight: 600; color: var(--text-4);
  text-transform: uppercase; letter-spacing: .08em;
  padding: 0 10px 10px 10px; border-bottom: 2px solid var(--bd);
}
.ch-table td { padding: 8px 10px; border-bottom: 1px solid var(--bd-sub); color: var(--text-3); line-height: 1.4; }
.ch-table tr:last-child td { border-bottom: none; }
.ch-table .num  { text-align: right; font-variant-numeric: tabular-nums; }
.ch-table .bold { font-weight: 700; color: var(--text-1); }
.ch-highlight td { background: var(--p-surface); color: var(--p); font-weight: 600; }
.ch-highlight td:first-child { border-left: 3px solid var(--p); padding-left: 7px; }

/* ── Detail rows ── */
.dr { display: flex; justify-content: space-between; align-items: center; padding: 7px 0; font-size: 13px; color: var(--text-3); border-bottom: 1px solid var(--bd-sub); line-height: 1.5; }
.dr.sep  { border-top: 1px solid var(--bd); margin-top: 4px; padding-top: 10px; }
.dr.bold { font-weight: 700; font-size: 14px; color: var(--text-1); }
.dr.last { border-bottom: none; }
.dv   { font-variant-numeric: tabular-nums; white-space: nowrap; }
.dv-g { color: var(--success); font-variant-numeric: tabular-nums; white-space: nowrap; font-weight: 600; }
.dv-s { color: var(--neutral); font-variant-numeric: tabular-nums; white-space: nowrap; }
.dv-r { color: var(--danger);  font-variant-numeric: tabular-nums; white-space: nowrap; }

/* ── Spot comparison ── */
.spot-grid { display: grid; grid-template-columns: 1fr 32px 1fr; align-items: center; gap: 4px; margin-bottom: 12px; }
.spot-box { border: 1px solid var(--bd-sub); border-radius: 10px; padding: 14px 16px; background: var(--bg-page); }
.spot-box.after { border-color: var(--p-border); background: var(--p-surface); }
.spot-tag { font-size: 10px; font-weight: 600; color: var(--text-4); text-transform: uppercase; letter-spacing: .06em; margin: 0 0 5px 0; }
.spot-val { font-size: 20px; font-weight: 700; color: var(--text-1); font-variant-numeric: tabular-nums; }
.spot-box.after .spot-val { color: var(--p); }
.spot-note { font-size: 11px; color: var(--text-4); margin: 3px 0 0 0; line-height: 1.5; }
.arrow-c { text-align: center; color: #cbd5e1; font-size: 20px; }

/* ── Save badge ── */
.save-badge {
  display: inline-flex; align-items: center; gap: 5px;
  background: linear-gradient(135deg, var(--success-surface) 0%, #d1fae5 100%);
  color: #15803d; border: 1px solid var(--success-border);
  border-radius: 8px; padding: 6px 14px; font-size: 13px; font-weight: 700;
  box-shadow: 0 1px 3px rgba(16,185,129,.15);
}
.save-badge::before { content: '↓'; font-weight: 900; }

/* ── Warn note ── */
.warn { font-size: 11px; color: #78350f; background: var(--warning-surface); border: 1px solid var(--warning-border); border-radius: 8px; padding: 8px 12px; margin-top: 12px; line-height: 1.6; }

/* ── Saving preview (input tab) ── */
.saving-preview {
  margin-top: 20px; padding: 18px 20px;
  background: var(--p-surface); border: 1px solid var(--p-border); border-radius: 12px;
}
.saving-preview-lbl { font-size: 10px; font-weight: 600; color: var(--text-4); letter-spacing: .10em; text-transform: uppercase; margin: 0 0 6px 0; }
.saving-preview-num { font-size: 30px; font-weight: 800; color: var(--p); margin: 0; font-variant-numeric: tabular-nums; letter-spacing: -0.015em; }
.saving-preview-hint { font-size: 12px; color: var(--text-4); margin: 6px 0 0 0; line-height: 1.5; }

/* ── Button ── */
.stButton > button {
  background: var(--p) !important; color: #fff !important;
  border: none !important; border-radius: 8px !important;
  padding: 9px 22px !important; font-size: 13px !important; font-weight: 500 !important;
  transition: all 0.15s ease !important;
}
.stButton > button:hover {
  background: var(--p-hover) !important;
  box-shadow: 0 4px 12px rgba(43,112,239,.3) !important;
  transform: translateY(-1px) !important;
}

/* ── Print ── */
.print-header { display: none; }
@media print {
  [data-testid="stSidebar"] { display: none !important; }
  .stApp { background: white !important; }
  .block-container { padding: 0 !important; max-width: 100% !important; }
  .print-header { display: block !important; margin-bottom: 20px; }
  .ph-title { font-size: 11px; color: var(--text-4); letter-spacing: .08em; text-transform: uppercase; margin: 0; }
  .ph-name  { font-size: 22px; font-weight: 700; color: var(--text-1); margin: 4px 0 0 0; }
  .ph-line  { border: none; border-top: 2px solid var(--p); margin: 10px 0 0 0; }
  .hero { background: #0f172a !important; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  .hero-num { -webkit-text-fill-color: #34d399 !important; background: none !important; }
  @page { margin: 12mm 15mm; size: A4; }
}
</style>
""", unsafe_allow_html=True)

# ══ Helpers ════════════════════════════════════════════════════
def sldr(label, key, mn, mx, step, fmt_fn, hint=""):
    v = st.session_state.get(key, mn)
    st.markdown(
        f'<div class="srow">'
        f'<span class="slbl">{label}</span>'
        f'<span class="sval">{fmt_fn(v)}</span>'
        f'</div>',
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
    is_on = st.session_state.get(f'{sec}_on', False)
    row_cls  = f"sec-header {'is-on' if is_on else ''}"
    lbl_cls  = f"sec-lbl{'' if is_on else ' off'}"
    stat_cls = f"sec-status {'on' if is_on else 'off'}"
    stat_txt = "有効" if is_on else "無効"
    c1, c2 = st.columns([5, 1])
    with c1:
        st.markdown(
            f'<div class="{row_cls}">'
            f'<p class="{lbl_cls}">{label}</p>'
            f'<span class="{stat_cls}">{stat_txt}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )
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
    edited = edited.fillna({'チャネル名': '', '構成比(%)': 0, '採用単価(円)': 0})
    edited['構成比(%)']      = edited['構成比(%)'].astype(int)
    edited['採用単価(円)']   = edited['採用単価(円)'].astype(int)
    edited['採用人数']        = (edited['構成比(%)'] / 100 * hires).round().astype(int)
    edited['年間コスト(万円)'] = ((edited['採用人数'] * edited['採用単価(円)']) / 10_000).round().astype(int)

    total_ratio = int(edited['構成比(%)'].sum())
    remaining   = 100 - total_ratio
    if total_ratio > 100:
        cls, icon, msg = "error", "✕", f"合計 {total_ratio}%（{total_ratio-100}% 超過しています）"
    elif total_ratio == 100:
        cls, icon, msg = "ok",    "✓", "合計 100%（OK）"
    else:
        cls, icon, msg = "warn",  "○", f"合計 {total_ratio}%（残り {remaining}%）"
    st.markdown(
        f'<div class="val-ind {cls}"><span>{icon}</span><span>{msg}</span></div>',
        unsafe_allow_html=True,
    )
    return edited

# ══ Sidebar ════════════════════════════════════════════════════
with st.sidebar:
    st.markdown(
        '<div class="nav-brand">'
        '<div class="nav-brand-icon">T</div>'
        '<div><p class="nav-logo">TUNAGアルムナイ</p>'
        '<p class="nav-sub">採用費シミュレーター</p></div>'
        '</div>',
        unsafe_allow_html=True,
    )
    active_tab = st.radio(
        "",
        ["入力", "結果"],
        label_visibility="collapsed",
        key="active_tab_radio",
    )

# ══ 入力タブ ════════════════════════════════════════════════════
if active_tab == "入力":
    st.markdown('<p class="pg-title">採用費シミュレーター</p>', unsafe_allow_html=True)
    st.markdown('<p class="pg-sub">採用コスト・離職データを入力してください</p>', unsafe_allow_html=True)

    st.markdown('<p class="company-lbl">顧客企業名</p>', unsafe_allow_html=True)
    company_name = st.text_input(
        "", placeholder="例）〇〇株式会社",
        label_visibility="collapsed", key="company_name_input",
    )
    st.session_state['company_name'] = company_name

    results_cache = {}
    for sec, meta in SECTIONS.items():
        st.markdown('<hr class="sec-divider">', unsafe_allow_html=True)
        section_header(sec, meta['label'])

        if not st.session_state.get(f'{sec}_on', False):
            continue

        max_h  = 5000 if sec == 'part' else 500
        step_h = 50   if sec == 'part' else 10
        hires = sldr('年間採用数', f'{sec}_hires', 0, max_h, step_h, lambda v: f'{v:,}名')

        edited       = render_ch_editor(sec, hires)
        current_cost = int((edited['採用人数'] * edited['採用単価(円)']).sum())

        st.markdown('<hr class="sec-divider" style="margin:14px 0">', unsafe_allow_html=True)
        st.markdown('<p class="field-lbl">アルムナイ復職（OB/OG採用）</p>', unsafe_allow_html=True)

        max_l = 5000 if sec == 'part' else 500
        leavers  = sldr('年間離職者数',    f'{sec}_leavers',  0, max_l, step_h, lambda v: f'{v:,}名')
        reg_rate = sldr('アルムナイ登録率', f'{sec}_reg_rate', 0, 100, 1, lambda v: f'{v}%',
                        hint='退職者のうちTUNAGに登録する割合（実績: 20〜40%）')
        ret_rate = sldr('復帰率',          f'{sec}_ret_rate', 0,  50, 1, lambda v: f'{v}%',
                        hint='登録者のうち実際に復帰する割合（実績: 5〜15%）')

        ch_names = [r for r in edited['チャネル名'].tolist() if str(r).strip()]
        if not ch_names:
            ch_names = ['（チャネルなし）']
        replace_ch   = st.selectbox('復帰者が代替するチャネル', options=ch_names, key=f'{sec}_replace_ch')
        matched      = edited[edited['チャネル名'] == replace_ch]
        replace_unit = int(matched.iloc[0]['採用単価(円)']) if not matched.empty else 0

        alumni_returns = leavers * reg_rate / 100 * ret_rate / 100
        saving = alumni_returns * replace_unit

        results_cache[sec] = {
            'label': meta['label'], 'hires': hires, 'current_cost': current_cost,
            'ch_data': edited.to_dict('records'),
            'alumni_returns': alumni_returns, 'replace_ch': replace_ch,
            'replace_unit': replace_unit, 'saving': saving,
        }

    st.session_state['results_cache'] = results_cache

    # スポットワーク
    st.markdown('<hr class="sec-divider">', unsafe_allow_html=True)
    section_header('spot', 'スポットワーク手数料削減（タイミー代替）')

    spot_cache = {}
    if st.session_state.get('spot_on', False):
        st.markdown('<p class="field-lbl">現状（タイミー利用）</p>', unsafe_allow_html=True)
        workers    = sldr('月間スポットワーカー数', 'spot_workers',     0, 1000, 10, lambda v: f'{v:,}人')
        wage       = sldr('平均時給',               'spot_wage',      800, 3000, 50, lambda v: f'¥{v:,}')
        hours      = sldr('平均勤務時間 / 件',       'spot_hours',      1,   12,  1, lambda v: f'{v}h')
        timee_rate = sldr('タイミー手数料率',         'spot_timee_rate', 5,   50,  1, lambda v: f'{v}%')

        st.markdown('<hr class="sec-divider" style="margin:14px 0">', unsafe_allow_html=True)
        st.markdown('<p class="field-lbl">TUNAGアルムナイでの充足</p>', unsafe_allow_html=True)
        fulfill_rate = sldr('スポットワーク充足率', 'spot_fulfill_rate', 0, 100, 1, lambda v: f'{v}%',
                            hint='スポット需要のうちTUNAGアルムナイで充足できる割合')

        tunag_workers  = workers * fulfill_rate / 100
        timee_workers  = workers - tunag_workers
        current_annual = workers * wage * hours * timee_rate / 100 * 12
        new_annual     = (tunag_workers * wage * hours * 0.10
                          + timee_workers * wage * hours * timee_rate / 100) * 12
        spot_saving    = current_annual - new_annual
        spot_cache = {
            'workers': workers, 'wage': wage, 'hours': hours, 'timee_rate': timee_rate,
            'fulfill_rate': fulfill_rate, 'tunag_workers': tunag_workers,
            'timee_workers': timee_workers, 'current_annual': current_annual,
            'new_annual': new_annual, 'saving': spot_saving,
        }

    st.session_state['spot_cache'] = spot_cache

    # TUNAG利用料
    st.markdown('<hr class="sec-divider">', unsafe_allow_html=True)
    with st.expander('詳細設定（TUNAG利用料）'):
        c1, c2 = st.columns(2)
        with c1:
            st.number_input('初期費用（円）',   min_value=0, value=500_000, step=50_000, format='%d', key='initial_fee')
        with c2:
            st.number_input('月額利用料（円）', min_value=0, value=200_000, step=10_000, format='%d', key='monthly_fee')

    # 小計プレビュー
    recruit_saving = sum(r['saving'] for r in results_cache.values())
    spot_saving    = spot_cache.get('saving', 0)
    total_saving   = recruit_saving + spot_saving
    if total_saving > 0:
        st.markdown(f"""
        <div class="saving-preview">
          <p class="saving-preview-lbl">推計 年間削減効果</p>
          <p class="saving-preview-num">約 {man(total_saving)}</p>
          <p class="saving-preview-hint">「結果」タブで詳細・ROI・回収期間を確認できます</p>
        </div>
        """, unsafe_allow_html=True)

# ══ 結果タブ ════════════════════════════════════════════════════
else:
    results_cache = st.session_state.get('results_cache', {})
    spot_cache    = st.session_state.get('spot_cache', {})
    display_name  = st.session_state.get('company_name', '').strip() or '貴社'
    initial_fee   = st.session_state.get('initial_fee', 500_000)
    monthly_fee   = st.session_state.get('monthly_fee', 200_000)

    recruit_saving = sum(r['saving'] for r in results_cache.values())
    spot_saving    = spot_cache.get('saving', 0)
    total_saving   = recruit_saving + spot_saving
    tunag_y1       = initial_fee + monthly_fee * 12
    tunag_y2       = monthly_fee * 12
    net_y1         = total_saving - tunag_y1
    net_y2         = total_saving - tunag_y2
    roi            = total_saving / tunag_y2 if tunag_y2 > 0 else 0
    pb_months      = tunag_y1 / (total_saving / 12) if total_saving > 0 else float('inf')
    monthly_sav    = total_saving / 12
    pb_str         = f'{pb_months:.0f}ヶ月' if pb_months != float('inf') else '—'

    # Print header
    st.markdown(f"""
    <div class="print-header">
      <p class="ph-title">TUNAGアルムナイ 費用対効果試算書</p>
      <p class="ph-name">{display_name} 御中</p>
      <hr class="ph-line">
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f'<p class="pg-title">{display_name} 御中　試算結果</p>', unsafe_allow_html=True)
    st.markdown('<p class="pg-sub">入力タブの値をもとに算出した費用対効果です</p>', unsafe_allow_html=True)

    if not results_cache and not spot_cache:
        st.info("まず「入力」タブでデータを入力してください。")
    else:
        # ── Hero ──
        hero_sub_parts = []
        if recruit_saving > 0:
            hero_sub_parts.append(f'採用費削減 <b>{man(recruit_saving)}</b>')
        if spot_saving > 0:
            hero_sub_parts.append(f'スポット削減 <b>{man(spot_saving)}</b>')
        hero_sub_parts.append(f'TUNAG費 <b>{man(tunag_y1)}</b>')

        st.markdown(f"""
        <div class="hero">
          <p class="hero-lbl">年間コスト削減効果（合計）</p>
          <p class="hero-num">約 {man(total_saving)}</p>
          <hr class="hero-divider">
          <div class="hero-sub">{'&emsp;'.join(hero_sub_parts)}</div>
        </div>
        """, unsafe_allow_html=True)

        # ── KPI 4-column ──
        roi_cls = 'kpi-val k-roi'
        pb_cls  = 'kpi-val k-payback'
        st.markdown(f"""
        <div class="kpi-row">
          <div class="kpi-box k-saving">
            <p class="kpi-lbl">年間削減効果</p>
            <p class="kpi-val k-saving">{man(total_saving)}</p>
            <p class="kpi-sub">採用費＋スポット手数料</p>
          </div>
          <div class="kpi-box k-roi">
            <p class="kpi-lbl">ROI（2年目以降）</p>
            <p class="{roi_cls}">{roi:.1f}x</p>
            <p class="kpi-sub">TUNAG費1円あたり {roi:.1f}円の削減</p>
          </div>
          <div class="kpi-box k-payback">
            <p class="kpi-lbl">初期費用回収期間</p>
            <p class="{pb_cls}">{pb_str}</p>
            <p class="kpi-sub">月次削減額に基づく試算</p>
          </div>
          <div class="kpi-box k-cost">
            <p class="kpi-lbl">TUNAG利用料（初年度）</p>
            <p class="kpi-val k-cost">{man(tunag_y1)}</p>
            <p class="kpi-sub">月額 {man(monthly_fee)}×12 ＋ 初期費用</p>
          </div>
        </div>
        """, unsafe_allow_html=True)

        # ── セクション別チャネル表 ──
        for sec, r in results_cache.items():
            edited  = pd.DataFrame(r['ch_data'])
            ch_rows = ''
            for _, row in edited.iterrows():
                name = str(row['チャネル名']).strip()
                if not name:
                    continue
                is_replace = (name == r['replace_ch'])
                tr_cls = ' class="ch-highlight"' if is_replace else ''
                badge  = '&nbsp;<span style="font-size:9px;font-weight:700;color:var(--p);background:var(--p-surface);border:1px solid var(--p-border);border-radius:4px;padding:1px 5px;letter-spacing:.03em">代替</span>' if is_replace else ''
                ch_rows += f"""
                <tr{tr_cls}>
                  <td>{name}{badge}</td>
                  <td class="num">{row['構成比(%)']:.0f}%</td>
                  <td class="num">{row['採用人数']:,}名</td>
                  <td class="num">¥{row['採用単価(円)']:,}</td>
                  <td class="num bold">{row['年間コスト(万円)']:,}万円</td>
                </tr>"""

            alumni_n = r['alumni_returns']
            save     = r['saving']
            st.markdown(f"""
            <div class="card">
              <p class="card-title">{r['label']}</p>
              <table class="ch-table">
                <thead>
                  <tr>
                    <th>チャネル</th>
                    <th style="text-align:right">構成比</th>
                    <th style="text-align:right">採用人数</th>
                    <th style="text-align:right">採用単価</th>
                    <th style="text-align:right">年間コスト</th>
                  </tr>
                </thead>
                <tbody>{ch_rows}</tbody>
              </table>
              <div style="margin-top:12px;padding-top:12px;border-top:1px solid var(--bd-sub);display:flex;align-items:center;flex-wrap:wrap;gap:10px">
                <span style="font-size:12px;color:var(--text-3)">アルムナイ復職: <b style="color:var(--text-1)">{alumni_n:.1f}名/年</b>&nbsp;×&nbsp;{r['replace_ch']}単価 ¥{r['replace_unit']:,}</span>
                <span class="save-badge">削減　{man(save)} / 年</span>
              </div>
            </div>
            """, unsafe_allow_html=True)

        # ── スポットワーク ──
        if spot_cache:
            sr = spot_cache
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
            for r in results_cache.values()
        )
        spot_row = dr('　スポットワーク手数料削減', '＋' + man(spot_saving), 'dv-g') if spot_cache else ''

        st.markdown(f"""
        <div class="card">
          <p class="card-lbl">費用対効果まとめ</p>
          {sec_rows}
          {spot_row}
          {dr('合計削減効果', '＋' + man(total_saving), 'dv-g', bold=True, sep=True)}
          {dr('TUNAG年間費用（初年度: 初期＋月額×12）', '−' + man(tunag_y1), 'dv-s', sep=True)}
          {dr('TUNAG年間費用（2年目以降: 月額×12）',   '−' + man(tunag_y2), 'dv-s')}
          {dr('純削減額（初年度）',    man(abs(net_y1)), s1c, bold=True, sep=True)}
          {dr('純削減額（2年目以降）', man(abs(net_y2)), s2c, bold=True, last=True)}
          <div class="warn">※ アルムナイ採用単価はゼロで試算（TUNAGアルムナイ経由の1名あたり追加コストは発生しないため）。登録率・復職率はTUNAGアルムナイ導入企業の実績値に基づく参考値です。</div>
        </div>
        """, unsafe_allow_html=True)

        # ── PDF ──
        st.markdown('<div style="margin-top:16px">', unsafe_allow_html=True)
        if st.button('PDF保存 / 印刷', use_container_width=False):
            components.html('<script>window.print();</script>', height=0)
        st.markdown('</div>', unsafe_allow_html=True)
