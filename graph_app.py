import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import io

# ==========================================
# 最新Python対応：文字化け対策（PC＆Webサーバー両対応）
# ==========================================
import matplotlib.font_manager as fm
# サーバー（Linux）用：標準的な日本語フォントを優先し、なければWindowsフォントを当てる
plt.rcParams['font.family'] = ['sans-serif', 'MS Gothic', 'Meiryo', 'AppleGothic']

# ページの設定（iPadやPCの画面幅に自動追従）
st.set_page_config(page_title="統計解析＆マルチグラフ作成アプリ", layout="wide")

st.title("📊 統計解析 ＆ グラフ作成アプリ (Web版)")
st.caption("Excelデータを貼り付けるだけで、基本統計量の計算とエラーバー付きグラフを作成します。")

# --- 画面を左右に分割（左：設定・入力、右：結果表示） ---
col_left, col_right = st.columns([1, 2])

with col_left:
    st.subheader("1. データとグラフの設定")
    
    # データの入力
    input_text = st.text_area(
        "データの入力 (Excel等からコピペ)", 
        placeholder="ここにコピーしたデータを貼り付けてください",
        height=250
    )
    
    # グラフの種類
    chart_type = st.segmented_control(
        "グラフの種類:", 
        options=["棒グラフ", "折れ線グラフ"], 
        default="棒グラフ"
    )
    
    # 色とサイズの設定
    chart_color = st.selectbox(
        "メインカラー:", 
        ["ブルー", "グリーン", "オレンジ", "レッド", "グレー"]
    )
    
    chart_weight = st.selectbox(
        "サイズ（幅・太さ）:", 
        ["細め", "標準", "太め"], 
        index=1
    )
    
    # 軸ラベルの設定
    st.markdown("---")
    entry_title = st.text_input("グラフのタイトル:", placeholder="例: 実験データの比較")
    entry_xlabel = st.text_input("横軸ラベル:", placeholder="例: 条件")
    entry_ylabel = st.text_input("縦軸ラベル:", placeholder="例: 測定値")
    
    # 計算実行ボタン
    calc_button = st.button("統計計算 ＆ グラフ表示", type="primary", use_container_width=True)

with col_right:
    st.subheader("2. 解析結果")
    
    if calc_button and input_text.strip():
        try:
            # データの読み込みと計算
            df = pd.read_csv(io.StringIO(input_text.strip()), sep='\t')
            df = df.apply(pd.to_numeric, errors='coerce')
            
            summary = pd.DataFrame()
            summary['N'] = df.count()
            summary['Mean'] = df.mean()
            summary['SEM'] = df.sem()
            summary['SD'] = df.std()
            summary['Min'] = df.min()
            summary['Median'] = df.median()
            summary['Max'] = df.max()
            summary['Sum'] = df.sum()
            
            # --- ① 基本統計量の表を表示 ---
            st.markdown("#### 📋 基本統計量")
            # Webで見やすいように、四捨五入して綺麗にフォーマットした表を表示
            st.dataframe(summary.style.format({
                'N': '{:.0f}', 'Mean': '{:.2f}', 'SEM': '{:.2f}', 
                'SD': '{:.2f}', 'Min': '{:.2f}', 'Median': '{:.2f}', 
                'Max': '{:.2f}', 'Sum': '{:.1f}'
            }), use_container_width=True)
            
            # --- ② グラフの描画 ---
            st.markdown("#### 📈 グラフ表示")
            fig, ax = plt.subplots(figsize=(6, 4.2), dpi=120)
            
            x_labels = summary.index.tolist()
            means = summary['Mean'].tolist()
            sems = summary['SEM'].tolist()

            # 色マッピング
            color_map = {"ブルー": "#2574bf", "グリーン": "#2ca02c", "オレンジ": "#ff7f0e", "レッド": "#d62728", "グレー": "#7f7f7f"}
            chosen_color = color_map.get(chart_color, "#2574bf")

            if chart_type == "棒グラフ":
                width_map = {"細め": 0.3, "標準": 0.5, "太め": 0.7}
                chosen_width = width_map.get(chart_weight, 0.5)
                ax.bar(x_labels, means, yerr=sems, width=chosen_width, capsize=6, 
                       color=chosen_color, edgecolor="black", error_kw={'ecolor': '#cc0000', 'lw': 1.8})
            else:
                linewidth_map = {"細め": 1.2, "標準": 2.2, "太め": 3.5}
                chosen_linewidth = linewidth_map.get(chart_weight, 2.2)
                x_pos = np.arange(len(x_labels))
                ax.errorbar(x_pos, means, yerr=sems, fmt='-o', capsize=6, color=chosen_color, 
                            markerfacecolor="white", markeredgewidth=1.2, markersize=5,
                            linewidth=chosen_linewidth, ecolor='#cc0000', elinewidth=1.8)
                ax.set_xticks(x_pos)
                ax.set_xticklabels(x_labels)

            # ラベル・デザイン設定
            ax.set_title(entry_title if entry_title else f"{chart_type} (SEM表示)", fontsize=12, fontweight="bold")
            if entry_xlabel: ax.set_xlabel(entry_xlabel, fontsize=10)
            if entry_ylabel: ax.set_ylabel(entry_ylabel, fontsize=10)
            ax.grid(axis='y', linestyle='--', alpha=0.7)
            fig.tight_layout()

            # Streamlit専用のグラフ表示命令
            st.pyplot(fig)
            plt.close(fig)
            
        except Exception as e:
            st.error(f"データの読み込みや計算でエラーが発生しました。\n理由: {str(e)}")
            
    elif calc_button:
        st.warning("データが入力されていません。左側の入力欄にデータを貼り付けてください。")
    else:
        st.info("左側の欄にデータを入力し、「統計計算 ＆ グラフ表示」ボタンを押してください。")
