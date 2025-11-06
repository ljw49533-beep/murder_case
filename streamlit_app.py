import streamlit as st
import pandas as pd
import plotly.express as px

# 데이터 불러오기와 컬럼 체크
@st.cache_data
def load_data():
    df = pd.read_csv('filtered_cities.csv')
    # 컬럼명 소문자로 변환
    df.columns = [c.lower() for c in df.columns]
    # age가 없는/비수치인 경우 0으로 채우기
    if 'age' in df.columns:
        df['age'] = pd.to_numeric(df['age'], errors='coerce').fillna(0)
    return df

df = load_data()

# 도메인 리스트 추출(결측치 제거)
cities = sorted(df['city'].dropna().unique()) if 'city' in df.columns else []
races = sorted(df['race'].dropna().unique()) if 'race' in df.columns else []
sexes = sorted(df['sex'].dropna().unique()) if 'sex' in df.columns else []

# 나이그룹 생성
if 'age' in df.columns:
    df['age_group'] = pd.cut(df['age'], bins=[-1,19,29,39,49,59,69,79,200],
                            labels=['10대 이하','20대','30대','40대','50대','60대','70대','80세 이상'])
    age_groups = sorted(df['age_group'].dropna().unique())
else:
    age_groups = []

# 스트림릿 사이드바 필터
st.sidebar.title("필터 옵션")
selected_cities = st.sidebar.multiselect('도시', cities, default=cities)
selected_races = st.sidebar.multiselect('인종', races, default=races)
selected_sexes = st.sidebar.multiselect('성별', sexes, default=sexes)
selected_ages = st.sidebar.multiselect('나이대', age_groups, default=age_groups)

# 필터링
filtered_df = df[
    df['city'].isin(selected_cities) &
    df['race'].isin(selected_races) &
    df['sex'].isin(selected_sexes) &
    (df['age_group'].isin(selected_ages) if 'age_group' in df.columns else True)
]

st.title('미국 미제 살인사건 대시보드')

st.write(f"필터 적용
