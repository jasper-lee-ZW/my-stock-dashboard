import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(page_title="Stock Radar", layout="wide", page_icon="📈")

# 现代暗黑美化 CSS
st.markdown('''
<style>
    .main {background-color: #0a0a0a;}
    .header {background-color: #111827; padding: 1rem; border-radius: 12px; margin-bottom: 1.5rem;}
    .chip {background-color: #1f2937; padding: 0.5rem 1rem; border-radius: 9999px; margin: 0.3rem; display: inline-flex; align-items: center; font-weight: 600;}
    .stock-card {
        background-color: #1f2937; padding: 1.5rem; border-radius: 16px; 
        border: 1px solid #374151; transition: all 0.2s;
    }
    .stock-card:hover {border-color: #3b82f6; transform: translateY(-3px);}
    .positive {color: #22c55e; font-weight: bold;}
    .negative {color: #ef4444; font-weight: bold;}
</style>
''', unsafe_allow_html=True)

# 初始化
if 'tickers' not in st.session_state:
    st.session_state.tickers = ['AAPL', 'NVDA', 'TSLA', 'MSFT', '600519.SS']
if 'view' not in st.session_state:
    st.session_state.view = 'list'   # list 或 detail
if 'selected_ticker' not in st.session_state:
    st.session_state.selected_ticker = None

# Header（完全模仿第二张图）
st.markdown('<div class="header">', unsafe_allow_html=True)
col1, col2, col3 = st.columns([3, 4, 2])
with col1:
    st.title("📈 STOCK RADAR")
with col2:
    st.caption(f"更新于 {datetime.now().strftime('%Y/%m/%d %H:%M:%S')}   •   Yahoo Finance 真实数据")
with col3:
    if st.button("🔄 刷新", use_container_width=True, type="primary"):
        st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

# 自选股芯片区
st.subheader("自选股")
chip_container = st.container()
with chip_container:
    cols = st.columns(len(st.session_state.tickers) + 1)
    for i, ticker in enumerate(st.session_state.tickers):
        with cols[i]:
            if st.button(f"{ticker} ×", key=f"chip_{ticker}"):
                st.session_state.tickers.remove(ticker)
                if st.session_state.selected_ticker == ticker:
                    st.session_state.selected_ticker = st.session_state.tickers[0] if st.session_state.tickers else None
                st.rerun()

# 添加按钮（小而精致）
col_add, _ = st.columns([1, 5])
with col_add:
    if st.button("＋ 添加", type="primary", use_container_width=True):
        st.session_state.show_add = True

# 添加对话框（干净弹出）
@st.dialog("添加新股票")
def add_dialog():
    code = st.text_input("输入股票代码", placeholder="AAPL 或 600519.SS")
    if st.button("确认添加", type="primary"):
        if code:
            upper = code.strip().upper()
            if upper not in st.session_state.tickers:
                st.session_state.tickers.append(upper)
                st.success(f"✅ 已添加 {upper}")
                st.rerun()
            else:
                st.warning("已在列表中")
        else:
            st.error("请输入代码")
if st.session_state.get("show_add", False):
    add_dialog()
    st.session_state.show_add = False

# ====================== 主内容 ======================
if st.session_state.view == 'list':
    st.subheader(f"📋 股票列表（共 {len(st.session_state.tickers)} 只）")
    for ticker in st.session_state.tickers:
        try:
            t = yf.Ticker(ticker)
            info = t.info
            fast = t.fast_info
            name = info.get('longName') or info.get('shortName') or ticker
            price = fast.get('lastPrice') or info.get('currentPrice', 0)
            change = info.get('regularMarketChangePercent', 0)
            high = info.get('regularMarketDayHigh', 0)
            low = info.get('regularMarketDayLow', 0)
            vol = info.get('regularMarketVolume', 0)
            prev = info.get('regularMarketPreviousClose', 0)
            
            color_class = "positive" if change >= 0 else "negative"
            
            st.markdown(f"""
            <div class="stock-card">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div>
                        <h3 style="margin:0;">{name} <small style="color:#9ca3af;">({ticker})</small></h3>
                        <h2 style="margin:0.3rem 0;">{price:.2f} <span class="{color_class}">({change:+.2f}%)</span></h2>
                    </div>
                </div>
                <p style="margin:0; color:#9ca3af;">
                    昨收 {prev:.2f} | 高 {high:.2f} | 低 {low:.2f} | 量 {vol:,}
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("📈 查看 K 线 + 机构评级", key=f"view_{ticker}", use_container_width=True):
                st.session_state.selected_ticker = ticker
                st.session_state.view = 'detail'
                st.rerun()
        except:
            st.error(f"{ticker} 加载失败")

else:  # detail 页
    ticker = st.session_state.selected_ticker
    if st.button("← 返回列表", type="secondary"):
        st.session_state.view = 'list'
        st.rerun()
    
    t = yf.Ticker(ticker)
    info = t.info
    name = info.get('longName') or ticker
    
    st.header(f"{name} ({ticker})")
    
    # 指标
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("当前价", f"{info.get('currentPrice', 0):.2f}")
    with c2: st.metric("今日涨跌", f"{info.get('regularMarketChangePercent', 0):+.2f}%")
    with c3: st.metric("日最高", f"{info.get('regularMarketDayHigh', 0):.2f}")
    with c4: st.metric("目标价", f"{info.get('targetMeanPrice', 'N/A')}")
    
    # K线
    st.subheader("K 线走势图")
    tf = st.radio("切换周期", ["日K (最近1年)", "周K (最近5年)", "月K (全部历史)"], horizontal=True)
    period_map = {"日K (最近1年)": ("1y", "1d"), "周K (最近5年)": ("5y", "1wk"), "月K (全部历史)": ("max", "1mo")}
    period, interval = period_map[tf]
    
    hist = t.history(period=period, interval=interval)
    fig = go.Figure(data=[go.Candlestick(x=hist.index,
        open=hist['Open'], high=hist['High'],
        low=hist['Low'], close=hist['Close'],
        increasing_line_color='#22c55e', decreasing_line_color='#ef4444')])
    fig.update_layout(height=680, template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)
    
    # 机构评级
    st.subheader("🏦 机构买入评级")
    st.write(f"**推荐级别**：{info.get('recommendationKey', '暂无').upper()}")
    st.write(f"**分析师人数**：{info.get('numberOfAnalystOpinions', '暂无')}")
    try:
        rec = t.recommendations
        if not rec.empty:
            st.dataframe(rec.tail(12), use_container_width=True)
    except:
        st.info("暂无最新机构评级")

st.caption("数据来自 Yahoo Finance（近实时） • 完全免费 • Grok 专属定制")
