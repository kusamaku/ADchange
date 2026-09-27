"""
積分型（二重積分型）ADC ステップ・バイ・ステップ学習シミュレータ
Streamlit版
対象：高専4年生程度
"""

import numpy as np
import plotly.graph_objects as go
import streamlit as st


st.set_page_config(
    page_title="積分型ADC 学習シミュレータ",
    page_icon="📐",
    layout="wide",
)


# ---------------------------------------------------------
# 計算
# ---------------------------------------------------------
def calculate(vin: float, vref: float, bits: int):
    if vin < 0:
        raise ValueError("Vin は 0 V 以上にしてください。")
    if vref <= 0:
        raise ValueError("Vref は 0 V より大きくしてください。")
    if vin > vref:
        raise ValueError("この教材では Vin ≤ Vref としてください。")
    if not 3 <= bits <= 16:
        raise ValueError("分解能は3～16 bitの範囲にしてください。")

    max_code = 2**bits - 1
    ideal_code = vin / vref * max_code
    code = int(round(ideal_code))
    code = max(0, min(max_code, code))

    # 二重積分型ADCの教材用正規化モデル
    T_INT = 1.0
    T_MAX = 1.0

    n1 = 250
    t1 = np.linspace(0, T_INT, n1)
    integ1 = -(vin / vref) * (t1 / T_INT)

    # 理想的なランダウン時間
    t_rd_ideal = (vin / vref) * T_MAX

    # カウンタで量子化されたランダウン時間
    t_rd_quant = code / max_code * T_MAX

    n2 = 250
    t2 = np.linspace(0, T_MAX, n2)
    integ2 = -vin / vref + (t2 / T_MAX)

    t_total = np.concatenate([t1, T_INT + t2])
    integ_total = np.concatenate([integ1, integ2])

    count_time = np.linspace(0, T_MAX, max(100, max_code + 1))
    count_values = np.minimum(
        np.floor(count_time / T_MAX * max_code),
        max_code,
    )

    return {
        "vin": vin,
        "vref": vref,
        "bits": bits,
        "max_code": max_code,
        "ideal_code": ideal_code,
        "code": code,
        "resolution": vref / (2**bits),
        "T_INT": T_INT,
        "T_RD_IDEAL": t_rd_ideal,
        "T_RD_QUANT": t_rd_quant,
        "t_total": t_total,
        "integ_total": integ_total,
        "t1": t1,
        "integ1": integ1,
        "t2": t2,
        "integ2": integ2,
        "count_time": count_time,
        "count_values": count_values,
    }


# ---------------------------------------------------------
# グラフ
# ---------------------------------------------------------
def make_wave_graph(r, step):
    fig = go.Figure()

    if step == 0:
        fig.add_trace(
            go.Scatter(
                x=r["t_total"],
                y=r["integ_total"],
                mode="lines",
                line=dict(width=2),
                opacity=0.3,
                name="積分器出力",
            )
        )
        title = "積分器出力（これから変換を開始）"

    elif step == 1:
        fig.add_trace(
            go.Scatter(
                x=r["t1"],
                y=r["integ1"],
                mode="lines",
                line=dict(width=3),
                name="第1積分",
            )
        )
        fig.add_trace(
            go.Scatter(
                x=[r["T_INT"]],
                y=[r["integ1"][-1]],
                mode="markers",
                marker=dict(size=10),
                name="積分終了点",
            )
        )
        fig.add_hline(y=0, line_width=1)
        fig.add_annotation(
            x=r["T_INT"] * 0.55,
            y=r["integ1"].min() * 0.5,
            text=f"Vin = {r['vin']:.3f} V",
            showarrow=False,
        )
        title = "Step 1：入力電圧 Vin を積分"

    elif step == 2:
        fig.add_trace(
            go.Scatter(
                x=r["t1"],
                y=r["integ1"],
                mode="lines",
                line=dict(width=2),
                opacity=0.35,
                name="第1積分",
            )
        )
        fig.add_trace(
            go.Scatter(
                x=r["T_INT"] + r["t2"],
                y=r["integ2"],
                mode="lines",
                line=dict(width=3),
                name="ランダウン",
            )
        )
        fig.add_hline(y=0, line_width=1)
        fig.add_vline(x=r["T_INT"], line_dash="dash", line_width=1.5)
        fig.add_vline(
            x=r["T_INT"] + r["T_RD_IDEAL"],
            line_dash="dash",
            line_width=1.5,
        )
        fig.add_annotation(
            x=r["T_INT"],
            y=r["integ1"][-1],
            text="第1積分終了",
            showarrow=True,
            arrowhead=2,
            ax=60,
            ay=35,
        )
        fig.add_annotation(
            x=r["T_INT"] + r["T_RD_IDEAL"],
            y=0,
            text=f"ランダウン終了 ≈ {r['T_RD_IDEAL']:.3f} × T_MAX",
            showarrow=True,
            arrowhead=2,
            ax=70,
            ay=-45,
        )
        title = "Step 2：基準電圧によるランダウン"

    else:
        fig.add_trace(
            go.Scatter(
                x=r["t1"],
                y=r["integ1"],
                mode="lines",
                line=dict(width=2),
                opacity=0.4,
                name="第1積分",
            )
        )
        fig.add_trace(
            go.Scatter(
                x=r["T_INT"] + r["t2"],
                y=r["integ2"],
                mode="lines",
                line=dict(width=3),
                name="ランダウン",
            )
        )
        end_x = r["T_INT"] + r["T_RD_QUANT"]
        fig.add_hline(y=0, line_width=1)
        fig.add_vline(x=end_x, line_dash="dash", line_width=2)
        fig.add_trace(
            go.Scatter(
                x=[end_x],
                y=[0],
                mode="markers",
                marker=dict(size=12),
                name="変換完了点",
            )
        )
        fig.add_annotation(
            x=end_x,
            y=0,
            text=f"デジタル出力 = {r['code']}",
            showarrow=True,
            arrowhead=2,
            ax=70,
            ay=-50,
        )
        title = "Step 3：変換完了 ― ランダウン時間をデジタル値へ"

    fig.update_layout(
        title=title,
        xaxis_title="時間（正規化）",
        yaxis_title="積分器出力（正規化）",
        height=450,
        margin=dict(l=50, r=30, t=60, b=50),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
    )
    fig.update_xaxes(showgrid=True)
    fig.update_yaxes(showgrid=True)
    return fig


