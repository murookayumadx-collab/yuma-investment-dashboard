# 監視銘柄の共通設定
WATCHLIST = [
    "NVDA", "MU", "GOOGL", "MSFT", "TSM",
    "AVGO", "CRWD", "ANET", "VRT", "COHR"
]

import streamlit as st
import pandas as pd
st.set_page_config(
    page_title="YUMA Investment System",
    page_icon="📈",
    layout="wide"
)

st.title("📈 YUMA Investment System")
st.subheader("米国株 投資分析ダッシュボード")

st.success("投資システムの起動に成功しました！")

st.write("今後ここに以下の機能を追加します。")
st.write("① 買い候補ランキング TOP20")
st.write("② 保有銘柄の売却警戒アラート")
st.write("③ CAN SLIM × SEPA スコア")
st.write("④ 米国市場の地合い分析")
import yfinance as yf
@st.cache_data(ttl=900)
def get_stock_data(symbol, period="1y"):
    return yf.download(
        symbol,
        period=period,
        auto_adjust=True,
        progress=False
    )

ticker = st.selectbox(
    "分析する銘柄を選んでね",
WATCHLIST
)

data = get_stock_data(ticker)

if not data.empty:
    st.line_chart(data["Close"])
else:
    st.warning("株価データを取得できませんでした")

    # 売却警戒シグナル
if not data.empty:
    close = data["Close"].squeeze()
    ma50 = close.rolling(50).mean()
    ma200 = close.rolling(200).mean()

    price = float(close.iloc[-1])
    avg50 = float(ma50.iloc[-1])
    avg200 = float(ma200.iloc[-1])

    st.subheader("🚨 売却警戒シグナル")

    if price < avg200:
        st.error("🔴 強い警戒：200日移動平均線を下回っています")
    elif price < avg50:
        st.warning("🟡 注意：50日移動平均線を下回っています")
    else:
        st.success("🟢 トレンド良好：主要移動平均線の上にあります")

        # 出来高による売却警戒シグナル
if not data.empty and len(data) >= 21:
    close = data["Close"].squeeze()
    volume = data["Volume"].squeeze()

    avg_volume = volume.shift(1).rolling(20).mean()

    price_down = close.iloc[-1] < close.iloc[-2]
    volume_ratio = volume.iloc[-1] / avg_volume.iloc[-1]

    st.subheader("📊 出来高分析")

    st.write(f"直近の出来高倍率：{volume_ratio:.2f}倍")

    if price_down and volume_ratio >= 1.5:
        st.error("🔴 警戒：株価下落＋出来高急増")
    elif price_down and volume_ratio >= 1.0:
        st.warning("🟡 注意：平均以上の出来高を伴う下落")
    else:
        st.success("🟢 出来高による強い売り警戒なし")

        # 総合売却警戒スコア
if not data.empty and len(data) >= 200:
    close = data["Close"].squeeze()
    volume = data["Volume"].squeeze()

    price = float(close.iloc[-1])
    ma50 = float(close.rolling(50).mean().iloc[-1])
    ma200 = float(close.rolling(200).mean().iloc[-1])
    trend_ok = ma50 > ma200
    avg_volume = float(volume.shift(1).rolling(20).mean().iloc[-1])
    drawdown = (price / float(close.tail(20).max()) - 1) * 100
    score = 0

    # 50日移動平均線を下回る
    if price < ma50:
        score += 30

    # 200日移動平均線を下回る
    if price < ma200:
        score += 40

    # 出来高急増を伴う下落
    if (
        close.iloc[-1] < close.iloc[-2]
        and avg_volume > 0
        and volume.iloc[-1] >= avg_volume * 1.5
    ):
        score += 30
    st.subheader("📈 ミネルヴィニ式トレンド判定")

    if trend_ok:
        st.success("🟢 50日線が200日線より上：上昇トレンド条件クリア")
    else:
        st.warning("🟡 50日線が200日線以下：トレンドに注意")
    st.subheader("🎯 総合売却警戒スコア")
    st.metric("警戒スコア", f"{score} / 100")
    if drawdown <= -8:
        st.warning("⚠️ 直近20営業日の最高終値から8%以上下落")
    if score >= 70:
        st.error("🔴 警戒度：高｜売却・縮小を優先的に検討")
    elif score >= 30:
        st.warning("🟡 警戒度：中｜保有状況を再確認")
    else:
        st.success("🟢 警戒度：低｜現時点の警戒条件なし")

        # 5銘柄の売却警戒ランキング
