import streamlit as st

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