import streamlit as st
import pandas as pd
import plotly.express as px

@st.cache_data
def load_data():
    df = pd.read_csv('filtered_cities.csv')
    return df

df = load_data()

# 사이드바: 도시, 인종, 성별, 나이대 선택
st.sidebar.title("필터 옵션")
cities = df['city'].dropna().unique()
selected_cities = st.sidebar.multiselect('도시', cities, default=list(cities))

races = df['race'].dropna().unique()
selected_races = st.sidebar.multiselect('인종', races, default=list(races))

sexes = df['sex'].dropna().unique()
selected_sexes = st.sidebar.multiselect('성별', sexes, default=list(sexes))

# 나이대 분포 만들기
df['age_group'] = pd.cut(df['age'], bins=[0,19,29,39,49,59,69,79,120], labels=['10대 이하','20대','30대','40대','50대','60대','70대','80세 이상'])
age_groups = df['age_group'].dropna().unique()
selected_ages = st.sidebar.multiselect('나이대', age_groups, default=list(age_groups))

filtered_df = df[
    (df['city'].isin(selected_cities)) &
    (df['race'].isin(selected_races)) &
    (df['sex'].isin(selected_sexes)) &
    (df['age_group'].isin(selected_ages))
]

st.title('미국 미제 살인사건 대시보드')

st.write(f"필터링된 사건 수: {len(filtered_df):,}건")

# 지도 시각화
st.subheader('사건분포 지도(도시 기준)')
city_coords = {
    'New York': {'lat': 40.7128, 'lon': -74.0060},
    'Los Angeles': {'lat': 34.0522, 'lon': -118.2437},
    'Chicago': {'lat': 41.8781, 'lon': -87.6298},
    'Houston': {'lat': 29.7604, 'lon': -95.369
