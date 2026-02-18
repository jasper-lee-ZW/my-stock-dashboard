import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="我的股票实时仪表盘", layout="wide", page_icon="📈", initial_sidebar_state="expanded")

st.title("📈 我的股票实时仪表盘")

# 默认股票（可随时修改）
if 'tickers' not in st.session_state:
    st.session_state.tickers = ['AAPL', 'TSLA', 'NVDA', '600519.SS', '000001.SS']  # 茅台 + 上证指数示例

# 侧边栏管理
with st.sidebar:
    st.header("📋 管理股票列表")
    new_ticker = st.text_input("添加股票代码（如 AAPL 或 600519.SS）")
    col_add, col_refresh = st.columns(2)
    with col_add:
        if st.button("➕ 添加"):
            if new_ticker and new_ticker.upper() not in [t.upper() for t in st.session_state.tickers]:
                st.session_state.tickers.append(new_ticker.upper())
                st.success(f"✅ 已添加 {new_ticker.upper()}")
                st.rerun()
    with col_refresh:
        if st.button("🔄 刷新数据"):
            st.rerun()

    st.subheader("当前列表")
    to_remove = st.multiselect("选择删除", st.session_state.tickers)
    if st.button("🗑 删除选中"):
        st.session_state.tickers = [t for t in st.session_state.tickers if t not in to_remove]
        st.rerun()

# 获取数据
@st.cache_data(ttl=60)  # 60秒自动刷新一次
def get_stock_data(symbols):
    data = []
    for sym in symbols:
        try:
            t = yf.Ticker(sym)
            info = t.fast_info
            full_info = t.info
            name = full_info.get('longName') or full_info.get('shortName') or sym
            data.append({
                '名称': name,
                '代码': sym,
                '涨跌%': round(info.get('regularMarketChangePercent', 0), 2),
                '日最高': round(info.get('regularMarketDayHigh', 0), 2),
                '日最低': round(info.get('regularMarketDayLow', 0), 2),
                '成交量': f"{int(info.get('regularMarketVolume', 0)):,}",
                '昨收': round(info.get('regularMarketPreviousClose', 0), 2),
                '当前价': round(info.get('lastPrice', info.get('regularMarketPrice', 0)), 2)
            })
        except:
            data.append({'名称': sym, '代码': sym, '涨跌%': 0, '日最高': 0, '日最低': 0, '成交量': '0', '昨收': 0, '当前价': 0})
    return pd.DataFrame(data)

df = get_stock_data(st.session_state.tickers)

# 美观表格
st.subheader(f"📊 我的股票列表（共 {len(df)} 只）")
def highlight_change(val):
    return f'color: {"#22c55e" if val > 0 else "#ef4444"}; font-weight: bold;'
styled = df.style.map(highlight_change, subset=['涨跌%']).format({
    '涨跌%': '{:.2f}%',
    '日最高': '{:.2f}', '日最低': '{:.2f}', '昨收': '{:.2f}', '当前价': '{:.2f}'
})
st.dataframe(styled, use_container_width=True, hide_index=True)

# 详情页
st.subheader("🔍 点这里查看详情")
selected = st.selectbox("选择股票", options=df['代码'], index=0)

if selected:
    ticker = yf.Ticker(selected)
    info = ticker.info
    st.divider()
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("当前价格", f"{info.get('currentPrice', info.get('regularMarketPrice', 0)):.2f}")
    with col2:
        change_pct = info.get('currentChangePercent', info.get('regularMarketChangePercent', 0))
        st.metric("今日涨跌", f"{change_pct:.2f}%", delta=None)
    with col3:
        st.metric("目标价", f"{info.get('targetMeanPrice', '暂无'):.2f}" if info.get('targetMeanPrice') else "暂无")

    # K线图
    st.subheader("📉 K线走势图")
    tf = st.radio("切换时间框架", ["日K线 (最近1年)", "周K线 (最近5年)", "月K线 (全部历史)"], horizontal=True, key="tf")
    if "日" in tf:
        period, interval = "1y", "1d"
    elif "周" in tf:
        period, interval = "5y", "1wk"
    else:
        period, interval = "max", "1mo"

    hist = ticker.history(period=period, interval=interval)
    fig = go.Figure(data=[go.Candlestick(
        x=hist.index,
        open=hist['Open'], high=hist['High'], low=hist['Low'], close=hist['Close'],
        increasing_line_color='#22c55e', decreasing_line_color='#ef4444'
    )])
    fig.update_layout(height=650, template="plotly_dark", xaxis_title="日期", yaxis_title="价格 (CNY/USD)")
    st.plotly_chart(fig, use_container_width=True)

    # 机构评级
    st.subheader("🏦 机构买入评级")
    col_a, col_b = st.columns(2)
    with col_a:
        st.write(f"**推荐级别**：{info.get('recommendationKey', '暂无').upper()}")
        st.write(f"**分析师人数**：{info.get('numberOfAnalystOpinions', '暂无')}")
    with col_b:
        st.write(f"**平均目标价**：{info.get('targetMeanPrice', '暂无'):.2f}")

    try:
        rec = ticker.recommendations
        if not rec.empty:
            st.dataframe(rec.tail(10), use_container_width=True)
        else:
            st.info("暂无最新机构评级数据")
    except:
        st.info("暂无机构评级数据")

st.caption("数据来源于 Yahoo Finance（免费近实时，市场延迟约15分钟） • 刷新页面或点击按钮即可更新 • 完全免费无广告")
