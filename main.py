import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# 1. 페이지 설정
st.set_page_config(page_title="AI Agent Tenggu's Investment", layout="wide", initial_sidebar_state="collapsed")

# 2. CSS 스타일 (기존 인프라 완벽 유지)
st.markdown("""
    <style>
    .stApp { 
        background: radial-gradient(circle at top right, #0d1b2a, #010409 70%); 
        color: #E0E0E0; 
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important;
    }
    .macro-container {
        display: flex; justify-content: space-between; background: rgba(0, 212, 255, 0.08);
        padding: 18px; border-radius: 12px; border: 1px solid rgba(0, 212, 255, 0.3); margin-bottom: 10px;
    }
    .macro-item { text-align: center; flex: 1; border-right: 1px solid rgba(255,255,255,0.1); }
    .macro-item:last-child { border-right: none; }
    .macro-label { font-size: 0.85rem; color: #8B949E; margin-bottom: 5px; }
    .macro-value { font-size: 1.2rem; font-weight: bold; color: #00D4FF; }
    
    .advice-box { 
        background: rgba(13, 25, 41, 0.85); 
        border: 1px solid rgba(0, 212, 255, 0.3); 
        padding: 25px; border-radius: 15px; margin-top: 20px; border-left: 10px solid #00D4FF;
        line-height: 1.8;
    }
    .report-title { color: #00D4FF; font-weight: 800; font-size: 1.4rem; margin-bottom: 15px; display: block; }
    .taenggu-summary { background: rgba(0, 212, 255, 0.05); padding: 18px; border-radius: 10px; margin-top: 20px; border: 1px dashed rgba(0,212,255,0.5); font-size: 0.95rem; }
    
    .briefing-container {
        background: rgba(0, 212, 255, 0.05);
        border: 1px solid rgba(0, 212, 255, 0.2);
        padding: 15px; border-radius: 10px; height: 100%;
    }
    .briefing-title { color: #00D4FF; font-weight: bold; margin-bottom: 8px; display: block; }
    .briefing-content { font-size: 0.92rem; line-height: 1.7; color: #CCCCCC; }
    
    .tenggu-img-alt {
        width: 300px; height: 200px; background: rgba(255,255,255,0.05);
        border-radius: 15px; display: flex; flex-direction: column;
        align-items: center; justify-content: center; border: 1px dashed #444;
    }
    hr { border: 0; border-top: 1px solid rgba(0, 212, 255, 0.2); margin: 20px 0; }
    </style>
    """, unsafe_allow_html=True)
# 2. CSS 스타일 (모바일 최적화 추가)
st.markdown("""
    <style>
    /* 기본 데스크탑 설정 */
    .stApp { 
        background: radial-gradient(circle at top right, #0d1b2a, #010409 70%); 
        color: #E0E0E0; 
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important;
    }
    .macro-container {
        display: flex; justify-content: space-between; background: rgba(0, 212, 255, 0.08);
        padding: 18px; border-radius: 12px; border: 1px solid rgba(0, 212, 255, 0.3); margin-bottom: 10px;
    }
    .macro-item { text-align: center; flex: 1; border-right: 1px solid rgba(255,255,255,0.1); }
    .macro-item:last-child { border-right: none; }
    .macro-label { font-size: 0.85rem; color: #8B949E; margin-bottom: 5px; }
    .macro-value { font-size: 1.2rem; font-weight: bold; color: #00D4FF; }
    
    .advice-box { 
        background: rgba(13, 25, 41, 0.85); 
        border: 1px solid rgba(0, 212, 255, 0.3); 
        padding: 25px; border-radius: 15px; margin-top: 20px; border-left: 10px solid #00D4FF;
        line-height: 1.8;
    }
    .report-title { color: #00D4FF; font-weight: 800; font-size: 1.4rem; margin-bottom: 15px; display: block; }
    .taenggu-summary { background: rgba(0, 212, 255, 0.05); padding: 18px; border-radius: 10px; margin-top: 20px; border: 1px dashed rgba(0,212,255,0.5); font-size: 0.95rem; }
    
    .briefing-container {
        background: rgba(0, 212, 255, 0.05);
        border: 1px solid rgba(0, 212, 255, 0.2);
        padding: 15px; border-radius: 10px; height: 100%;
    }
    .briefing-title { color: #00D4FF; font-weight: bold; margin-bottom: 8px; display: block; }
    .briefing-content { font-size: 0.92rem; line-height: 1.7; color: #CCCCCC; }

    /* [추가] 모바일 전용 반응형 폰트 조절 (768px 이하) */
    @media (max-width: 768px) {
        .macro-container { flex-wrap: wrap; gap: 10px; }
        .macro-item { border-right: none; min-width: 30%; margin-bottom: 10px; }
        .macro-value { font-size: 1rem; }
        .macro-label { font-size: 0.7rem; }
        .report-title { font-size: 1.1rem; }
        .briefing-title { font-size: 0.9rem; }
        .briefing-content { font-size: 0.8rem; line-height: 1.5; }
        .taenggu-summary { font-size: 0.8rem; padding: 12px; }
        h1 { font-size: 1.5rem !important; } /* 메인 타이틀 크기 조정 */
        .stApp p, .stApp span, .stApp div { font-size: 0.85rem !important; }
    }
    </style>
    """, unsafe_allow_html=True)

