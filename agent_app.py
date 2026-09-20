"""
강건 국면적응 예측 에이전트 — 전용 대시보드
실행: streamlit run agent_app.py

구성:
  ① 로드맵 — 에이전트 설계 발전 4단계 한눈에
  ② 개발 과정 — 각 단계 실험 결과 (자르기/유사구간/부족대응/강건선택)
  ③ 에이전트 실행 — 데이터 넣으면 최적 조합 자동 선택 + 예측
"""
import streamlit as st
import pandas as pd
import numpy as np
import json
import plotly.graph_objects as go

st.set_page_config(page_title="예측 에이전트", page_icon="🤖",
                   layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
.hero { background:linear-gradient(135deg,#13233A,#1E3556); color:#fff;
        border-radius:14px; padding:26px 30px; margin-bottom:10px; }
.step { background:#F4F6F9; color:#24303F; border-left:4px solid #C87941;
        border-radius:0 10px 10px 0; padding:13px 17px; margin:8px 0; font-size:14px; }
.res  { background:#EAF5EF; color:#13233A; border-radius:10px; padding:14px 18px;
        margin:8px 0; font-size:14px; border:1px solid #B8DFC9; }
.road { background:#1E3556; color:#DCE6F2; border-radius:10px; padding:16px 20px;
        margin:8px 0; }
</style>
""", unsafe_allow_html=True)

NAVY="#13233A"; COPPER="#C87941"; STEEL="#5B7A99"; GREEN="#2E7D5B"; RED="#B0413E"
COPPER_L="#E8A66B"; ICE="#DCE6F2"
THEME = dict(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
             font=dict(color="#888"),
             xaxis=dict(gridcolor="rgba(128,128,128,0.2)"),
             yaxis=dict(gridcolor="rgba(128,128,128,0.2)"))

@st.cache_data
def load():
    return json.load(open("agent_dashboard.json"))

D = load()

with st.sidebar:
    st.markdown("## 🤖 예측 에이전트")
    st.markdown("*강건 국면적응 예측\nLME × 데이터 특성 적응*")
    st.divider()
    page = st.radio("메뉴", [
        "① 로드맵",
        "② 개발 과정",
        "③ 에이전트 실행",
    ])
    st.divider()
    st.caption("데이터를 넣으면 상황에 맞는\n최적 예측 조합을 자동 선택")

# ══════════════════════════════════════════════
# ① 로드맵
# ══════════════════════════════════════════════
if page.startswith("①"):
    st.markdown('<div class="hero"><div style="font-size:13px;color:#E8A66B;letter-spacing:2px;font-weight:bold">ROADMAP</div>'
                '<div style="font-size:30px;font-weight:bold;margin-top:6px">에이전트 설계 로드맵</div>'
                '<div style="font-size:15px;color:#DCE6F2;margin-top:10px">단순한 첫 시도에서 출발해, 네 단계에 걸쳐 발전시켰습니다</div></div>',
                unsafe_allow_html=True)

    st.markdown("### 발전 과정")
    stages = [
        ("0", "첫 시도", "단순 국면 적응", "단순 RSM을 못 이김 (8.33 vs 8.29). 왜 안 될까?", RED),
        ("1", "발전 ①", "강건 선택", "정확도만이 아니라 안정성(분산)도 함께 본다 (품질손실)", COPPER),
        ("2", "발전 ②", "유사 구간 합치기", "마지막 구간만 쓰지 말고, 비슷한 과거 국면을 함께 학습", STEEL),
        ("3", "발전 ③", "통합 에이전트", "데이터 구성 × 방법을 모두 결합 탐색 → 최적 자동 선택", GREEN),
    ]
    for num, phase, title, desc, color in stages:
        st.markdown(f"""
<div style="display:flex;align-items:center;gap:16px;margin:10px 0;
     padding:16px 20px;border-radius:12px;background:#F4F6F9;border-left:5px solid {color}">
  <div style="min-width:70px;text-align:center">
    <div style="font-size:12px;color:#888">{phase}</div>
    <div style="font-size:26px;font-weight:bold;color:{color}">{num}</div>
  </div>
  <div>
    <div style="font-size:18px;font-weight:bold;color:#13233A">{title}</div>
    <div style="font-size:13px;color:#555;margin-top:3px">{desc}</div>
  </div>
</div>
""", unsafe_allow_html=True)
        if num != "3":
            st.markdown("<div style='text-align:center;color:#C87941;font-size:20px'>↓</div>", unsafe_allow_html=True)

    st.markdown("""
<div class="road">
<b>핵심 철학</b><br>
무엇도 미리 고정하지 않는다. 여러 경우를 다 해보고, 여러 검증 시점에서
일관되게(강건하게) 좋은 것을 자동 선택한다. 사람이 다 못 해보는 경우의 수를
대신 탐색해 최적을 제시하는 것이 에이전트의 존재 이유다.
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════
# ② 개발 과정
# ══════════════════════════════════════════════
elif page.startswith("②"):
    st.markdown('<div class="hero"><div style="font-size:13px;color:#E8A66B;letter-spacing:2px;font-weight:bold">DEVELOPMENT</div>'
                '<div style="font-size:28px;font-weight:bold;margin-top:6px">개발 과정 — 실험으로 검증</div>'
                '<div style="font-size:14px;color:#DCE6F2;margin-top:8px">각 단계를 실제 데이터로 검증한 결과입니다</div></div>',
                unsafe_allow_html=True)

    tabs = st.tabs(["1️⃣ 자르기", "2️⃣ 유사구간 합치기", "3️⃣ 부족 대응", "4️⃣ 강건 선택"])

    # --- 탭1: 자르기 ---
    with tabs[0]:
        st.markdown("**로컬 극값(피크/저점)에서 자동으로 국면을 나눕니다**")
        s1 = D["step1_cut"]
        dd = pd.to_datetime(pd.Series(s1["dates"])+"-01")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=dd, y=s1["prices"], line=dict(color=NAVY, width=2), name="LME"))
        for cp in s1["cut_points"]:
            fig.add_vline(x=dd.iloc[cp["idx"]].timestamp()*1000, line_dash="dash",
                          line_color=RED if cp["type"]=="피크" else GREEN, opacity=0.5)
        fig.update_layout(**THEME, height=340, margin=dict(t=20,b=20), yaxis_title="LME ($/톤)")
        st.plotly_chart(fig, use_container_width=True)
        pts = " · ".join([f"{cp['date']}({cp['type']})" for cp in s1["cut_points"]])
        st.markdown(f'<div class="res">🔍 자동 탐지된 전환점: {pts}<br>→ 코로나 저점·전쟁 피크 등 주요 국면 전환을 정확히 잡아냄</div>', unsafe_allow_html=True)

    # --- 탭2: 유사구간 ---
    with tabs[1]:
        st.markdown("**마지막 구간만 쓰는 건 낭비 → 비슷한 과거 국면도 함께 학습**")
        s2 = D["step2_similar"]
        fig = go.Figure()
        x = s2["labels"]
        for name, color in [("LME",NAVY),("유가",COPPER),("비트코인",STEEL)]:
            fig.add_trace(go.Bar(name=name, x=x, y=s2[name], marker_color=color))
        fig.update_layout(**THEME, height=340, margin=dict(t=20,b=20),
                          yaxis_title="MAPE (%)", barmode="group", legend=dict(orientation="h",y=1.12))
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('<div class="res">💡 LME·유가에서 <b>유사구간 합침</b>이 마지막 구간만은 물론, 안 자른 전체보다도 우수. 국면 순수성과 데이터 양을 동시에 확보하기 때문.</div>', unsafe_allow_html=True)

    # --- 탭3: 부족 대응 ---
    with tabs[2]:
        st.markdown("**자르면 데이터가 준다 → 여러 대응 옵션을 다 해보고 선택**")
        s3 = D["step3_shortage"]
        target = st.radio("데이터", ["LME","유가","비트코인"], horizontal=True, key="s3")
        fig = go.Figure(go.Bar(x=s3["options"], y=s3[target],
                        marker_color=[GREEN if o==s3["best"][target] else STEEL for o in s3["options"]]))
        fig.update_layout(**THEME, height=320, margin=dict(t=20,b=20), yaxis_title="MAPE (%)")
        st.plotly_chart(fig, use_container_width=True)
        st.markdown(f'<div class="res">🏆 {target} 최적: <b>{s3["best"][target]}</b> — 데이터마다 최적 대응이 다름. 그래서 고정 규칙이 아닌 "다 해보고 선택".</div>', unsafe_allow_html=True)

    # --- 탭4: 강건 선택 ---
    with tabs[3]:
        st.markdown("**정확도만 보면 놓치는 것 → 안정성(분산)까지 보는 품질손실 기준**")
        s4 = D["step4_robust"]
        c1, c2 = st.columns(2)
        with c1:
            fig = go.Figure(go.Bar(x=s4["methods"], y=s4["accuracy_mape"],
                            marker_color=[GREEN, STEEL]))
            fig.update_layout(**THEME, height=300, margin=dict(t=30,b=20),
                              title="정확도 기준 (MAPE, 낮을수록 좋음)", yaxis_title="MAPE(%)")
            st.plotly_chart(fig, use_container_width=True)
            st.caption("정확도 1위: RSM")
        with c2:
            fig = go.Figure(go.Bar(x=s4["methods"], y=s4["quality_loss"],
                            marker_color=[STEEL, GREEN]))
            fig.update_layout(**THEME, height=300, margin=dict(t=30,b=20),
                              title="품질손실 기준 (바이어스²+분산)", yaxis_title="품질손실")
            st.plotly_chart(fig, use_container_width=True)
            st.caption("품질손실 1위: SVR ← 역전!")
        st.markdown(f'<div class="res">🔄 <b>{s4["desc"]}</b><br>정확도로는 RSM이 이기지만, 안정성까지 보면 SVR이 역전. {s4["reproducibility"]}</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════
# ③ 에이전트 실행
# ══════════════════════════════════════════════
elif page.startswith("③"):
    st.markdown('<div class="hero"><div style="font-size:13px;color:#E8A66B;letter-spacing:2px;font-weight:bold">RUN</div>'
                '<div style="font-size:28px;font-weight:bold;margin-top:6px">에이전트 실행</div>'
                '<div style="font-size:14px;color:#DCE6F2;margin-top:8px">데이터를 선택하면 최적 조합을 자동으로 찾아 예측합니다</div></div>',
                unsafe_allow_html=True)

    if "agent" not in D:
        st.warning("agent 데이터가 없습니다.")
        st.stop()
    A = D["agent"]
    target = st.radio("데이터 선택", list(A.keys()), horizontal=True)
    d = A[target]

    c1,c2,c3 = st.columns(3)
    c1.metric("선택된 데이터 구성", d["best_data"])
    c2.metric("선택된 예측 방법", d["best_method"])
    c3.metric("검증 MAPE", f"{d['best_mape']}%", f"편차 {d['best_std']}")

    st.markdown(f'<div class="res">🤖 <b>에이전트 판단</b>: [{d["best_data"]} + {d["best_method"]}] 조합이 '
                f'평균 MAPE {d["best_mape"]}%, 시점편차 {d["best_std"]}로 가장 강건했습니다.</div>',
                unsafe_allow_html=True)

    st.markdown("### 미래 예측")
    hist, future = d["history"], d["future"]
    nh = len(hist)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=list(range(nh)), y=hist, name="실제(최근24개월)", line=dict(color=NAVY,width=2)))
    fig.add_trace(go.Scatter(x=list(range(nh-1, nh+len(future))), y=[hist[-1]]+future,
                             name="에이전트 예측", line=dict(color=COPPER,width=2,dash="dash")))
    fig.update_layout(**THEME, height=340, margin=dict(t=20,b=20), yaxis_title="가격",
                      legend=dict(orientation="h",y=1.1))
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### 탐색한 조합 (상위 8개, 강건 점수 순)")
    rows=[{"데이터 구성":c["data"],"방법":c["method"],"MAPE(%)":c["mape"],"시점편차":c["std"]} for c in d["combos"]]
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    st.markdown('<div class="step">💡 개별 요소로는 안 보이던 최적 조합이 결합 탐색에서 드러납니다. 비트코인은 개별로는 전체사용이 최선(46%)이었으나, 유사구간+증강+XGBoost 조합에서 12%로 급감했습니다.</div>', unsafe_allow_html=True)