def make_count_graph(r, step):
    fig = go.Figure()
    t = r["count_time"]
    y = r["count_values"]

    if step < 2:
        fig.add_trace(
            go.Scatter(
                x=t,
                y=y,
                mode="lines",
                line=dict(width=2),
                opacity=0.3,
                name="カウンタ",
            )
        )
        title = "カウンタ（ランダウン開始前）"
    else:
        fig.add_trace(
            go.Scatter(
                x=t,
                y=y,
                mode="lines",
                line=dict(width=3),
                name="カウント値",
            )
        )
        fig.add_vline(
            x=r["T_RD_QUANT"],
            line_dash="dash",
            line_width=1.5,
        )
        fig.add_trace(
            go.Scatter(
                x=[r["T_RD_QUANT"]],
                y=[r["code"]],
                mode="markers",
                marker=dict(size=11),
                name="最終カウント",
            )
        )
        fig.add_annotation(
            x=r["T_RD_QUANT"],
            y=r["code"],
            text=f"カウント値 = {r['code']}",
            showarrow=True,
            arrowhead=2,
            ax=65,
            ay=-45,
        )
        title = (
            "ランダウン中：クロックを数えている"
            if step == 2
            else "変換完了：カウント値がデジタル出力"
        )

    fig.update_layout(
        title=title,
        xaxis_title="ランダウン時間（正規化）",
        yaxis_title="カウント値",
        height=350,
        margin=dict(l=50, r=30, t=60, b=50),
    )
    fig.update_xaxes(showgrid=True, range=[0, 1])
    fig.update_yaxes(showgrid=True, range=[0, r["max_code"] * 1.08])
    return fig


# ---------------------------------------------------------
# セッション状態
# ---------------------------------------------------------
if "step" not in st.session_state:
    st.session_state.step = 0
if "vin" not in st.session_state:
    st.session_state.vin = 2.50
if "vref" not in st.session_state:
    st.session_state.vref = 5.00
if "bits" not in st.session_state:
    st.session_state.bits = 8


# ---------------------------------------------------------
# サイドバー
# ---------------------------------------------------------
st.sidebar.title("⚙️ 入力パラメータ")

with st.sidebar.form("parameter_form"):
    vin_input = st.number_input(
        "入力電圧 Vin [V]",
        min_value=0.0,
        value=float(st.session_state.vin),
        step=0.1,
        format="%.2f",
    )
    vref_input = st.number_input(
        "基準電圧 Vref [V]",
        min_value=0.01,
        value=float(st.session_state.vref),
        step=0.1,
        format="%.2f",
    )
    bits_input = st.slider(
        "分解能 [bit]",
        min_value=3,
        max_value=16,
        value=int(st.session_state.bits),
    )
    apply = st.form_submit_button("パラメータを反映", use_container_width=True)

if apply:
    if vin_input > vref_input:
        st.sidebar.error("Vin は Vref 以下にしてください。")
    else:
        st.session_state.vin = vin_input
        st.session_state.vref = vref_input
        st.session_state.bits = bits_input
        st.session_state.step = 0
        st.rerun()