# 3. 데이터 엔진
@st.cache_data(ttl=60)
def get_macro_indicators():
    try:
        m_tickers = {"Exchange": "USDKRW=X", "DXY": "DX-Y.NYB", "Oil": "CL=F", "T10Y": "^TNX", "T2Y": "^IRX"}
        m_raw = yf.download(list(m_tickers.values()), period="30d", interval="1d", progress=False)['Close']
        vix_raw = yf.download("^VIX", period="1y", progress=False)['Close']
        vix_curr = float(vix_raw.iloc[-1].iloc[0]) if isinstance(vix_raw.iloc[-1], pd.Series) else float(vix_raw.iloc[-1])
        vix_min = float(vix_raw.min().min()); vix_max = float(vix_raw.max().max())
        fgi_val = 100 - ((vix_curr - vix_min) / (vix_max - vix_min) * 100)
        
        def get_val(df, col, idx=-1):
            target = df[col].dropna(); val = target.iloc[idx]
            return float(val.iloc[0]) if isinstance(val, pd.Series) else float(val)

        curr_ex = get_val(m_raw, "USDKRW=X")
        curr_dxy = get_val(m_raw, "DX-Y.NYB")
        curr_oil = get_val(m_raw, "CL=F")
        t10 = get_val(m_raw, "^TNX"); t2 = get_val(m_raw, "^IRX") / 10
        
        macro_score = 0
        if fgi_val > 50: macro_score += 1
        if curr_ex < 1350: macro_score += 1
        if (t10 - t2) > 0: macro_score += 1
        if curr_dxy < 104.0: macro_score += 1
        if curr_oil < 85: macro_score += 1

        # 5대 AI 반영: 매크로 해석 추가
        if macro_score >= 4:
            macro_msg = "💎 매크로 매우 긍정: 추가 매수가 유리한 환경입니다."
        elif macro_score == 3:
            macro_msg = "⚖️ 매크로 중립: 기존 포지션을 유지하며 추세를 주시하세요."
        else:
            macro_msg = "⚠️ 매크로 부정: 위험 관리 및 현금 비중 확대를 권고합니다."

        return {
            "FGI": fgi_val, "Exchange": curr_ex, "DXY": curr_dxy, "Oil": curr_oil,
            "Spread": (t10 - t2), "Macro_Score": macro_score, "Macro_Msg": macro_msg
        }
    except:
        return None

@st.cache_data(ttl=30)
def fetch_data(ticker):
    try:
        df = yf.download(ticker, period='10y', interval='1d', progress=False, auto_adjust=True)
        if df.empty: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        df['MA20'] = df['Close'].rolling(window=20).mean()
        std = df['Close'].rolling(window=20).std()
        df['BBU'] = df['MA20'] + (std * 2); df['BBL'] = df['MA20'] - (std * 2)
        delta = df['Close'].diff(); gain = (delta.where(delta > 0, 0)).rolling(14).mean(); loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        df['RSI'] = 100 - (100 / (1 + (gain / loss.replace(0, np.nan))))
        df['EMA12'] = df['Close'].ewm(span=12, adjust=False).mean(); df['EMA26'] = df['Close'].ewm(span=26, adjust=False).mean()
        df['MACD'] = df['EMA12'] - df['EMA26']; df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
        df['Hist'] = df['MACD'] - df['Signal']
        return df
    except: return None

