import streamlit as st
import pandas as pd
import plotly.express as px

@st.cache_data
def load_data():
    df = pd.read_csv('filtered_cities.csv')
    df.columns = [c.lower() for c in df.columns]
    if 'age' in df.columns:
        df['age'] = pd.to_numeric(df['age'], errors='coerce').fillna(0)
    return df

df = load_data()

cities = sorted(df['city'].dropna().unique()) if 'city' in df.columns else []
races = sorted(df['race'].dropna().unique()) if 'race' in df.columns else []
sexes = sorted(df['sex'].dropna().unique()) if 'sex' in df.columns else []

if 'age' in df.columns:
    df['age_group'] = pd.cut(df['age'], bins=[-1,19,29,39,49,59,69,79,200],
                            labels=['10대 이하','20대','30대','40대','50대','60대','70대','80세 이상'])
    age_groups = sorted(df['age_group'].dropna().unique())
else:
    age_groups = []

st.sidebar.title("필터 옵션")
selected_cities = st.sidebar.multiselect('도시', cities, default=cities)
selected_races = st.sidebar.multiselect('인종', races, default=races)
selected_sexes = st.sidebar.multiselect('성별', sexes, default=sexes)
selected_ages = st.sidebar.multiselect('나이대', age_groups, default=age_groups)

filtered_df = df[
    df['city'].isin(selected_cities) &
    df['race'].isin(selected_races) &
    df['sex'].isin(selected_sexes) &
    (df['age_group'].isin(selected_ages) if 'age_group' in df.columns else True)
]

st.title('미국 미제 살인사건 대시보드')

st.write(f"필터 적용 사건 수: {len(filtered_df):,}건")

city_coords = {
    'New York': {'lat': 40.7128, 'lon': -74.0060},
    'Los Angeles': {'lat': 34.0522, 'lon': -118.2437},
    'Chicago': {'lat': 41.8781, 'lon': -87.6298},
    'Houston': {'lat': 29.7604, 'lon': -95.3698}
}

if 'city' in filtered_df.columns and len(filtered_df) > 0:
    city_count = filtered_df['city'].value_counts().reset_index()
    city_count.columns = ['city', 'cases']
    city_count['lat'] = city_count['city'].map(lambda c: city_coords[c]['lat'] if c in city_coords else None)
    city_count['lon'] = city_count['city'].map(lambda c: city_coords[c]['lon'] if c in city_coords else None)
    city_count = city_count.dropna(subset=['lat', 'lon'])

    fig_map = px.scatter_mapbox(city_count,
        lat="lat", lon="lon", size="cases", color="city",
        hover_name="city", hover_data=["cases"],
        size_max=30, zoom=3, mapbox_style="carto-positron",
        title="사건분포 지도"
    )
    st.plotly_chart(fig_map, use_container_width=True)

if 'race' in filtered_df.columns:
    st.subheader('인종별 사건수')
    race_count = filtered_df['race'].value_counts().reset_index()
    race_count.columns = ['race', 'cases']
    fig_race = px.bar(race_count, x='race', y='cases', color='race', title='인종별 사건수')
    st.plotly_chart(fig_race, use_container_width=True)

if 'sex' in filtered_df.columns:
    st.subheader('성별 사건수')
    sex_count = filtered_df['sex'].value_counts().reset_index()
    sex_count.columns = ['sex', 'cases']
    fig_sex = px.bar(sex_count, x='sex', y='cases', color='sex', title='성별 사건수')
    st.plotly_chart(fig_sex, use_container_width=True)

if 'age_group' in filtered_df.columns:
    st.subheader('나이대별 사건수')
    age_count = filtered_df['age_group'].value_counts().sort_index().reset_index()
    age_count.columns = ['age_group', 'cases']
    fig_age = px.bar(age_count, x='age_group', y='cases', color='age_group', title='나이대별 사건수')
    st.plotly_chart(fig_age, use_container_width=True)

if 'year' in filtered_df.columns:
    st.subheader('연도별 사건수')
    yearly = filtered_df.groupby('year').size().reset_index(name='count')
    fig_year = px.bar(yearly, x='year', y='count', color='count', title='연도별 사건수')
    st.plotly_chart(fig_year, use_container_width=True)

st.subheader('상세 데이터 미리보기')
st.dataframe(filtered_df.head(100))

st.download_button(
    label="필터링된 데이터 다운로드",
    data=filtered_df.to_csv(index=False).encode('utf-8'),
    file_name='filtered_data.csv',
    mime='text/csv'
)
