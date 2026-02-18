import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(page_title="Stock Radar", layout="wide", page_icon="📈")

st.markdown('''
<style>
    .main {background-color: #0a0a0a; color: #e2e8f0;}
    .header {background-color: #111827; padding: 1rem; border-radius: 16px; margin-bottom: 1.5rem;}
    .chip {background-color: #1f2937; padding: 8px 16px; border-radius: 9999px; margin: 4px; display: inline-flex; align-items: center; font-weight: 600; font-size: 15px;}
    .stock-card {background-color: #1f2937; padding: 1.5rem; border-radius: 16px; border: 1px solid #374151; transition: all 0.2s;}
    .stock-card:hover {border-color: #3b82f6; transform: translateY(-4px);}
    .price-up {color: #22c55e; font-weight: bold;}
    .price-down {color: #ef4444; font-weight: bold;}
</style>
''', unsafe_allow_html=True)

if 'tickers' not in st.session_state:
    st.session_state.tickers = ['AAPL', 'NVDA', 'TSLA', 'MSFT', '600519.SS']
if 'view' not in st.session_state:
    st.session_state.view = 'list'
if 'selected_ticker' not in st.session_state:
    st.session_state.selected_ticker = None

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

# ====================== 列表页 ======================
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

            if st.button("📈 查看 K 线 + 评级", key=f"view_{ticker}", use_container_width=True):
                st.session_state.selected_ticker = ticker
                st.session_state.view = 'detail'
                st.rerun()
        except:
            st.error(f"{ticker} 数据加载失败")

else:  # ====================== v4.0 详情页（重点优化） ======================
    ticker = st.session_state.selected_ticker
    if st.button("← 返回列表", type="secondary"):
        st.session_state.view = 'list'
        st.rerun()

    t = yf.Ticker(ticker)
    info = t.info
    name = info.get('longName') or ticker
    current_price = info.get('currentPrice', info.get('regularMarketPrice', 0))
    change_pct = info.get('regularMarketChangePercent', 0)

    # 顶部大价格（完全像参考图）
    st.markdown(f"""
    <div style="background:#1f2937;padding:1.8rem;border-radius:16px;margin-bottom:1.5rem;text-align:center;">
        <h1 style="margin:0;font-size:2.8rem;">{ticker}</h1>
        <h2 style="margin:0.5rem 0;color:#cbd5e1;">{name}</h2>
        <h1 style="margin:0.8rem 0 0.2rem 0;font-size:3.2rem;">{current_price:.2f}</h1>
        <h2 class="{'price-up' if change_pct>=0 else 'price-down'}" style="margin:0;font-size:1.6rem;">{change_pct:+.2f}%</h2>
    </div>
    """, unsafe_allow_html=True)

    # K线切换
    period_map = {"日K": ("1y", "1d"), "周K": ("5y", "1wk"), "月K": ("max", "1mo")}
    cols = st.columns(4)
    selected_period = "日K"
    for i, p in enumerate(["日K", "周K", "月K"]):
        with cols[i]:
            if st.button(p, key=f"btn_{p}", use_container_width=True):
                selected_period = p

    period, interval = period_map[selected_period]
    hist = t.history(period=period, interval=interval)

    if not hist.empty:
        hist['MA5'] = hist['Close'].rolling(window=5).mean()
        hist['MA20'] = hist['Close'].rolling(window=20).mean()

        # 单主图面板（去掉大成交量，只保留主K线 + MA）
        fig = go.Figure()
        fig.add_trace(go.Candlestick(
            x=hist.index,
            open=hist['Open'], high=hist['High'], low=hist['Low'], close=hist['Close'],
            increasing_line_color='#22c55e', decreasing_line_color='#ef4444'
        ))
        fig.add_trace(go.Scatter(x=hist.index, y=hist['MA5'], line=dict(color='#fbbf24', width=2.5), name="MA5"))
        fig.add_trace(go.Scatter(x=hist.index, y=hist['MA20'], line=dict(color='#60a5fa', width=2.5), name="MA20"))

        # 添加 MA5 / MA20 左上标签（完全像参考图）
        fig.add_annotation(x=0.02, y=0.96, xref="paper", yref="paper", text="MA5", showarrow=False, font=dict(color="#fbbf24", size=16, family="Arial Black"))
        fig.add_annotation(x=0.10, y=0.96, xref="paper", yref="paper", text="MA20", showarrow=False, font=dict(color="#60a5fa", size=16, family="Arial Black"))

        fig.update_layout(
            height=680,
            template="plotly_dark",
            xaxis_rangeslider_visible=False,
            plot_bgcolor="#111827",
            paper_bgcolor="#0a0a0a",
            margin=dict(l=10, r=10, t=30, b=20),
            yaxis_title="价格",
            yaxis_side="right"
        )
        st.plotly_chart(fig, use_container_width=True)

        # 底部数据栏（完全复刻参考图）
        latest = hist.iloc[-1]
        period_change = (latest['Close'] / hist.iloc[0]['Close'] - 1) * 100
        st.markdown(f"""
        <div style="background:#1f2937;padding:1.2rem;border-radius:12px;margin-top:1rem;display:flex;justify-content:space-around;text-align:center;font-size:15px;">
            <div><strong>最新收盘</strong><br>{latest['Close']:.2f}</div>
            <div><strong>开盘</strong><br>{latest['Open']:.2f}</div>
            <div><strong>最高</strong><br>{latest['High']:.2f}</div>
            <div><strong>最低</strong><br>{latest['Low']:.2f}</div>
            <div><strong>区间涨跌</strong><br><span style="color:{'#22c55e' if period_change>0 else '#ef4444'}">{period_change:+.2f}%</span></div>
            <div><strong>K线数量</strong><br>{len(hist)} 根</div>
        </div>
        """, unsafe_allow_html=True)

    # 机构评级
    st.subheader("🏦 机构买入评级")
    st.write(f"**推荐级别**：{info.get('recommendationKey', '暂无').upper()}  **分析师人数**：{info.get('numberOfAnalystOpinions', '暂无')}")
    try:
        rec = t.recommendations
        if not rec.empty:
            st.dataframe(rec.tail(10), use_container_width=True)
    except:
        st.info("暂无最新机构评级")

st.caption("数据来自 Yahoo Finance • Grok v4.0 专属定制 • 现在超级接近你第一张参考图了！")