# 4. 분석 및 차트 함수
def draw_cyber_chart(ticker, title, period_label, macro_data):
    full_df = fetch_data(ticker)
    if full_df is None:
        st.error(f"📡 {ticker} 데이터를 불러올 수 없습니다. 네트워크 상태를 확인하세요.")
        return
    
    period_map = {"1W": 7, "1M": 21, "6M": 126, "1Y": 252, "ALL": len(full_df)}
    df = full_df.iloc[-period_map.get(period_label, 21):].copy()
    last = full_df.iloc[-1]; prev = full_df.iloc[-2]
    
    rsi_val = float(last['RSI'])
    macd_val = float(last['Hist'])
    
    fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.05, 
                        row_heights=[0.5, 0.15, 0.35], subplot_titles=(f"{title}", f"RSI({rsi_val:.1f})", "MACD Energy"))
    
    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], 
                                increasing_line_color='#FF3333', decreasing_line_color='#3333FF', name="현재가"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['MA20'], line=dict(color='orange', width=1.2), name='MA20'), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], line=dict(color='#00D4FF', width=2), name="RSI"), row=2, col=1)
    fig.add_trace(go.Bar(x=df.index, y=df['Hist'], marker_color=['#FF3333' if v < 0 else '#00FF00' for v in df['Hist']], name="MACD"), row=3, col=1)

    fig.update_layout(height=700, template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)

    # 5대 AI 반영: 이격도 및 리스크 관리 로직
    close_price = float(last['Close']); ma20_val = float(last['MA20'])
    disparity = (close_price / ma20_val) * 100 if ma20_val != 0 else 100
    
    st.markdown(f'<div class="advice-box"><span class="report-title">🛰️ {title} 퀀트 전략 리포트</span>', unsafe_allow_html=True)
    q_briefing = [f"이격도({disparity:.1f}%) 기반 평균 회귀 분석"]
    
    if disparity > 110: q_briefing.append("‼️ <b>과열 경보:</b> 역사적 상단입니다. 비중 축소 및 수익 실현을 권장합니다.")
    elif disparity < 90: q_briefing.append("✅ <b>침체 구간:</b> 저가 매수 기회입니다. 기술적 반등 가능성이 높습니다.")
    else: q_briefing.append("안정적 추세 범위 내에 있습니다.")
    
    if close_price < ma20_val * 0.95:
        q_briefing.append("⚠️ <b>리스크 경보:</b> 20일선 대비 -5% 급락했습니다. 보수적 대응이 필요합니다.")
        
    st.markdown(f'<div class="taenggu-summary"><b>[AI 기술적 분석 종합 결과]</b><br>{" | ".join(q_briefing)}</div></div>', unsafe_allow_html=True)

# 5. 메인 레이아웃 실행
col_t, col_i = st.columns([7, 3])
with col_t:
    st.title("AI Agent Tenggu's Investment")
    st.write("Professional Quant Asset Management v4.3.7 (5-AI Multi-Insight)")
with col_i:
    try: st.image("tenggu.jpg", width=300)
    except: st.markdown('<div class="tenggu-img-alt"><span style="font-size:3rem;">🐶</span><br><b>Tenggu AI Agent</b></div>', unsafe_allow_html=True)

