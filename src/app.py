"""
PharmaSim — Streamlit 界面
药物市场准入模拟平台的交互界面
"""

import streamlit as st
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

st.set_page_config(page_title="PharmaSim", page_icon="💊", layout="wide")

st.title("💊 PharmaSim — 药物市场准入模拟平台")
st.markdown("基于多Agent的药物市场准入仿真系统，模拟医生、患者、医保等多方博弈")


# 侧边栏
page = st.sidebar.selectbox(
    "功能模块",
    ["🏠 首页", "🧪 快速模拟", "⚖️ 药物对比", "📊 结果分析", "📋 模拟模板"]
)


if page == "🏠 首页":
    st.header("欢迎使用 PharmaSim")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("**🧪 快速模拟**\n设置药物参数，运行单药物市场准入模拟")
    with col2:
        st.info("**⚖️ 药物对比**\n多药物并行模拟，对比市场表现")
    with col3:
        st.info("**📊 结果分析**\n深度分析模拟结果，生成报告")
    
    st.markdown("---")
    st.markdown("""
    ### 平台特点
    - 🤖 **多Agent仿真** — 400+医生、1000+患者、400+专家的多维度博弈
    - 🌐 **社交网络** — 基于真实社交关系的信息传播模拟
    - 📊 **实时分析** — 月度快照，追踪市场渗透、医生采纳、收入变化
    - 🔄 **场景对比** — 不同定价、疗效策略的快速对比分析
    """)


elif page == "🧪 快速模拟":
    st.header("🧪 快速模拟")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("药物信息")
        drug_name = st.text_input("药物名称", "免疫检查点抑制剂X")
        indication = st.text_input("适应症", "非小细胞肺癌")
        mechanism = st.text_input("作用机制", "PD-1/PD-L1抑制")
        price = st.number_input("月治疗费用 (¥)", 0.0, 200000.0, 28000.0, 1000.0)
        efficacy = st.slider("疗效评分", 0.0, 1.0, 0.72, 0.01)
        safety = st.slider("安全性评分", 0.0, 1.0, 0.85, 0.01)
    
    with col2:
        st.subheader("模拟参数")
        num_agents = st.number_input("Agent总数", 100, 5000, 1800, 100)
        sim_months = st.number_input("模拟月数", 6, 60, 24, 1)
        random_seed = st.number_input("随机种子", 1, 99999, 42)
        regions = st.multiselect(
            "模拟地区",
            ["北京", "上海", "广州", "深圳", "成都", "武汉", "杭州", "南京", "重庆", "天津", "西安", "长沙"],
            default=["北京", "上海", "广州", "深圳"]
        )
    
    if st.button("🚀 开始模拟", type="primary"):
        with st.spinner("正在运行模拟...（可能需要几分钟）"):
            try:
                from simulation_engine import PharmaSimEngine
                engine = PharmaSimEngine()
                result = engine.quick_simulate(
                    drug_name=drug_name,
                    indication=indication,
                    mechanism=mechanism,
                    price=price,
                    efficacy_rate=efficacy,
                    safety_score=safety,
                    num_agents=num_agents,
                    simulation_months=sim_months,
                    random_seed=random_seed,
                    regions=regions
                )
                
                st.success("模拟完成！")
                
                metrics = result.get("final_metrics", {})
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("市场渗透率", f"{metrics.get('market_penetration', 0):.1%}")
                col2.metric("医生采纳率", f"{metrics.get('doctor_adoption_rate', 0):.1%}")
                col3.metric("累计收入", f"¥{metrics.get('total_revenue', 0):,.0f}")
                col4.metric("患者满意度", f"{metrics.get('patient_satisfaction', 0):.2f}")
                
                # 月度趋势
                snapshots = result.get("monthly_snapshots", [])
                if snapshots:
                    st.subheader("月度趋势")
                    import pandas as pd
                    df = pd.DataFrame(snapshots)
                    if "market_penetration" in df.columns:
                        st.line_chart(df[["month", "market_penetration"]].set_index("month"))
                
            except Exception as e:
                st.error(f"模拟出错: {e}")


elif page == "⚖️ 药物对比":
    st.header("⚖️ 药物对比模拟")
    
    num_drugs = st.number_input("对比药物数量", 2, 5, 2)
    
    drugs = []
    for i in range(num_drugs):
        st.subheader(f"药物 {i+1}")
        col1, col2, col3 = st.columns(3)
        name = col1.text_input(f"名称", f"药物{chr(65+i)}", key=f"dname_{i}")
        efficacy = col2.slider(f"疗效", 0.0, 1.0, 0.7 - 0.05*i, key=f"eff_{i}")
        price = col3.number_input(f"月费(¥)", 0.0, 200000.0, 20000 + 5000*i, key=f"price_{i}")
        drugs.append({"name": name, "indication": "示例适应症", "efficacy_rate": efficacy, "price": price, "safety_score": 0.8})
    
    if st.button("⚖️ 开始对比模拟", type="primary"):
        with st.spinner("正在并行模拟..."):
            try:
                from simulation_engine import PharmaSimEngine
                engine = PharmaSimEngine()
                result = engine.compare_drugs(drugs, num_agents=500, simulation_months=12)
                
                st.success("对比完成！")
                
                import pandas as pd
                comparison = result.get("comparison", [])
                if comparison:
                    df = pd.DataFrame(comparison)
                    st.dataframe(df, use_container_width=True)
                
            except Exception as e:
                st.error(f"对比出错: {e}")


elif page == "📊 结果分析":
    st.header("📊 结果分析")
    
    st.markdown("上传模拟结果JSON文件或粘贴JSON数据进行分析")
    
    json_input = st.text_area("粘贴模拟结果JSON", height=300)
    
    if json_input and st.button("分析"):
        try:
            result = json.loads(json_input)
            from analysis import SimulationAnalyzer
            analyzer = SimulationAnalyzer(result)
            
            report = analyzer.generate_report()
            
            st.subheader("执行摘要")
            st.text(report["executive_summary"])
            
            st.subheader("市场渗透分析")
            st.json(report["market_penetration"])
            
            st.subheader("收入分析")
            st.json(report["revenue"])
            
        except Exception as e:
            st.error(f"分析出错: {e}")


elif page == "📋 模拟模板":
    st.header("📋 模拟模板库")
    
    template_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "simulation-templates.json")
    if os.path.exists(template_path):
        with open(template_path) as f:
            templates = json.load(f)
        
        for tpl in templates.get("templates", []):
            with st.expander(f"📄 {tpl['name']}"):
                st.markdown(f"**描述**: {tpl.get('description', '')}")
                st.markdown(f"**适应症**: {tpl.get('indication', '')}")
                st.json(tpl.get("default_params", {}))
    else:
        st.warning("未找到模拟模板文件")


st.sidebar.markdown("---")
st.sidebar.markdown("### 关于")
st.sidebar.markdown("PharmaSim v2.0\n\n多Agent药物市场准入模拟平台")
