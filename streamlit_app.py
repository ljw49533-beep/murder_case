import streamlit as st
import pandas as pd
import plotly.express as px

@st.cache_data
def load_data():
    df = pd.read_csv('filtered_cities.csv')
    df.columns = [c.lower() for c in df.columns]
    if 'victimage' in df.columns:
        df['victimage'] = pd.to_numeric(df['victimage'], errors='coerce').fillna(0)
    if 'reporteddate' in df.columns:
        df['year'] = df['reporteddate'].astype(str).str[:4]
        df['month'] = df['reporteddate'].astype(str).str[4:6]
    # 나이그룹 생성
    if 'victimage' in df.columns:
        df['age_group'] = pd.cut(df['victimage'],
                                 bins=[-1,19,29,39,49,59,69,79,200],
                                 labels=['10대 이하','20대','30대','40대','50대','60대','70대','80세 이상'])
    return df

df = load_data()

# 필터 옵션 생성
cities = sorted(df['city'].dropna().unique()) if 'city' in df.columns else []
selected_cities = st.sidebar.multiselect('도시', cities, default=cities)

victim_races = sorted(df['victimrace'].dropna().unique()) if 'victimrace' in df.columns else []
selected_races = st.sidebar.multiselect('피해자 인종', victim_races, default=victim_races)

victim_sexes = sorted(df['victimsex'].dropna().unique()) if 'victimsex' in df.columns else []
selected_sexes = st.sidebar.multiselect('피해자 성별', victim_sexes, default=victim_sexes)

age_groups = sorted(df['age_group'].dropna().unique()) if 'age_group' in df.columns else []
selected_ages = st.sidebar.multiselect('피해자 나이대', age_groups, default=age_groups)

states = sorted(df['state'].dropna().unique()) if 'state' in df.columns else []
selected_states = st.sidebar.multiselect('주(state)', states, default=states)

dispositions = sorted(df['disposition'].dropna().unique()) if 'disposition' in df.columns else []
selected_dispositions = st.sidebar.multiselect('사건 상태', dispositions, default=dispositions)

# 데이터 필터링
filtered_df = df.copy()
if 'city' in df.columns:
    filtered_df = filtered_df[filtered_df['city'].isin(selected_cities)]
if 'victimrace' in df.columns and selected_races:
    filtered_df = filtered_df[filtered_df['victimrace'].isin(selected_races)]
if 'victimsex' in df.columns and selected_sexes:
    filtered_df = filtered_df[filtered_df['victimsex'].isin(selected_sexes)]
if 'age_group' in df.columns and selected_ages:
    filtered_df = filtered_df[filtered_df['age_group'].isin(selected_ages)]
if 'state' in df.columns and selected_states:
    filtered_df = filtered_df[filtered_df['state'].isin(selected_states)]
if 'disposition' in df.columns and selected_dispositions:
    filtered_df = filtered_df[filtered_df['disposition'].isin(selected_dispositions)]

st.title('미국 미제 살인사건 대시보드')
st.write(f"필터 적용 사건 수: {len(filtered_df):,}건")

# 사건 상태(미해결/검거/기타) 차트
if 'disposition' in filtered_df.columns and not filtered_df.empty:
    st.subheader('사건 상태별 분포')
    disp_ct = filtered_df['disposition'].value_counts().reset_index()
    disp_ct.columns = ['disposition', 'count']
    fig_disp = px.bar(disp_ct, x='disposition', y='count', color='disposition', title='사건 상태별 분포')
    st.plotly_chart(fig_disp, use_container_width=True)

# state(주)별 사건 분포
if 'state' in filtered_df.columns and not filtered_df.empty:
    st.subheader('주별 사건 분포')
    state_ct = filtered_df['state'].value_counts().reset_index()
    state_ct.columns = ['state', 'count']
    fig_state = px.bar(state_ct, x='state', y='count', color='state', title='주별 사건 분포')
    st.plotly_chart(fig_state, use_container_width=True)

# 실제 사건 현장 지도 시각화
if {'lat','lon','victimage','victimrace','city'}.issubset(filtered_df.columns) and not filtered_df.empty:
    st.subheader('사건 현장 지도(개별 사건)')
    fig_geo = px.scatter_mapbox(filtered_df,
        lat='lat', lon='lon',
        hover_name='city',
        hover_data={'victimrace': True, 'victimage': True, 'victimsex': True},
        color='victimrace',
        zoom=3, mapbox_style='carto-positron', size_max=6,
        title="개별 사건 오프라인 지도"
    )
    st.plotly_chart(fig_geo, use_container_width=True)

# 연도별/월별 사건수
if 'year' in filtered_df.columns and not filtered_df.empty:
    st.subheader('연도별 사건수')
    year_ct = filtered_df['year'].value_counts().sort_index().reset_index()
    year_ct.columns = ['year', 'count']
    fig_year = px.bar(year_ct, x='year', y='count', color='year', title='연도별 사건수')
    st.plotly_chart(fig_year, use_container_width=True)

if 'month' in filtered_df.columns and not filtered_df.empty:
    st.subheader('월별 사건수')
    month_ct = filtered_df['month'].value_counts().sort_index().reset_index()
    month_ct.columns = ['month', 'count']
    fig_month = px.bar(month_ct, x='month', y='count', color='month', title='월별 사건수')
    st.plotly_chart(fig_month, use_container_width=True)

# 피해자 인종/성별/나이대별 사건수
if 'victimrace' in filtered_df.columns and not filtered_df.empty:
    st.subheader('피해자 인종별 사건수')
    race_ct = filtered_df['victimrace'].value_counts().reset_index()
    race_ct.columns = ['victimrace', 'count']
    fig_race = px.bar(race_ct, x='victimrace', y='count', color='victimrace', title='피해자 인종별 사건수')
    st.plotly_chart(fig_race, use_container_width=True)

if 'victimsex' in filtered_df.columns and not filtered_df.empty:
    st.subheader('피해자 성별 사건수')
    sex_ct = filtered_df['victimsex'].value_counts().reset_index()
    sex_ct.columns = ['victimsex', 'count']
    fig_sex = px.bar(sex_ct, x='victimsex', y='count', color='victimsex', title='피해자 성별 사건수')
    st.plotly_chart(fig_sex, use_container_width=True)

if 'age_group' in filtered_df.columns and not filtered_df.empty:
    st.subheader('피해자 나이대별 사건수')
    age_ct = filtered_df['age_group'].value_counts().sort_index().reset_index()
    age_ct.columns = ['age_group', 'count']
    fig_age = px.bar(age_ct, x='age_group', y='count', color='age_group', title='피해자 나이대별 사건수')
    st.plotly_chart(fig_age, use_container_width=True)

# 데이터 상세보기/CSV 다운로드
st.subheader('상세 데이터 표 (100행)')
st.dataframe(filtered_df.head(100))
st.download_button(
    label="필터링된 데이터 다운로드",
    data=filtered_df.to_csv(index=False).encode('utf-8'),
    file_name='filtered_data.csv',
    mime='text/csv'
)
