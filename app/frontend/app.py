import streamlit as st
import pandas as pd
import requests
import plotly.express as px
from datetime import datetime
import random

st.set_page_config(
    page_title="Engagement Risk Intelligence Platform",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

API_URL = "http://127.0.0.1:8000"

st.markdown("""
<style>
    .main-header { font-size: 2.5rem; font-weight: 700; color: #1a3a5c; margin-bottom: 1rem; }
    .metric-card { background-color: #f8f9fa; border-radius: 10px; padding: 1.5rem; box-shadow: 0 2px 4px rgba(0,0,0,0.1); text-align: center; }
    .metric-value { font-size: 2rem; font-weight: 700; color: #1a3a5c; }
    .metric-label { font-size: 0.9rem; color: #6c757d; }
    .risk-high { color: #dc3545; font-weight: 600; }
    .risk-medium { color: #ffc107; font-weight: 600; }
    .risk-low { color: #28a745; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">🎯 Engagement Risk Intelligence Platform</div>', unsafe_allow_html=True)
st.markdown("*AI-powered risk monitoring and personalized engagement strategies*")

with st.sidebar:
    st.markdown("## 🧠 Intelligence Hub")
    st.markdown("---")
    page = st.radio(
        "Navigate",
        [
            "📊 Dashboard",
            "👤 User Profile",
            "🔍 Search Users",
            "🔎 Semantic Search",
            "📈 Risk Analytics",
            "🌎 Live Demographics",
            "🔄 What-If Simulator"
        ]
    )
    st.markdown("---")
    st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

@st.cache_data(ttl=10)
def api_health_check():
    try:
        response = requests.get(f"{API_URL}/", timeout=3)
        return response.status_code == 200
    except:
        return False

@st.cache_data(ttl=60)
def load_stats():
    try:
        response = requests.get(f"{API_URL}/stats", timeout=5)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        st.error(f"Error connecting to API: {e}")
        return None

@st.cache_data(ttl=60)
def load_users():
    try:
        response = requests.get(f"{API_URL}/users", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data and len(data) > 0:
                return pd.DataFrame(data)
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error loading users: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=60)
def load_high_risk_users():
    try:
        response = requests.get(f"{API_URL}/users/risk/high", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data and len(data) > 0:
                return pd.DataFrame(data)
        return pd.DataFrame()
    except:
        return pd.DataFrame()

@st.cache_data(ttl=60)
def load_demographics():
    try:
        response = requests.get(f"{API_URL}/demographics", timeout=5)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

if not api_health_check():
    st.error("🚨 Cannot connect to API. Please run: python app/backend/main.py")
    st.stop()

stats = load_stats()
users_df = load_users()
high_risk_df = load_high_risk_users()
demographics = load_demographics()

if not users_df.empty:
    st.sidebar.success(f"✅ {len(users_df)} users loaded")
else:
    st.sidebar.warning("⚠️ No users loaded")

# ========== DASHBOARD ==========
if page == "📊 Dashboard":
    st.markdown("## 📊 Dashboard Overview")
    if stats:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"""<div class="metric-card"><div class="metric-value">{stats['total_users']}</div><div class="metric-label">Total Users</div></div>""", unsafe_allow_html=True)
        with col2:
            st.markdown(f"""<div class="metric-card"><div class="metric-value">${stats.get('avg_spend', 0):,.0f}</div><div class="metric-label">Average Spend</div></div>""", unsafe_allow_html=True)
        with col3:
            st.markdown(f"""<div class="metric-card"><div class="metric-value">{stats.get('avg_risk_score', 0):.1f}</div><div class="metric-label">Avg Risk Score</div></div>""", unsafe_allow_html=True)
        with col4:
            risk_levels = stats.get('risk_levels', {})
            high_count = risk_levels.get('High', 0)
            st.markdown(f"""<div class="metric-card"><div class="metric-value" style="color:#dc3545;">{high_count}</div><div class="metric-label">High-Risk Users</div></div>""", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if not users_df.empty and 'risk_level' in users_df.columns:
            fig = px.pie(users_df, names='risk_level', title='Risk Level Distribution', color='risk_level',
                         color_discrete_map={'Low':'#28a745','Medium':'#ffc107','High':'#dc3545'})
            st.plotly_chart(fig, use_container_width=True)
    with col2:
        if not users_df.empty and 'risk_score' in users_df.columns:
            fig = px.histogram(users_df, x='risk_score', nbins=20, title='Risk Score Distribution', color_discrete_sequence=['#1a3a5c'])
            fig.update_layout(bargap=0.1)
            st.plotly_chart(fig, use_container_width=True)
    
    if not high_risk_df.empty:
        st.markdown("## 🚨 High-Risk Users")
        cols = [c for c in ['user_id','age','state','total_spend','visit_frequency','risk_score'] if c in high_risk_df.columns]
        if cols:
            st.dataframe(high_risk_df[cols], use_container_width=True)

# ========== USER PROFILE ==========
elif page == "👤 User Profile":
    st.markdown("## 👤 User Profile")
    user_id = st.number_input("Enter User ID", min_value=1, max_value=1000, value=1, step=1)
    
    if st.button("🔍 Load Profile", type="primary"):
        with st.spinner("Loading..."):
            try:
                response = requests.get(f"{API_URL}/users/{user_id}", timeout=5)
                if response.status_code == 200:
                    user = response.json()
                    if user:
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown("### User Information")
                            st.write(f"**User ID:** {user.get('user_id', 'N/A')}")
                            st.write(f"**Age:** {user.get('age', 'N/A')}")
                            st.write(f"**State:** {user.get('state', 'N/A')}")
                            st.write(f"**Segment:** {user.get('segment', 'N/A')}")
                            st.write(f"**Join Date:** {user.get('join_date', 'N/A')}")
                        with col2:
                            st.markdown("### Risk Profile")
                            risk_level = user.get('risk_level', 'Unknown')
                            color = {"High":"#dc3545","Medium":"#ffc107","Low":"#28a745"}.get(risk_level, "#6c757d")
                            st.markdown(f"**Risk Level:** <span style='color:{color};font-weight:bold'>{risk_level}</span>", unsafe_allow_html=True)
                            st.write(f"**Risk Score:** {user.get('risk_score', 'N/A')}/100")
                            st.write(f"**Total Spend:** ${user.get('total_spend', 0):.2f}")
                            st.write(f"**Visit Frequency:** {user.get('visit_frequency', 'N/A')} days")
                            st.write(f"**Game Types:** {user.get('game_types', 'N/A')}")
                        
                        st.markdown("---")
                        st.markdown("### 🔍 Risk Factors Explained")
                        risk_factors = []
                        if user.get('age', 0) < 25:
                            risk_factors.append("⚠️ Young age (<25) is a risk factor")
                        if user.get('age', 0) > 60:
                            risk_factors.append("⚠️ Older age (>60) is a risk factor")
                        if user.get('total_spend', 0) > 2000:
                            risk_factors.append(f"💰 High spend (${user.get('total_spend', 0):.2f}) is a risk factor")
                        if user.get('visit_frequency', 0) < 5:
                            risk_factors.append(f"⏰ Frequent visits ({user.get('visit_frequency', 0)} days) is a risk factor")
                        if user.get('median_income', 0) < 50000:
                            risk_factors.append(f"📉 Lower income (${user.get('median_income', 0):.0f}) is a risk factor")
                        if risk_factors:
                            for factor in risk_factors:
                                st.write(factor)
                        else:
                            st.write("✅ No significant risk factors identified")
                        
                        st.markdown("---")
                        st.markdown("## 🤖 AI-Powered Recommendations")
                        with st.spinner("Generating..."):
                            try:
                                rec_resp = requests.post(f"{API_URL}/recommendations", json={"user_id": user_id}, timeout=30)
                                if rec_resp.status_code == 200:
                                    rec = rec_resp.json()
                                    col1, col2 = st.columns(2)
                                    with col1:
                                        st.markdown("### 💡 Recommendation")
                                        st.info(rec.get('recommendation', 'No recommendation available'))
                                    with col2:
                                        st.markdown("### 🛡️ Intervention Strategy")
                                        st.success(rec.get('intervention_strategy', 'No intervention strategy available'))
                                else:
                                    st.error(f"Error: {rec_resp.status_code}")
                            except Exception as e:
                                st.error(f"Error: {e}")
            except Exception as e:
                st.error(f"Error: {e}")

# ========== SEARCH USERS ==========
elif page == "🔍 Search Users":
    st.markdown("## 🔍 Search Users")
    
    if users_df.empty:
        st.warning("No user data loaded. Please check if the API is running and data exists.")
        st.info("Try: 1) Restart API  2) Check data files in app/data/")
    else:
        search_term = st.text_input("Search by User ID, State, or Segment", "")
        if search_term:
            filtered = users_df.copy()
            if 'user_id' in filtered.columns:
                filtered = filtered[filtered['user_id'].astype(str).str.contains(search_term, case=False)]
            if 'state' in filtered.columns and filtered.empty:
                filtered = users_df[users_df['state'].str.contains(search_term, case=False)]
            if 'segment' in filtered.columns and filtered.empty:
                filtered = users_df[users_df['segment'].str.contains(search_term, case=False)]
            
            if not filtered.empty:
                st.dataframe(filtered, use_container_width=True)
                col1, col2 = st.columns(2)
                with col1:
                    if 'risk_level' in filtered.columns:
                        fig = px.pie(filtered, names='risk_level', title='Risk Distribution')
                        st.plotly_chart(fig, use_container_width=True)
                with col2:
                    st.markdown("### Summary")
                    st.write(f"**Total Users:** {len(filtered)}")
                    if 'risk_level' in filtered.columns:
                        st.write(f"**High Risk:** {len(filtered[filtered['risk_level'] == 'High'])}")
                    if 'total_spend' in filtered.columns:
                        st.write(f"**Avg Spend:** ${filtered['total_spend'].mean():.2f}")
                    if 'risk_score' in filtered.columns:
                        st.write(f"**Avg Risk Score:** {filtered['risk_score'].mean():.1f}")
            else:
                st.warning("No users found.")

# ========== SEMANTIC SEARCH ==========
elif page == "🔎 Semantic Search":
    st.markdown("## 🔎 Semantic Player Search (AI-Powered)")
    st.caption("Search for players using natural language (e.g., 'high-risk players in California')")
    
    search_query = st.text_input("Enter your search query:", placeholder="e.g., high-value players in Texas")
    
    col1, col2 = st.columns(2)
    with col1:
        risk_filter = st.selectbox(
            "Risk Level Filter",
            ["Auto-Detect", "High", "Medium", "Low", "All"],
            index=0
        )
    with col2:
        segment_filter = st.selectbox(
            "Segment Filter",
            ["Auto-Detect", "Casual", "Regular", "Frequent", "High-Value", "VIP", "All"],
            index=0
        )
    
    n_results = st.slider("Number of results", min_value=5, max_value=50, value=10)
    
    if st.button("🔍 Search", type="primary") and search_query:
        with st.spinner("Searching..."):
            try:
                payload = {"query": search_query, "n_results": n_results}
                
                if risk_filter not in ["Auto-Detect", "All"]:
                    payload["risk_level"] = risk_filter
                if segment_filter not in ["Auto-Detect", "All"]:
                    payload["segment"] = segment_filter
                
                response = requests.post(
                    f"{API_URL}/search/semantic",
                    json=payload,
                    timeout=10
                )
                if response.status_code == 200:
                    data = response.json()
                    results = data.get('results', [])
                    filters_applied = data.get('filters_applied', {})
                    
                    if results:
                        st.markdown(f"### Found {len(results)} players")
                        st.caption(f"Filters applied: {filters_applied if filters_applied else 'None'}")
                        
                        df = pd.DataFrame(results)
                        st.dataframe(df, use_container_width=True)
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if 'risk_level' in df.columns:
                                risk_counts = df['risk_level'].value_counts()
                                fig = px.pie(risk_counts, values=risk_counts.values, names=risk_counts.index, title='Risk Distribution')
                                st.plotly_chart(fig, use_container_width=True)
                        with col2:
                            if 'segment' in df.columns:
                                segment_counts = df['segment'].value_counts()
                                fig = px.pie(segment_counts, values=segment_counts.values, names=segment_counts.index, title='Segment Distribution')
                                st.plotly_chart(fig, use_container_width=True)
                        
                        st.markdown("### Summary")
                        st.write(f"**Avg Age:** {df['age'].mean():.1f}")
                        st.write(f"**Avg Spend:** ${df['total_spend'].mean():.2f}")
                        st.write(f"**Avg Risk Score:** {df['risk_score'].mean():.1f}")
                    else:
                        st.warning("No results found. Try a different query.")
                else:
                    st.error("Search failed. Please try again.")
            except Exception as e:
                st.error(f"Error: {e}")

# ========== RISK ANALYTICS ==========
elif page == "📈 Risk Analytics":
    st.markdown("## 📈 Risk Analytics")
    
    if users_df.empty:
        st.warning("No user data available.")
    else:
        col1, col2 = st.columns(2)
        with col1:
            if 'total_spend' in users_df.columns and 'risk_score' in users_df.columns and 'risk_level' in users_df.columns:
                fig = px.scatter(users_df, x='total_spend', y='risk_score', color='risk_level',
                                 hover_data=['user_id', 'state', 'segment'], title='Spend vs Risk Score',
                                 color_discrete_map={'Low':'#28a745','Medium':'#ffc107','High':'#dc3545'})
                st.plotly_chart(fig, use_container_width=True)
        with col2:
            if 'state' in users_df.columns and 'risk_score' in users_df.columns:
                state_risk = users_df.groupby('state')['risk_score'].mean().reset_index()
                fig = px.bar(state_risk.sort_values('risk_score', ascending=False).head(10),
                             x='state', y='risk_score', title='Top 10 States by Average Risk Score',
                             color='risk_score', color_continuous_scale='Reds')
                st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("## 📊 Detailed User Data")
        cols = [c for c in ['user_id','age','state','segment','total_spend','visit_frequency','risk_score','risk_level'] if c in users_df.columns]
        if cols:
            st.dataframe(users_df[cols], use_container_width=True)

# ========== LIVE DEMOGRAPHICS ==========
elif page == "🌎 Live Demographics":
    st.markdown("## 🌎 Live US Demographic Data (Census API)")
    st.caption("Real demographic data fetched from the US Census Bureau API")
    
    if demographics is None:
        st.warning("No demographic data available. Please check if the API is running.")
    else:
        states_data = demographics.get('states', [])
        total_users = demographics.get('total_users', 0)
        avg_income = demographics.get('avg_income', 0)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{total_users:,}</div>
                <div class="metric-label">Total Users</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">${avg_income:,.0f}</div>
                <div class="metric-label">Average Income</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{len(states_data)}</div>
                <div class="metric-label">States Represented</div>
            </div>
            """, unsafe_allow_html=True)
        
        if states_data:
            states_df = pd.DataFrame(states_data)
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig = px.bar(
                    states_df.sort_values('median_income', ascending=False).head(10),
                    x='state',
                    y='median_income',
                    title='Top 10 States by Median Income',
                    color='median_income',
                    color_continuous_scale='Greens'
                )
                fig.update_layout(xaxis_title="State", yaxis_title="Median Income ($)")
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown("### 📋 State Demographic Data")
                st.dataframe(
                    states_df.sort_values('median_income', ascending=False),
                    use_container_width=True
                )
        else:
            st.info("No state demographic data available.")

# ========== WHAT-IF SIMULATOR ==========
elif page == "🔄 What-If Simulator":
    st.markdown("## 🔄 What-If Risk Simulator")
    st.caption("Adjust player behavior and see how risk score changes in real-time")
    
    col1, col2 = st.columns(2)
    
    with col1:
        age = st.slider("Age", 18, 75, 35)
        total_spend = st.slider("Total Spend ($)", 0, 5000, 1500)
        visit_frequency = st.slider("Days Since Last Visit", 1, 30, 10)
        median_income = st.slider("Median Income ($)", 30000, 150000, 70000)
    
    with col2:
        base_risk = 0
        if age < 25 or age > 60:
            base_risk += 15
        if total_spend > 2000:
            base_risk += 30
        elif total_spend > 1000:
            base_risk += 15
        if visit_frequency < 5:
            base_risk += 20
        elif visit_frequency < 10:
            base_risk += 10
        if median_income < 50000:
            base_risk += 10
        elif median_income > 100000:
            base_risk -= 5
        
        risk_score = max(0, min(100, base_risk + random.randint(-5, 5)))
        risk_level = 'Low' if risk_score < 30 else 'Medium' if risk_score < 60 else 'High'
        
        st.markdown("### Risk Profile")
        color = {"High":"#dc3545","Medium":"#ffc107","Low":"#28a745"}.get(risk_level, "#6c757d")
        st.markdown(f"**Risk Level:** <span style='color:{color};font-weight:bold;font-size:24px;'>{risk_level}</span>", unsafe_allow_html=True)
        st.markdown(f"**Risk Score:** {risk_score}/100")
        
        st.markdown("---")
        st.markdown("#### Risk Meter")
        st.progress(risk_score/100)
        
        st.markdown("#### Risk Factors")
        if age < 25:
            st.write("⚠️ Young age (<25) increases risk")
        if age > 60:
            st.write("⚠️ Older age (>60) increases risk")
        if total_spend > 2000:
            st.write("💰 High spend (>$2000) increases risk")
        if visit_frequency < 5:
            st.write("⏰ Frequent visits (<5 days) increases risk")
        if median_income < 50000:
            st.write("📉 Low income increases risk")
        
        st.markdown("---")
        st.markdown("#### Recommendations")
        if risk_level == "High":
            st.error("🔴 Immediate intervention recommended")
        elif risk_level == "Medium":
            st.warning("🟡 Monitor closely")
        else:
            st.success("🟢 Low risk - continue monitoring")

st.markdown("---")
st.caption("© 2026 Engagement Risk Intelligence Platform | Built with Python, FastAPI, Streamlit, and Groq")