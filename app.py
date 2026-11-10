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

ticker = st.selectbox(
    "分析する銘柄を選んでね",
    ["NVDA", "MU", "GOOGL", "MSFT", "TSM"]
)

data = yf.download(
    ticker,
    period="1y",
    auto_adjust=True,
    progress=False
)

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
    avg_volume = float(volume.shift(1).rolling(20).mean().iloc[-1])

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

    st.subheader("🎯 総合売却警戒スコア")
    st.metric("警戒スコア", f"{score} / 100")

    if score >= 70:
        st.error("🔴 警戒度：高｜売却・縮小を優先的に検討")
    elif score >= 30:
        st.warning("🟡 警戒度：中｜保有状況を再確認")
    else:
        st.success("🟢 警戒度：低｜現時点の警戒条件なし")

        # 5銘柄の売却警戒ランキング
st.subheader("🏆 売却警戒ランキング")

tickers = ["NVDA", "MU", "GOOGL", "MSFT", "TSM"]
results = []

for symbol in tickers:
    stock = yf.download(
        symbol, period="1y",
        auto_adjust=True, progress=False
    )

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