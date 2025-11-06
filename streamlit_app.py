import streamlit as st
import pandas as pd
import plotly.express as px

@st.cache_data
def load_data():
    df = pd.read_csv('filtered_cities.csv')
    df.columns = [c.lower() for c in df.columns]
    # victim_age 숫자 변환
    if 'victim_age' in df.columns:
        df['victim_age'] = pd.to_numeric(df['victim_age'], errors='coerce').fillna(0)
        df['age_group'] = pd.cut(df['victim_age'], bins=[-1,19,29,39,49,59,69,79,200],
                                 labels=['10대 이하','20대','30대','40대','50대','60대','70대','80세 이상'])
    # 연도/월 파싱
    if 'reporteddate' in df.columns:
        df['year'] = df['reporteddate'].astype(str).str[:4]
        df['month'] = df['reporteddate'].astype(str).str[4:6]
    return df

df = load_data()

# 필터 옵션
cities = sorted(df['city'].dropna().unique()) if 'city' in df.columns else []
victim_races = sorted(df['victim_race'].dropna().unique()) if 'victim_race' in df.columns else []
victim_sexes = sorted(df['victim_sex'].dropna().unique()) if 'victim_sex' in df.columns else []
age_groups = sorted(df['age_group'].dropna().unique()) if 'age_group' in df.columns else []
states = sorted(df['state'].dropna().unique()) if 'state' in df.columns else []
dispositions = sorted(df['disposition'].dropna().unique()) if 'disposition' in df.columns else []

selected_cities = st.sidebar.multiselect('도시', cities, default=cities)
selected_races = st.sidebar.multiselect('피해자 인종', victim_races, default=victim_races)
selected_sexes = st.sidebar.multiselect('피해자 성별', victim_sexes, default=victim_sexes)
selected_ages = st.sidebar.multiselect('피해자 나이대', age_groups, default=age_groups)
selected_states = st.sidebar.multiselect('주(state)', states, default=states)
selected_dispositions = st.sidebar.multiselect('사건 상태', dispositions, default=dispositions)

# 필터 적용
filtered = df.copy()
if 'city' in df.columns:
    filtered = filtered[filtered['city'].isin(selected_cities)]
if 'victim_race' in df.columns:
    filtered = filtered[filtered['victim_race'].isin(selected_races)]
if 'victim_sex' in df.columns:
    filtered = filtered[filtered['victim_sex'].isin(selected_sexes)]
if 'age_group' in df.columns:
    filtered = filtered[filtered['age_group'].isin(selected_ages)]
if 'state' in df.columns:
    filtered = filtered[filtered['state'].isin(selected_states)]
if 'disposition' in df.columns:
    filtered = filtered[filtered['disposition'].isin(selected_dispositions)]

st.title('미국 미제 살인사건 대시보드')
st.write(f"필터 적용 사건 수: {len(filtered):,}건")

tab1, tab2, tab3 = st.tabs(["요약 그래프", "지도 분석", "상세 데이터"])

with tab1:
    if 'year' in filtered.columns and not filtered.empty:
        st.subheader('연도별 사건수')
        year_ct = filtered['year'].value_counts().sort_index().reset_index()
        year_ct.columns = ['year', 'count']
        fig_year = px.line(year_ct, x='year', y='count', markers
