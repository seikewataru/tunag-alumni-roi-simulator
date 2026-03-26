import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="TUNAGアルムナイ｜採用費シミュレーター",
    page_icon="📊",
    layout="wide",
)

DEFAULTS = dict(
    hires=1000,
    leavers=900,
    agency_ratio=65,
    agency_unit=850_000,
    register_rate=30,
    return_rate=10,
)
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

st.markdown("""
<style>
/* ── Base ── */
.stApp { background: #f9fafb; }
.block-container { padding: 28px 32px 48px !important; max-width: 1120px !important; }
* {
  font-family: "Inter", "Noto Sans JP", "Hiragino Sans", sans-serif !important;
}
footer, #MainMenu, header[data-testid="stHeader"],
[data-testid="stToolbar"], .stDeployButton,
[data-testid="stDecoration"] { display: none !important; }

/* ── Page title: text-2xl font-bold text-brand-black ── */
.pg-title { font-size: 24px; font-weight: 700; color: #0f172a; margin: 0 0 4px 0; line-height: 1.3 !important; }
/* ── Subtitle: text-sm text-gray-400 ── */
.pg-sub { font-size: 14px; color: #94a3b8; margin: 0 0 24px 0; line-height: 1.6 !important; }

/* ── Left column card: rounded-xl border border-slate-200 bg-white p-6 shadow-sm ── */
[data-testid="column"]:first-child > div:first-child {
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 24px 24px 28px !important;
  box-shadow: 0 1px 3px rgba(0,0,0,.05);
}

/* ── Section heading: text-lg font-semibold text-brand-black ── */
.sec-lbl {
  font-size: 15px; font-weight: 600; color: #0f172a;
  margin: 0 0 10px 0; line-height: 1.4 !important;
}

/* ── Divider ── */
.sec-divider { border: none; border-top: 1px solid #f1f5f9; margin: 20px 0 16px 0; }

/* ── Company label: text-xs font-medium uppercase tracking-wide text-gray-400 ── */
.company-lbl {
  font-size: 11px; font-weight: 500; color: #94a3b8;
  letter-spacing: 0.08em; text-transform: uppercase; margin: 0 0 6px 0;
}

/* ── Text input: rounded border border-slate-200 px-3 py-1.5 text-sm ── */
div[data-testid="stTextInput"] input {
  border-radius: 6px !important;
  border: 1px solid #e2e8f0 !important;
  font-size: 14px !important;
  color: #0f172a !important;
  background: #fff !important;
  padding: 8px 12px !important;
}
div[data-testid="stTextInput"] input:focus {
  border-color: #2b70ef !important;
  outline: none !important;
  box-shadow: 0 0 0 3px rgba(43,112,239,.1) !important;
}

/* ── Slider label row ── */
.srow {
  display: flex; justify-content: space-between; align-items: center;
  margin: 14px 0 2px 0;
}
/* text-sm text-gray-500 */
.slbl { font-size: 13px; color: #64748b; font-weight: 400; }
/* text-sm font-semibold text-brand-black */
.sval { font-size: 13px; font-weight: 600; color: #0f172a; font-variant-numeric: tabular-nums; }
/* text-xs text-slate-400 */
.shint { font-size: 11px; color: #94a3b8; margin: -2px 0 4px 0; line-height: 1.6 !important; }

/* ── Slider (color controlled by config.toml primaryColor) ── */
div[data-testid="stSlider"] { margin-top: -2px !important; margin-bottom: 0 !important; }
div[data-testid="stSlider"] p { display: none !important; }

/* ── Number input ── */
label[data-testid="stWidgetLabel"] { font-size: 11px !important; color: #94a3b8 !important; }
div[data-testid="stNumberInput"] input {
  border-radius: 6px !important; border: 1px solid #e2e8f0 !important;
  font-size: 13px !important; color: #0f172a !important;
}
div[data-testid="stCheckbox"] label { font-size: 13px !important; color: #475569 !important; }
div[data-testid="stExpander"] summary { font-size: 12px !important; color: #64748b !important; }

/* ── Pill badge: bg-brand-lightest text-brand rounded-full ── */
.pill {
  display: inline-flex; align-items: center;
  background: #f0f5ff; border: 1px solid #c0d4ff;
  border-radius: 20px; padding: 2px 10px;
  font-size: 11px; font-weight: 600; color: #2b70ef;
  margin: 4px 0 0 4px;
}

/* ── Hero ── */
.hero {
  background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 100%);
  border-radius: 12px; padding: 24px 28px; margin-bottom: 12px;
}
/* text-xs font-medium uppercase tracking-wide */
.hero-lbl {
  font-size: 11px; font-weight: 500; color: rgba(255,255,255,.5);
  letter-spacing: .1em; text-transform: uppercase; margin: 0 0 6px 0;
}
/* text-2xl font-bold → hero is larger */
.hero-num {
  font-size: 48px; font-weight: 700; color: #fff;
  line-height: 1 !important; font-variant-numeric: tabular-nums; margin: 0;
}
/* text-sm text-gray-400 */
.hero-sub { font-size: 13px; color: rgba(255,255,255,.6); margin: 10px 0 0 0; line-height: 1.8 !important; }
.hero-sub b { color: rgba(255,255,255,.9); font-weight: 600; }

/* ── KPI row: 2-col grid ── */
.kpi-row { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 12px; }
/* rounded-xl border border-slate-200 bg-white p-6 shadow-sm */
.kpi-box {
  background: #fff; border: 1px solid #e2e8f0; border-radius: 12px;
  padding: 18px 20px; box-shadow: 0 1px 3px rgba(0,0,0,.05);
}
/* text-xs font-medium text-gray-400 uppercase tracking-wide */
.kpi-lbl {
  font-size: 11px; font-weight: 500; color: #94a3b8;
  letter-spacing: .08em; text-transform: uppercase; margin: 0 0 6px 0;
}
/* text-2xl font-bold */
.kpi-val   { font-size: 28px; font-weight: 700; color: #0f172a; font-variant-numeric: tabular-nums; margin: 0; }
.kpi-val-g { font-size: 28px; font-weight: 700; color: #059669; font-variant-numeric: tabular-nums; margin: 0; }
.kpi-val-r { font-size: 28px; font-weight: 700; color: #ef4444; font-variant-numeric: tabular-nums; margin: 0; }
/* text-sm text-gray-400 */
.kpi-sub { font-size: 12px; color: #94a3b8; margin: 4px 0 0 0; line-height: 1.6 !important; }

/* ── Before/After card: rounded-xl border border-slate-200 bg-white shadow-sm ── */
.cmp {
  background: #fff; border: 1px solid #e2e8f0; border-radius: 12px;
  padding: 20px 22px; margin-bottom: 12px; box-shadow: 0 1px 3px rgba(0,0,0,.05);
}
.cmp-lbl {
  font-size: 11px; font-weight: 500; color: #94a3b8;
  letter-spacing: .08em; text-transform: uppercase; margin: 0 0 14px 0;
}
.cmp-grid { display: grid; grid-template-columns: 1fr 32px 1fr; align-items: center; gap: 4px; }
/* Inner card: rounded-lg border border-slate-100 p-4 */
.cmp-box { border: 1px solid #f1f5f9; border-radius: 8px; padding: 14px 16px; background: #f8fafc; }
.cmp-box.after { border-color: #c0d4ff; background: #f0f5ff; }
/* text-xs font-medium text-gray-400 uppercase */
.cmp-tag {
  font-size: 10px; font-weight: 500; color: #94a3b8;
  text-transform: uppercase; letter-spacing: .06em; margin: 0 0 4px 0;
}
/* text-xl font-bold text-brand-black */
.cmp-val { font-size: 20px; font-weight: 700; color: #0f172a; font-variant-numeric: tabular-nums; margin: 0; }
.cmp-box.after .cmp-val { color: #2b70ef; }
/* text-xs text-slate-400 */
.cmp-note { font-size: 11px; color: #94a3b8; margin: 4px 0 0 0; }
.arrow { text-align: center; color: #cbd5e1; font-size: 20px; }
/* Save badge: rounded-full bg-green-50 text-green-800 border border-green-200 */
.save-badge {
  display: inline-flex; align-items: center; gap: 6px; margin-top: 12px;
  background: #f0fdf4; color: #166534; border: 1px solid #bbf7d0;
  border-radius: 8px; padding: 5px 12px; font-size: 12px; font-weight: 600;
}

/* ── Detail rows card ── */
.dtl {
  background: #fff; border: 1px solid #e2e8f0; border-radius: 12px;
  padding: 20px 22px; margin-bottom: 12px; box-shadow: 0 1px 3px rgba(0,0,0,.05);
}
.dtl-lbl {
  font-size: 11px; font-weight: 500; color: #94a3b8;
  letter-spacing: .08em; text-transform: uppercase; margin: 0 0 12px 0;
}
/* text-sm text-slate-600 */
.dr {
  display: flex; justify-content: space-between; align-items: center;
  padding: 7px 0; font-size: 13px; color: #475569; border-bottom: 1px solid #f8fafc;
}
.dr.sep { border-top: 1px solid #e2e8f0; margin-top: 4px; padding-top: 10px; }
.dr.bold { font-weight: 700; font-size: 14px; color: #0f172a; }
.dr.last { border-bottom: none; }
.dv   { font-variant-numeric: tabular-nums; white-space: nowrap; }
.dv-g { color: #059669; font-variant-numeric: tabular-nums; white-space: nowrap; }
.dv-r { color: #ef4444; font-variant-numeric: tabular-nums; white-space: nowrap; }

/* ── Sensitivity table ── */
/* Header: bg-gray-50 text-xs text-gray-400 font-medium */
.sh {
  display: grid; grid-template-columns: 1.2fr 1fr 1fr 1fr 1.5fr 1fr;
  font-size: 11px; font-weight: 500; color: #94a3b8; text-transform: uppercase;
  letter-spacing: .06em; padding: 0 8px 10px 8px; border-bottom: 1px solid #e2e8f0;
}
.sr {
  display: grid; grid-template-columns: 1.2fr 1fr 1fr 1fr 1.5fr 1fr;
  font-size: 13px; color: #475569; padding: 7px 8px; border-bottom: 1px solid #f8fafc;
}
/* Active row: bg-brand-lightest text-brand */
.sr.act {
  background: #f0f5ff; border-radius: 8px; color: #2b70ef;
  font-weight: 700; border-bottom: none; margin: 2px 0;
}

/* ── Disclaimer: text-xs text-slate-400 ── */
.warn {
  font-size: 11px; color: #78350f; background: #fffbeb; border: 1px solid #fde68a;
  border-radius: 8px; padding: 8px 12px; margin-top: 12px; line-height: 1.8 !important;
}

/* ── Button: rounded bg-brand-black text-white ── */
.stButton > button {
  background: #0f172a !important; color: #fff !important;
  border: none !important; border-radius: 6px !important;
  padding: 8px 20px !important; font-size: 13px !important;
  font-weight: 500 !important; cursor: pointer !important;
  transition: background .15s !important;
}
.stButton > button:hover { background: #334155 !important; }

/* ── Print ── */
.print-header { display: none; }
.print-only   { display: none; }
@media print {
  .stApp { background: white !important; }
  .block-container { padding: 0 !important; max-width: 100% !important; }
  [data-testid="stHorizontalBlock"] > div:first-child { display: none !important; }
  [data-testid="stHorizontalBlock"] > div:last-child {
    width: 100% !important; max-width: 100% !important; flex: none !important;
  }
  .print-header { display: block !important; margin-bottom: 20px; }
  .ph-title { font-size: 11px; color: #94a3b8; letter-spacing: .08em; text-transform: uppercase; margin: 0; }
  .ph-name  { font-size: 22px; font-weight: 700; color: #0f172a; margin: 4px 0 0 0; }
  .ph-line  { border: none; border-top: 2px solid #2b70ef; margin: 10px 0 0 0; }
  .print-only { display: block !important; }
  .cond-grid { display: grid; grid-template-columns: repeat(3,1fr); gap: 8px; margin-bottom: 16px; }
  .cond-box  { border: 1px solid #e2e8f0; border-radius: 8px; padding: 8px 10px; }
  .cond-lbl  { font-size: 9px; color: #94a3b8; font-weight: 500; text-transform: uppercase; margin: 0; }
  .cond-val  { font-size: 13px; font-weight: 600; color: #0f172a; margin: 2px 0 0 0; }
  .hero { background: #0f172a !important; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  .hero-num { font-size: 36px !important; }
  .kpi-val, .kpi-val-g, .kpi-val-r { font-size: 22px !important; }
  @page { margin: 12mm 15mm; size: A4; }
}
</style>
""", unsafe_allow_html=True)

