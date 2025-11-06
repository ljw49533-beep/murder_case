import streamlit as st
import pandas as pd
import plotly.express as px

@st.cache_data
def load_data():
    df = pd.read_csv('filtered_cities.csv')
    df.columns = [c.lower() for c in df.columns]
    if 'victimage' in df.columns:
        df['victimage'] = pd.to_numeric(df['victimage'], errors='coerce').fillna(0)
        df['age_group'] = pd.cut(df['victimage'],
                                 bins=[-1,19,29,39,49,59,69,79,200],
                                 labels=['10대 이하','20대','30대','40대','50대','60대','70대','80세 이상'])
    if 'reporteddate' in df.columns:
        df['year'] = df['reporteddate'].astype(str).str[:4]
        df['month'] = df['reporteddate'].astype(str).str[4:6]
    return df

df = load_data()

# 도시, 인종, 성별, 나이대 옵션을 빈 값 없이 준비
cities = sorted(list(set(df['city'].dropna()))) if 'city' in df.columns else []
victim_races = sorted(list(set(df['victimrace'].dropna()))) if 'victimrace' in df.columns else []
victim_sexes = sorted(list(set(df['victimsex'].dropna()))) if 'victimsex' in df.columns else []
age_groups = sorted(list(set(df['age_group'].dropna()))) if 'age_group' in df.columns else []

# 사이드바에서 옵션 선택
selected_cities = st.sidebar.multiselect('도시', cities, default=cities)
selected_races = st.sidebar.multiselect('피해자 인종', victim_races, default=victim_races)
selected_sexes = st.sidebar.multiselect('피해자 성별', victim_sexes, default=victim_sexes)
selected_ages = st.sidebar.multiselect('피해자 나이대', age_groups, default=age_groups)

# 필터 적용
filtered_df = df.copy()
if 'city' in df.columns:
    filtered_df = filtered_df[filtered_df['city'].isin(selected_cities)]
if 'victimrace' in df.columns:
    filtered_df = filtered_df[filtered_df['victimrace'].isin(selected_races)]
if 'victimsex' in df.columns:
    filtered_df = filtered_df[filtered_df['victimsex'].isin(selected_sexes)]
if 'age_group' in df.columns:
    filtered_df = filtered_df[filtered_df['age_group'].isin(selected_ages)]

st.title('미국 미제 살인사건 대시보드')
st.write(f"필터 적용 사건 수: {len(filtered_df):,}건")

city_coords = {
    'New York': {'lat': 40.7128, 'lon': -74.0060},
    'Los Angeles': {'lat': 34.0522, 'lon': -118.2437},
    'Chicago': {'lat': 41.8781, 'lon': -87.6298},
    'Houston': {'lat': 29.7604, 'lon': -95.3698}
}

if {'lat','lon','victimrace','city'}.issubset(filtered_df.columns) and not filtered_df.empty:
    st.subheader('사건 현장 지도')
    fig_geo = px.scatter_mapbox(
        filtered_df,
        lat='lat', lon='lon',
        hover_name='city',
        hover_data={'victimrace': True, 'victimage': True, 'victimsex': True},
        color='victimrace',
        zoom=3, mapbox_style='carto-positron', size_max=6
    )
    st.plotly_chart(fig_geo, use_container_width=True)

if 'victimrace' in filtered_df.columns and not filtered_df.empty:
    st.subheader('피해자 인종별 사건수')
    race_ct = filtered_df