st.subheader("🏆 売却警戒ランキング")

tickers = WATCHLIST
results = []

for symbol in tickers:
    stock = get_stock_data(symbol)

    if len(stock) < 200:
        continue

    close = stock["Close"].squeeze()
    volume = stock["Volume"].squeeze()

    price = float(close.iloc[-1])
    ma50 = float(close.rolling(50).mean().iloc[-1])
    ma200 = float(close.rolling(200).mean().iloc[-1])
    avg_vol = float(volume.shift(1).rolling(20).mean().iloc[-1])

    score = 0

    if price < ma50:
        score += 30

    if price < ma200:
        score += 40

    if (
        close.iloc[-1] < close.iloc[-2]
        and avg_vol > 0
        and volume.iloc[-1] >= avg_vol * 1.5
    ):
        score += 30

    results.append({
        "銘柄": symbol,
        "警戒スコア": score,
        "株価($)": round(price, 2)
    })

if results:
    ranking = pd.DataFrame(results)
    ranking = ranking.sort_values(
        "警戒スコア", ascending=False
    )
    st.dataframe(ranking, hide_index=True)
else:
    st.warning("ランキング用の株価データを取得できませんでした")

    # 米国市場のトレンド分析
st.subheader("🌎 米国市場の環境チェック")

market_tickers = {
    "NASDAQ100": "QQQ",
    "S&P500": "SPY",
    "半導体セクター": "SOXX"
}

for name, symbol in market_tickers.items():
    market = get_stock_data(symbol)

    if len(market) < 200:
        st.warning(f"{name}: データ不足")
        continue

    close = market["Close"].squeeze()

    price = float(close.iloc[-1])
    ma50 = float(close.rolling(50).mean().iloc[-1])
    ma200 = float(close.rolling(200).mean().iloc[-1])

    if price < ma200:
        st.error(f"🔴 {name}: 市場環境に強い警戒")
    elif price < ma50:
        st.warning(f"🟡 {name}: 市場環境に注意")
    else:
        st.success(f"🟢 {name}: 上昇トレンド")

        # RS分析：過去3か月のS&P500との比較
st.subheader("💪 RS分析（市場平均との比較）")

rs_tickers = WATCHLIST

spy_data = get_stock_data("SPY", period="6mo")

if len(spy_data) >= 64:
    spy_close = spy_data["Close"].squeeze()
    spy_return = (spy_close.iloc[-1] / spy_close.iloc[-64] - 1) * 100

    rs_results = []

    for symbol in rs_tickers:
        stock_data = get_stock_data(symbol, period="6mo")

        if len(stock_data) < 64:
            continue

        stock_close = stock_data["Close"].squeeze()
        stock_return = (
            stock_close.iloc[-1] / stock_close.iloc[-64] - 1
        ) * 100

        rs_results.append({
            "銘柄": symbol,
            "3か月騰落率(%)": round(float(stock_return), 2),
            "SPYとの差(%pt)": round(
                float(stock_return - spy_return), 2
            )
        })

    if rs_results:
        rs_table = pd.DataFrame(rs_results)
        rs_table = rs_table.sort_values(
            "SPYとの差(%pt)", ascending=False
        )
        st.dataframe(rs_table, hide_index=True)
else:
    st.warning("RS分析用のデータが不足しています")

    # 52週高値からの下落率分析