# ── Page header: text-2xl font-bold text-brand-black ──
st.markdown("""
<p class="pg-title">TUNAGアルムナイ　採用費シミュレーター</p>
<p class="pg-sub">採用コスト・離職データを入力すると、TUNAGアルムナイ導入による削減効果をリアルタイムで算出します</p>
""", unsafe_allow_html=True)

left, right = st.columns([1, 1.5], gap="large")

# ════════════════════════════════════════════════════
# ヘルパー
# ════════════════════════════════════════════════════
def sldr(label, key, mn, mx, step, fmt_fn, hint=""):
    v = st.session_state.get(key, DEFAULTS.get(key, mn))
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

# ════════════════════════════════════════════════════
# 左カラム：入力
# ════════════════════════════════════════════════════
with left:
    # 社名: text-xs font-medium uppercase tracking-wide text-gray-400
    st.markdown('<p class="company-lbl">顧客企業名</p>', unsafe_allow_html=True)
    company_name = st.text_input("顧客企業名", placeholder="例）〇〇株式会社",
                                  label_visibility="collapsed")

    st.markdown('<hr class="sec-divider">', unsafe_allow_html=True)

    # ── 採用の現状: text-lg font-semibold ──
    st.markdown('<p class="sec-lbl">採用の現状</p>', unsafe_allow_html=True)
    annual_hires  = sldr("年間採用数", "hires", 0, 5000, 50, lambda v: f"{v:,}名")
    agency_ratio  = sldr("うち人材紹介の比率", "agency_ratio", 0, 100, 1, lambda v: f"{v}%")
    agency_hires_n = round(
        st.session_state.get("hires", 1000) * st.session_state.get("agency_ratio", 65) / 100
    )
    st.markdown(
        f'<p class="shint">→ 人材紹介経由の採用は年間'
        f'<span class="pill">{agency_hires_n:,}名</span></p>',
        unsafe_allow_html=True,
    )
    agency_unit = sldr("人材紹介　採用単価", "agency_unit", 0, 2_000_000, 50_000,
                        lambda v: f"¥{v:,}", hint="人材紹介会社への成功報酬（1名あたり）")

    st.markdown('<hr class="sec-divider">', unsafe_allow_html=True)

    # ── 離職の現状 ──
    st.markdown('<p class="sec-lbl">離職の現状</p>', unsafe_allow_html=True)
    annual_leavers = sldr("年間離職者数", "leavers", 0, 5000, 50, lambda v: f"{v:,}名")

    st.markdown('<hr class="sec-divider">', unsafe_allow_html=True)

    # ── アルムナイ活用の見込み ──
    st.markdown('<p class="sec-lbl">アルムナイ活用の見込み</p>', unsafe_allow_html=True)
    register_rate = sldr("アルムナイ登録率", "register_rate", 0, 100, 1, lambda v: f"{v}%",
                          hint="退職者のうちTUNAGに登録する割合（導入企業実績: 20〜40%）")
    return_rate   = sldr("アルムナイ復職率", "return_rate", 0, 50, 1, lambda v: f"{v}%",
                          hint="登録者のうち実際に復職する割合（導入企業実績: 5〜15%）")

    # ── 詳細設定 ──
    initial_fee = 500_000
    monthly_fee = 200_000
    use_spot    = False
    spot_count  = spot_wage = spot_hours = 0
    with st.expander("詳細設定（TUNAG利用料 / スポットワーク）"):
        c1, c2 = st.columns(2)
        with c1:
            initial_fee = st.number_input("初期費用（円）", min_value=0, value=500_000, step=50_000, format="%d")
        with c2:
            monthly_fee = st.number_input("月額利用料（円）", min_value=0, value=200_000, step=10_000, format="%d")
        use_spot = st.checkbox("スポットワーク（タイミー代替）効果も含める", value=False)
        if use_spot:
            spot_count = sldr("月間スポット勤務件数", "sc",   0,  500,  5, lambda v: f"{v}件")
            spot_wage  = sldr("平均時給",             "sw", 800, 3000, 50, lambda v: f"¥{v:,}")
            spot_hours = sldr("平均勤務時間/件",      "sh_h",  1,  12,  1, lambda v: f"{v}h")

