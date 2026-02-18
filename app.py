import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(page_title="Stock Radar", layout="wide", page_icon="📈")

st.markdown('''
<style>
    .main {background-color: #0a0a0a; color: #e2e8f0;}
    .header {background-color: #111827; padding: 1rem; border-radius: 16px; margin-bottom: 1.5rem;}
    .stock-card {background-color: #1f2937; padding: 1.5rem; border-radius: 16px; border: 1px solid #374151;}
    .stock-card:hover {border-color: #3b82f6;}
    .price-up {color: #22c55e; font-weight: bold;}
    .price-down {color: #ef4444; font-weight: bold;}
    .period-btn {border-radius: 8px; padding: 8px 16px; margin: 0 4px;}
    .active {background-color: #fbbf24 !important; color: black !important; font-weight: bold;}
</style>
''', unsafe_allow_html=True)

if 'tickers' not in st.session_state:
    st.session_state.tickers = ['AAPL', 'NVDA', 'TSLA', 'MSFT', '600519.SS']
if 'view' not in st.session_state:
    st.session_state.view = 'list'
if 'selected_ticker' not in st.session_state:
    st.session_state.selected_ticker = None
if 'period' not in st.session_state:
    st.session_state.period = "日K"

# Header
st.markdown('<div class="header">', unsafe_allow_html=True)
c1, c2, c3 = st.columns([3, 4, 2])
with c1:
    st.title("📈 STOCK RADAR")
with c2:
    st.caption(f"更新于 {datetime.now().strftime('%Y/%m/%d %H:%M:%S')} • Yahoo Finance 真实数据")
with c3:
    if st.button("🔄 刷新", type="primary", use_container_width=True):
        st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

# 自选股芯片
st.subheader("自选股")
cols = st.columns(len(st.session_state.tickers) + 1)
for i, t in enumerate(st.session_state.tickers):
    with cols[i]:
        if st.button(f"{t} ×", key=f"del_{t}", use_container_width=True):
            st.session_state.tickers.remove(t)
            st.rerun()

# 添加按钮
col_add, _ = st.columns([1, 6])
with col_add:
    if st.button("＋ 添加", type="primary", use_container_width=True):
        code = st.text_input("输入股票代码", placeholder="AAPL 或 600519.SS", key="add_code")
        if st.button("✅ 确认添加", type="primary"):
            if code and code.upper() not in st.session_state.tickers:
                st.session_state.tickers.append(code.upper())
                st.success(f"✅ 已添加 {code.upper()}")
                st.rerun()

if st.session_state.view == 'list':
    st.subheader(f"📋 我的股票列表（共 {len(st.session_state.tickers)} 只）")
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
            color = "price-up" if change >= 0 else "price-down"

            st.markdown(f'''
            <div class="stock-card">
                <div style="display:flex;justify-content:space-between;">
                    <div>
                        <h3 style="margin:0;">{name}</h3>
                        <h2 style="margin:0.4rem 0 0.2rem 0;">{price:.2f} <span class="{color}">({change:+.2f}%)</span></h2>
                        <p style="margin:0;color:#9ca3af;">{ticker}</p>
                    </div>
                </div>
                <p style="margin:1rem 0 0 0;color:#9ca3af;">
                    昨收 {prev:.2f} | 高 {high:.2f} | 低 {low:.2f} | 量 {vol:,}
                </p>
            </div>
            ''', unsafe_allow_html=True)

            if st.button("📈 查看详情", key=f"view_{ticker}", use_container_width=True):
                st.session_state.selected_ticker = ticker
                st.session_state.view = 'detail'
                st.rerun()
        except:
            st.error(f"{ticker} 数据加载失败")

