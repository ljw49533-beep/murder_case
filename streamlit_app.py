import streamlit as st
import pandas as pd
import plotly.express as px

# 데이터 불러오기
@st.cache_data
def load_data():
    df = pd.read_csv('filtered_cities.csv')
    return df

df = load_data()

# 지도 시각화를 위한 도시별 위도/경도 정의(없으면, 아래 표 참고해서 추가해야 함)
city_coords = {
    'New York': {'lat': 40.7128, 'lon': -74.0060},
    'Los Angeles': {'lat': 34.0522, 'lon': -118.2437},
    'Chicago': {'lat': 41.8781, 'lon': -87.6298},
    'Houston': {'lat': 29.7604, 'lon': -95.3698}
}

# 스트림릿 사이드바: 도시 선택
st.sidebar.title("도시 선택")
cities = df['city'].unique()
selected_cities = st.sidebar.multiselect('도시를 선택하세요', cities, default=list(cities))

filtered_df = df[df['city'].isin(selected_cities)]

# 대시보드 타이틀 및 통계
st.title('미국 미제 살인사건 대시보드')
st.write(f"선택된 사건 수: {len(filtered_df):,}건")

# 지도 시각화
st.subheader('미국 주요 도시 사건 분포')
if 'city' in df.columns and len(filtered_df) > 0:
    city_count = filtered_df['city'].value_counts().reset_index()
    city_count.columns = ['city', 'cases']
    city_count['lat'] = city_count['city'].apply(lambda c: city_coords[c]['lat'])
    city_count['lon'] = city_count['city'].apply(lambda c: city_coords[c]['lon'])

    fig = px.scatter_mapbox(city_count,
                            lat="lat", lon="lon", size="cases",
                            hover_name="city", hover_data=["cases"],
                            color="city", size_max=30, zoom=3,
                            mapbox_style="carto-positron", title="사건 분포 지도")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info('지도 시각화를 위한 도시 좌표 또는 선정된 사건 데이터가 필요합니다.')

# 연도별 차트
st.subheader('연도별 사건')
if 'year' in filtered_df.columns:
    yearly = filtered_df.groupby('year').size().reset_index(name='count')
    fig2 = px.bar(yearly, x='year', y='count', color='count', title='연도별 사건 발생수')
    st.plotly_chart(fig2, use_container_width=True)

# 데이터 보기
st.subheader('상세 데이터')
st.dataframe(filtered_df.head(100))

# 다운로드 버튼
st.download_button(
    label="필터링된 데이터 다운로드",
    data=filtered_df.to_csv(index=False).encode('utf-8'),
    file_name='filtered_data.csv',
    mime='text/csv'
)