# ════════════════════════════════════════════════════
# 計算
# ════════════════════════════════════════════════════
agency_hires   = annual_hires * agency_ratio / 100
current_cost   = agency_hires * agency_unit
alumni_returns = min(
    annual_leavers * (register_rate / 100) * (return_rate / 100),
    agency_hires,
)
new_agency     = max(0, agency_hires - alumni_returns)
new_cost       = new_agency * agency_unit
recruit_saving = current_cost - new_cost

spot_saving    = spot_count * 12 * spot_wage * spot_hours * 0.20 if use_spot else 0
total_saving   = recruit_saving + spot_saving
tunag_y1       = initial_fee + monthly_fee * 12
tunag_y2       = monthly_fee * 12
net_y1         = total_saving - tunag_y1
net_y2         = total_saving - tunag_y2
roi            = total_saving / tunag_y2 if tunag_y2 > 0 else 0
pb_months      = tunag_y1 / (total_saving / 12) if total_saving > 0 else float("inf")
monthly_save   = total_saving / 12

def man(n): return f"{n/10_000:.0f}万円"

# ════════════════════════════════════════════════════
# 右カラム：結果
# ════════════════════════════════════════════════════
with right:
    pb_str       = f"{pb_months:.0f}ヶ月" if pb_months != float("inf") else "—"
    display_name = company_name.strip() if company_name and company_name.strip() else "貴社"

    # 印刷ヘッダー（画面では非表示）
    st.markdown(f"""
    <div class="print-header">
      <p class="ph-title">TUNAGアルムナイ 費用対効果試算書</p>
      <p class="ph-name">{display_name} 御中</p>
      <hr class="ph-line">
    </div>
    """, unsafe_allow_html=True)

    # ── Hero ──
    sub_parts = [f"毎月 <b>約{man(monthly_save)}</b> の節約"]
    if pb_months != float("inf"):
        sub_parts.append(f"初期費用は <b>{pb_str}</b> で回収")

    st.markdown(f"""
    <div class="hero">
      <p class="hero-lbl">年間コスト削減効果（採用費）</p>
      <p class="hero-num">約&thinsp;{man(recruit_saving)}</p>
      <p class="hero-sub">{'　/　'.join(sub_parts)}</p>
    </div>
    """, unsafe_allow_html=True)

    # ── KPI: text-2xl font-bold ──
    roi_cls = "kpi-val" if roi >= 1 else "kpi-val-r"
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

    # ── Before/After: inner cards rounded-lg border border-slate-100 p-4 ──
    if current_cost > 0:
        pct = recruit_saving / current_cost * 100
        st.markdown(f"""
        <div class="cmp">
          <p class="cmp-lbl">人材紹介コスト比較（年間）</p>
          <div class="cmp-grid">
            <div class="cmp-box">
              <p class="cmp-tag">現状</p>
              <p class="cmp-val">{man(current_cost)}</p>
              <p class="cmp-note">人材紹介 {agency_hires:.0f}名 × ¥{agency_unit:,}</p>
            </div>
            <div class="arrow">→</div>
            <div class="cmp-box after">
              <p class="cmp-tag">導入後</p>
              <p class="cmp-val">{man(new_cost)}</p>
              <p class="cmp-note">アルムナイ復職 {alumni_returns:.0f}名が代替</p>
            </div>
          </div>
          <div><span class="save-badge">削減　{man(recruit_saving)} / 年　▼{pct:.0f}%</span></div>
        </div>
        """, unsafe_allow_html=True)

    # ── Detail rows ──
    def dr(label, val, cls="dv", bold=False, sep=False, last=False):
        rc = "dr" + (" bold" if bold else "") + (" sep" if sep else "") + (" last" if last else "")
        return f'<div class="{rc}"><span>{label}</span><span class="{cls}">{val}</span></div>'

    spot_dr = dr("　スポットワーク手数料削減（タイミー代替）", "＋" + man(spot_saving), "dv-g") if use_spot else ""
    s1c = "dv-g" if net_y1 >= 0 else "dv-r"
    s2c = "dv-g" if net_y2 >= 0 else "dv-r"

    # 印刷時のみ表示する入力条件
    st.markdown(f"""
    <div class="print-only">
      <div class="cond-grid">
        <div class="cond-box"><p class="cond-lbl">年間採用数</p><p class="cond-val">{annual_hires:,}名</p></div>
        <div class="cond-box"><p class="cond-lbl">人材紹介比率</p><p class="cond-val">{agency_ratio}%（{agency_hires:.0f}名/年）</p></div>
        <div class="cond-box"><p class="cond-lbl">人材紹介単価</p><p class="cond-val">¥{agency_unit:,}</p></div>
        <div class="cond-box"><p class="cond-lbl">年間離職者数</p><p class="cond-val">{annual_leavers:,}名</p></div>
        <div class="cond-box"><p class="cond-lbl">アルムナイ登録率</p><p class="cond-val">{register_rate}%（実績: 20〜40%）</p></div>
        <div class="cond-box"><p class="cond-lbl">アルムナイ復職率</p><p class="cond-val">{return_rate}%（実績: 5〜15%）</p></div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="dtl">
      <p class="dtl-lbl">費用対効果まとめ</p>
      {dr("現状の年間人材紹介コスト", man(current_cost))}
      {dr("導入後の年間人材紹介コスト", man(new_cost))}
      {dr("　採用コスト削減額", "＋" + man(recruit_saving), "dv-g", sep=True)}
      {spot_dr}
      {dr("合計削減効果", "＋" + man(total_saving), "dv-g", bold=True, sep=True)}
      {dr("TUNAG年間費用（初年度: 初期＋月額×12）", "−" + man(tunag_y1), "dv-r", sep=True)}
      {dr("TUNAG年間費用（2年目以降: 月額×12）", "−" + man(tunag_y2), "dv-r")}
      {dr("純削減額（初年度）", man(abs(net_y1)), s1c, bold=True, sep=True)}
      {dr("純削減額（2年目以降）", man(abs(net_y2)), s2c, bold=True, last=True)}
      <div class="warn">※ アルムナイ採用単価はゼロで試算しています（人材紹介会社への成功報酬が不要なため）。登録率・復職率はTUNAGアルムナイ導入企業の実績値に基づく参考値です。</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Sensitivity analysis ──
    with st.expander("最悪シナリオでも黒字か確認する"):
        scenarios = [("保守的", 20, 5), ("標準", 30, 10), ("楽観的", 40, 15)]
        rows = ""
        for sname, r_reg, r_ret in scenarios:
            s_ret  = min(annual_leavers * r_reg/100 * r_ret/100, agency_hires)
            s_save = s_ret * agency_unit
            s_roi  = s_save / tunag_y2 if tunag_y2 > 0 else 0
            act    = " act" if r_reg == register_rate and r_ret == return_rate else ""
            rows  += (
                f'<div class="sr{act}"><span>{sname}</span><span>{r_reg}%</span>'
                f'<span>{r_ret}%</span><span>{s_ret:.0f}名</span>'
                f'<span>{man(s_save)}</span><span>{s_roi:.1f}倍</span></div>'
            )
        st.markdown(f"""
        <div class="sh"><span>シナリオ</span><span>登録率</span><span>復職率</span>
          <span>復職数</span><span>採用削減</span><span>ROI</span></div>
        {rows}
        """, unsafe_allow_html=True)

    # ── Print button: rounded bg-brand-black text-white ──
    st.markdown("<div style='margin-top:20px'>", unsafe_allow_html=True)
    if st.button("PDF保存 / 印刷", use_container_width=False):
        components.html("<script>window.print();</script>", height=0)
    st.markdown("</div>", unsafe_allow_html=True)