else:  # ====================== 详情页（完全模仿你朋友第二张图） ======================
    ticker = st.session_state.selected_ticker
    if st.button("← 返回列表", type="secondary"):
        st.session_state.view = 'list'
        st.rerun()

    t = yf.Ticker(ticker)
    info = t.info
    name = info.get('longName') or ticker
    current_price = info.get('currentPrice', info.get('regularMarketPrice', 0))
    change_pct = info.get('regularMarketChangePercent', 0)
    change_val = info.get('regularMarketChange', 0)

    # 顶部（完全一样）
    col_l, col_r = st.columns([3, 2])
    with col_l:
        st.markdown(f"<h1 style='margin:0;'>{ticker}</h1><h3 style='margin:0;color:#9ca3af;'>{name}</h3>", unsafe_allow_html=True)
    with col_r:
        st.markdown(f"""
        <div style='text-align:right;'>
            <h1 style='margin:0;'>${current_price:.2f}</h1>
            <h2 class='{"price-down" if change_pct<0 else "price-up"}' style='margin:0;'> {change_val:+.2f} ({change_pct:+.2f}%)</h2>
        </div>
        """, unsafe_allow_html=True)

    # 切换按钮（完全一样）
    period_options = ["日K", "周K", "月K"]
    cols = st.columns(5)
    for i, p in enumerate(period_options):
        with cols[i]:
            if st.button(p, key=f"btn_{p}", use_container_width=True, type="primary" if st.session_state.period == p else "secondary"):
                st.session_state.period = p
                st.rerun()
    with cols[3]:
        if st.button("✕", key="close_btn", use_container_width=True):
            st.session_state.view = 'list'
            st.rerun()

    # MA5 MA20 标签（完全一样位置）
    st.markdown("""
    <div style="margin:10px 0 0 20px;">
        <span style="color:#fbbf24; font-size:18px; font-weight:bold;">MA5</span>
        <span style="color:#60a5fa; font-size:18px; font-weight:bold; margin-left:20px;">MA20</span>
    </div>
    """, unsafe_allow_html=True)

    # 图表
    period_map = {"日K": ("1y", "1d"), "周K": ("5y", "1wk"), "月K": ("max", "1mo")}
    period, interval = period_map[st.session_state.period]
    hist = t.history(period=period, interval=interval)

    if not hist.empty:
        hist['MA5'] = hist['Close'].rolling(window=5).mean()
        hist['MA20'] = hist['Close'].rolling(window=20).mean()

        fig = go.Figure()
        fig.add_trace(go.Candlestick(x=hist.index, open=hist['Open'], high=hist['High'], low=hist['Low'], close=hist['Close'],
                                     increasing_line_color='#22c55e', decreasing_line_color='#ef4444'))
        fig.add_trace(go.Scatter(x=hist.index, y=hist['MA5'], line=dict(color='#fbbf24', width=2.5), name="MA5"))
        fig.add_trace(go.Scatter(x=hist.index, y=hist['MA20'], line=dict(color='#60a5fa', width=2.5), name="MA20"))

        fig.update_layout(
            height=620,
            template="plotly_dark",
            showlegend=False,
            xaxis_rangeslider_visible=False,
            plot_bgcolor="#111827",
            paper_bgcolor="#0a0a0a",
            margin=dict(l=10, r=60, t=10, b=20),
            yaxis_side="right"
        )
        st.plotly_chart(fig, use_container_width=True)

        # 底部数据栏（完全一样）
        latest = hist.iloc[-1]
        period_change = (latest['Close'] / hist.iloc[0]['Close'] - 1) * 100
        st.markdown(f"""
        <div style="background:#1f2937;padding:1rem;border-radius:12px;margin-top:10px;display:flex;justify-content:space-around;text-align:center;font-size:15px;">
            <div><strong>最新收盘</strong><br>${latest['Close']:.2f}</div>
            <div><strong>开盘</strong><br>${latest['Open']:.2f}</div>
            <div><strong>最高</strong><br>${latest['High']:.2f}</div>
            <div><strong>最低</strong><br>${latest['Low']:.2f}</div>
            <div><strong>区间涨跌</strong><br><span style="color:{'#22c55e' if period_change>0 else '#ef4444'}">{period_change:+.2f}%</span></div>
            <div><strong>K线数量</strong><br>{len(hist)} 根</div>
        </div>
        """, unsafe_allow_html=True)

    # 机构评级（模仿第一张图）
    st.subheader("机构评级")
    try:
        rec = t.recommendations
        if not rec.empty:
            latest_rec = rec.tail(5)
            for idx, row in latest_rec.iterrows():
                firm = idx[0] if isinstance(idx, tuple) else idx
                rating = row.get('To Grade', 'HOLD')
                target = row.get('Target Price', 'N/A')
                color = "#22c55e" if "BUY" in rating.upper() else "#3b82f6" if "OVERWEIGHT" in rating.upper() else "#ef4444"
                st.markdown(f"""
                <div style="display:flex;justify-content:space-between;align-items:center;padding:8px 0;border-bottom:1px solid #374151;">
                    <div><strong>{firm}</strong></div>
                    <div style="background:{color};color:white;padding:4px 12px;border-radius:9999px;font-size:13px;">{rating}</div>
                    <div>${target}</div>
                </div>
                """, unsafe_allow_html=True)
    except:
        st.info("暂无最新机构评级")

st.caption("Grok v6.0 • 完全参考你朋友网站 • 现在一模一样了！")
