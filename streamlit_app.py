import streamlit as st
import pandas as pd

# 데이터 불러오기
@st.cache_data
def load_data():
    df = pd.read_csv('filtered_cities.csv')
    return df

df = load_data()

# 대시보드 제목
st.title('미국 주요 4도시 미제 살인사건 대시보드 (New York, Los Angeles, Chicago, Houston)')

# 도시 선택 필터
cities = df['city'].unique()
selected_cities = st.multiselect('도시 선택', cities, default=list(cities))

filtered_df = df[df['city'].isin(selected_cities)]

# 기본 통계
st.write(f"선택된 사건 수: {len(filtered_df):,}건")

# 연도별 사건수 바 차트
st.subheader('연도별 사건 발생수')
if 'year' in filtered_df.columns:
    count_by_year = filtered_df.groupby('year').size()
    st.bar_chart(count_by_year)
else:
    st.info('year 컬럼이 없으면 막대 그래프가 표시되지 않습니다.')

# 도시별 사건수
st.subheader('도시별 사건수')
count_by_city = filtered_df['city'].value_counts()
st.bar_chart(count_by_city)

# 데이터 미리보기
st.subheader('상세 데이터 미리보기')
st.dataframe(filtered_df.head(100))

# csv 다운로드
st.download_button(
    label="필터링된 데이터 다운로드",
    data=filtered_df.to_csv(index=False).encode('utf-8'),
    file_name='filtered_data.csv',
    mime='text/csv'
)