st.subheader("📉 52週高値からの下落率")

high_results = []

for symbol in WATCHLIST:
    stock = get_stock_data(symbol)
    if stock.empty:
        continue

    close = stock["Close"].squeeze()
    high = stock["High"].squeeze()

    latest_price = float(close.iloc[-1])
    highest_price = float(high.max())

    decline = (latest_price / highest_price - 1) * 100

    high_results.append({
        "銘柄": symbol,
        "現在株価($)": round(latest_price, 2),
        "52週高値($)": round(highest_price, 2),
        "高値からの下落率(%)": round(decline, 2)
    })

if high_results:
    high_table = pd.DataFrame(high_results)
    high_table = high_table.sort_values(
        "高値からの下落率(%)"
    )
    st.dataframe(high_table, hide_index=True)
else:
    st.warning("高値分析用のデータを取得できませんでした")

    # 売却監視ダッシュボード
st.subheader("🚨 売却監視ダッシュボード")

watchlist = WATCHLIST
summary = []

for symbol in watchlist:
    try:
        stock = get_stock_data(symbol)
        if len(stock) < 200:
            continue

        close = stock["Close"].squeeze()
        high = stock["High"].squeeze()
        volume = stock["Volume"].squeeze()

        price = float(close.iloc[-1])
        ma50 = float(close.rolling(50).mean().iloc[-1])
        ma200 = float(close.rolling(200).mean().iloc[-1])
        peak = float(high.max())
        decline = (price / peak - 1) * 100

        avg_vol = float(
            volume.shift(1).rolling(20).mean().iloc[-1]
        )

        score = 0

        if price < ma50:
            score += 30
        if price < ma200:
            score += 40
        if (
            close.iloc[-1] < close.iloc[-2]
            and avg_vol > 0
            and volume.iloc[-1] >= avg_vol * 1.5
        ):
            score += 30

        if score >= 70:
            level = "🔴 高"
        elif score >= 30:
            level = "🟡 中"
        else:
            level = "🟢 低"

        summary.append({
            "銘柄": symbol,
            "株価($)": round(price, 2),
            "警戒スコア": score,
            "警戒度": level,
            "高値からの下落(%)": round(decline, 2)
        })

    except Exception as e:
        st.warning(f"{symbol}: データ取得エラー")

if summary:
    summary_df = pd.DataFrame(summary)
    summary_df = summary_df.sort_values(
        "警戒スコア", ascending=False
    )
    st.dataframe(summary_df, hide_index=True)
else:
    st.warning("監視データを取得できませんでした")

    # 売却シグナルの変化を検出
st.subheader("⚡ 売却警戒シグナルの変化")

for symbol in WATCHLIST:
    stock = get_stock_data(symbol)

    if len(stock) < 201:
        continue

    close = stock["Close"].squeeze()
    volume = stock["Volume"].squeeze()

    ma50 = close.rolling(50).mean()
    ma200 = close.rolling(200).mean()
    avg_vol = volume.shift(1).rolling(20).mean()

    def get_score(i):
        score = 0

        if close.iloc[i] < ma50.iloc[i]:
            score += 30

        if close.iloc[i] < ma200.iloc[i]:
            score += 40

        if (
            close.iloc[i] < close.iloc[i - 1]
            and avg_vol.iloc[i] > 0
            and volume.iloc[i] >= avg_vol.iloc[i] * 1.5
        ):
            score += 30

        return score

    yesterday = get_score(-2)
    today = get_score(-1)

    if today > yesterday:
        st.error(
            f"🔴 {symbol}: 警戒スコア悪化 "
            f"{yesterday} → {today}"
        )
    elif today < yesterday:
        st.success(
            f"🟢 {symbol}: 警戒スコア改善 "
            f"{yesterday} → {today}"
        )
    else:
        st.info(
            f"⚪ {symbol}: 変化なし（{today}点）"
        )