macro = get_macro_indicators()
if macro:
    st.markdown(f"""
        <div class="macro-container">
            <div class="macro-item"><div class="macro-label">공포탐욕지수</div><div class="macro-value">{macro['FGI']:.0f}</div></div>
            <div class="macro-item"><div class="macro-label">원/달러 환율</div><div class="macro-value">₩{macro['Exchange']:,.1f}</div></div>
            <div class="macro-item"><div class="macro-label">달러 인덱스</div><div class="macro-value">{macro['DXY']:.2f}</div></div>
            <div class="macro-item"><div class="macro-label">WTI 유가</div><div class="macro-value">${macro['Oil']:.2f}</div></div>
            <div class="macro-item"><div class="macro-label">장단기 금리차</div><div class="macro-value">{macro['Spread']:.3f}</div></div>
        </div>
        <div style="background: rgba(0, 212, 255, 0.15); padding: 10px; border-radius: 8px; text-align: center; border: 1px solid #00D4FF; margin-bottom: 20px; font-weight: bold;">
            {macro['Macro_Msg']} (Score: {macro['Macro_Score']}/5)
        </div>
        """, unsafe_allow_html=True)

    fgi_b = f"({macro['FGI']:.0f}): {'자산 거품 경계 필요' if macro['FGI']>75 else '공포 구간 저가 매수 유효' if macro['FGI']<40 else '중립적 심리'}"
    ex_b = f"(₩{macro['Exchange']:,.1f}): {'외인 수급 악화 주의' if macro['Exchange']>1360 else '수급 안정적'}"
    dxy_b = f"({macro['DXY']:.2f}): {'기술주 압박 지속' if macro['DXY']>104.5 else '기술주 모멘텀 양호'}"
    oil_b = f"(${macro['Oil']:.2f}): {'인플레이션 압력' if macro['Oil']>88 else '물가 하향 안정'}"
    spr_b = f"({macro['Spread']:.3f}): {'침체 신호 지속' if macro['Spread']<0 else '금융 시장 정상화'}"

    tab1, tab2 = st.tabs(["🇰🇷 KOREA", "🇺🇸 USA"])
    with tab1:
        col_k1, col_k2 = st.columns([1, 1])
        with col_k1:
            st.markdown(f'<div class="briefing-container"><span class="briefing-title">🐶 탱구의 5대 지표 브리핑</span><div class="briefing-content">① <b>공포</b> {fgi_b}<br>② <b>환율</b> {ex_b}<br>③ <b>달러</b> {dxy_b}<br>④ <b>유가</b> {oil_b}<br>⑤ <b>금리</b> {spr_b}</div></div>', unsafe_allow_html=True)
        with col_k2:
            ks_df = fetch_data("^KS200")
            if ks_df is not None:
                ks_rsi = ks_df['RSI'].iloc[-1]; ks_close = ks_df['Close'].iloc[-1]; ks_bbu = ks_df['BBU'].iloc[-1]
                rise_adv = "⚠️ <b>밴드 상단 이탈:</b> 상방 제한 리스크가 큽니다. 일부 익절 권장." if ks_close > ks_bbu else "안정적 박스권. <b>프리미엄 수익</b> 극대화 가능 구간."
                tiger_adv = "🔥 <b>강력 매수 타점:</b> 과매도 구간(RSI 35미만) 진입." if ks_rsi < 35 else "현재 추세 유지하며 분할 매수 대응."
                st.markdown(f'<div class="briefing-container"><span class="briefing-title">🇰🇷 국내 ETF 투자 전략</span><div class="briefing-content"><b>[Rise200커버드콜]:</b> {rise_adv}<br><br><b>[Tiger 레버리지]:</b> {tiger_adv}</div></div>', unsafe_allow_html=True)
        kr_range = st.radio("Range", ["1W", "1M", "6M", "1Y", "ALL"], index=1, horizontal=True, key="kr")
        draw_cyber_chart("^KS200", "KOSPI 200", kr_range, macro)

    with tab2:
        col_u1, col_u2 = st.columns([1, 1])
        with col_u1:
            st.markdown(f'<div class="briefing-container"><span class="briefing-title">🐶 탱구의 5대 지표 브리핑</span><div class="briefing-content">① <b>공포</b> {fgi_b}<br>② <b>환율</b> {ex_b}<br>③ <b>달러</b> {dxy_b}<br>④ <b>유가</b> {oil_b}<br>⑤ <b>금리</b> {spr_b}</div></div>', unsafe_allow_html=True)
        with col_u2:
            nas_df = fetch_data("^NDX"); sox_df = fetch_data("^SOX")
            if nas_df is not None and sox_df is not None:
                nas_rsi = nas_df['RSI'].iloc[-1]; sox_rsi = sox_df['RSI'].iloc[-1]
                m_score = macro['Macro_Score']
                if m_score >= 4 and nas_rsi < 60: qld_adv = "🚀 <b>풀파워 적립:</b> 매크로 최적기입니다. <b>적립금 2배 증액</b> 권고."
                elif nas_rsi > 70 or m_score <= 1: qld_adv = "🛑 <b>방어적 전환:</b> 과열 상태입니다. <b>적립금 0.5배 축소</b> 및 현금 확보."
                else: qld_adv = "안정적 정액 적립 구간입니다."
                soxl_adv = "과매도 진입. <b>공격적 분할 매수</b> 유효." if sox_rsi < 40 else "에너지 분산 중. 눌림목을 기다리세요."
                st.markdown(f'<div class="briefing-container"><span class="briefing-title">🇺🇸 미국 ETF 투자 전략</span><div class="briefing-content"><b>[QLD 적립 가이드]:</b> {qld_adv}<br><br><b>[SOXL 투자 가이드]:</b> {soxl_adv}</div></div>', unsafe_allow_html=True)
        us_range = st.radio("Range", ["1W", "1M", "6M", "1Y", "ALL"], index=1, horizontal=True, key="us")
        draw_cyber_chart("^NDX", "NASDAQ 100", us_range, macro)
        st.markdown("<br><hr><br>", unsafe_allow_html=True)
        draw_cyber_chart("^SOX", "PHLX SEMI", us_range, macro)
else:
    st.warning("📡 거시경제 데이터를 불러오는 중입니다. 잠시만 기다려 주세요.")