try:
    result = calculate(
        st.session_state.vin,
        st.session_state.vref,
        st.session_state.bits,
    )
except ValueError as e:
    st.error(str(e))
    st.stop()


# ---------------------------------------------------------
# メイン画面
# ---------------------------------------------------------
st.title("📐 積分型（二重積分型）ADC ステップ・バイ・ステップ学習シミュレータ")
st.caption("電圧 → 積分量 → 時間 → カウント値 → デジタル値、という変換の流れを視覚的に学習できます。")

# ステップ説明
step_titles = [
    "Step 0 / 3　初期化",
    "Step 1 / 3　入力電圧を積分",
    "Step 2 / 3　基準電圧でランダウン",
    "Step 3 / 3　デジタル値を確定",
]

explanations = [
    """まず二重積分型ADCの準備をします。\n\n入力電圧 Vin と基準電圧 Vref を、単純に比較するのではなく、積分回路を使って電圧を「時間」に変換します。\n\n主なポイントは、①積分回路、②基準電圧、③ランダウン時間、④カウンタです。\n\n「次のステップ →」を押すと変換が進みます。""",
    """【第1積分】\n\n一定時間 T_INT の間、入力電圧 Vin を積分回路へ入力します。\n\n積分器の出力は時間とともに直線的に変化します。Vin が大きいほど、積分器出力の変化量も大きくなります。\n\nここでは、Vin を「積分された量」に変換していると考えてください。\n\nポイント：\n・積分時間は一定\n・入力電圧が大きいほど積分器出力の絶対値が大きい""",
    """【第2積分：ランダウン】\n\n次に入力 Vin を切り離し、極性を反転した基準電圧を積分回路へ入力します。\n\n積分器の出力が0 Vへ戻るまでの時間を「ランダウン時間」と呼びます。\n\nVin が大きいほど第1積分で蓄積された量が大きいため、0 Vへ戻るまでの時間も長くなります。\n\nつまり、電圧の大きさを時間に変換できます。""",
    f"""【デジタル値の確定】\n\nランダウン中にクロックを数えた値がデジタル出力になります。\n\n今回の結果：{result['code']}（10進）\n分解能：{result['bits']} bit\n1 LSB ≈ {result['resolution']:.6f} V\n\n二重積分型ADCでは、入力電圧に比例したランダウン時間をカウンタで測定することで、アナログ値をデジタル値へ変換します。\n\n重要なのは「電圧 → 積分量 → 時間 → カウント値」という変換の流れです。""",
]

st.subheader(step_titles[st.session_state.step])
st.info(explanations[st.session_state.step])

# 操作ボタン
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("← 前のステップ", disabled=st.session_state.step == 0, use_container_width=True):
        st.session_state.step -= 1
        st.rerun()
with col2:
    if st.button("最初から", use_container_width=True):
        st.session_state.step = 0
        st.rerun()
with col3:
    if st.button("次のステップ →", disabled=st.session_state.step == 3, use_container_width=True):
        st.session_state.step += 1
        st.rerun()

# 結果カード
st.markdown("### 変換結果")
metric1, metric2, metric3, metric4 = st.columns(4)
metric1.metric("入力電圧 Vin", f"{result['vin']:.3f} V")
metric2.metric("基準電圧 Vref", f"{result['vref']:.3f} V")
metric3.metric("デジタル値", f"{result['code']} / {result['max_code']}")
metric4.metric("分解能", f"{result['bits']} bit")

if st.session_state.step == 3:
    st.success(
        f"変換完了：デジタル出力 = {result['code']}、"
        f"ランダウン時間 ≈ {result['T_RD_QUANT']:.4f} × T_MAX、"
        f"1 LSB ≈ {result['resolution']:.6f} V"
    )

# グラフ
st.markdown("### 積分器出力")
st.plotly_chart(make_wave_graph(result, st.session_state.step), use_container_width=True)

st.markdown("### カウンタの動作")
st.plotly_chart(make_count_graph(result, st.session_state.step), use_container_width=True)

# キーワード
st.markdown("### 🔑 重要キーワード")
keywords = ["積分回路", "基準電圧 Vref", "ランダウン時間", "カウンタ", "分解能"]
cols = st.columns(len(keywords))
for col, keyword in zip(cols, keywords):
    col.info(keyword)

# 教材上の注意
with st.expander("このシミュレータの計算モデルについて"):
    st.write(
        "このプログラムは、二重積分型ADCの基本原理を理解するための教材用・正規化モデルです。"
        "実際のADCでは、積分器の抵抗・コンデンサ、クロック周波数、オフセット、ノイズ、"
        "スイッチやコンパレータなどの影響があります。"
    )
