import streamlit as st
import pandas as pd
import plotly.express as px

@st.cache_data
def load_data():
    df = pd.read_csv('filtered_cities.csv')
    df.columns = [c.lower() for c in df.columns]
    if 'victim_age' in df.columns:
        df['victim_age'] = pd.to_numeric(df['victim_age'], errors='coerce').fillna(0)
        df['age_group'] = pd.cut(df['victim_age'], bins=[-1,19,29,39,49,59,69,79,200],
                                 labels=['10대 이하','20대','30대','40대','50대','60대','70대','80세 이상'])
    if 'reporteddate' in df.columns:
        df['year'] = df['reporteddate'].astype(str).str[:4]
        df['month'] = df['reporteddate'].astype(str).str[4:6]
    return df

df = load_data()

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
        fig_year = px.line(year_ct, x='year', y='count', markers=True)
        st.plotly_chart(fig_year, use_container_width=True)
    if 'month' in filtered.columns and not filtered.empty:
        st.subheader('월별 사건수')
        month_ct = filtered['month'].value_counts().sort_index().reset_index()
        month_ct.columns = ['month', 'count']
        fig_month = px.bar(month_ct, x='month', y='count', color='month')
        st.plotly_chart(fig_month, use_container_width=True)
    if 'age_group' in filtered.columns and not filtered.empty:
        st.subheader('피해자 나이대별 사건수')
        age_count = filtered['age_group'].value_counts().sort_index().reset_index()
        age_count.columns = ['age_group', 'count']
        fig_age = px.bar(age_count, x='age_group', y='count', color='age_group')
        st.plotly_chart(fig_age, use_container_width=True)
    if 'victim_race' in filtered.columns and not filtered.empty:
        st.subheader('피해자 인종별 사건수')
        race_count = filtered['victim_race'].value_counts().reset_index()
        race_count.columns = ['victim_race', 'count']
        fig_race = px.bar(race_count, x='victim_race', y='count', color='victim_race')
        st.plotly_chart(fig_race, use_container_width=True)
    if 'victim_sex' in filtered.columns and not filtered.empty:
        st.subheader('피해자 성별 사건수')
        sex_count = filtered['victim_sex'].value_counts().reset_index()
        sex_count.columns = ['victim_sex', 'count']
        fig_sex = px.bar(sex_count, x='victim_sex', y='count', color='victim_sex')
        st.plotly_chart(fig_sex, use_container_width=True)
    if 'disposition' in filtered.columns and not filtered.empty:
        st.subheader('사건 상태 분포')
        disp_count = filtered['disposition'].value_counts().reset_index()
        disp_count.columns = ['disposition', 'count']
        fig_disp = px.pie(disp_count, names='disposition', values='count')
        st.plotly_chart(fig_disp, use_container_width=True)
    if 'state' in filtered.columns and not filtered.empty:
        st.subheader('주별 사건수')
        state_count = filtered['state'].value_counts().reset_index()
        state_count.columns = ['state', 'count']
        fig_state = px.bar(state_count, x='state', y='count', color='state')
        st.plotly_chart(fig_state, use_container_width=True)

with tab2:
    st.subheader("사건 현장 지도")
    map_styles = ["carto-positron", "open-street-map", "satellite-streets"]
    map_style = st.radio("지도 스타일", map_styles, index=0, horizontal=True)
    color_candidates = [c for c in ['victim_race', 'disposition', 'victim_sex', 'year', 'city'] if c in filtered.columns]
    color_option = st.selectbox("마커 색상 기준", options=color_candidates, index=0 if color_candidates else None)
    size_candidates = [c for c in ['victim_age', 'year'] if c in filtered.columns and pd.api.types.is_numeric_dtype(filtered[c])]
    size_option = st.selectbox("마커 크기 기준", options=[None]+size_candidates, index=0)
    if {'lat', 'lon'}.issubset(filtered.columns) and not filtered.empty:
        fig_geo = px.scatter_mapbox(
            filtered,
            lat='lat',
            lon='lon',
            color=color_option,
            size=size_option if size_option else None,
            hover_name=filtered['city'] if 'city' in filtered.columns else None,
            hover_data={c: True for c in ['victim_race', 'victim_age', 'victim_sex', 'disposition', 'year', 'city'] if c in filtered.columns},
            zoom=3,
            mapbox_style=map_style,
            size_max=15,
            opacity=0.6,
        )
        st.plotly_chart(fig_geo, use_container_width=True)
        st.caption("색상/크기 기준을 원하는 컬럼(피해자 특성, 사건 상태 등)으로 바꿔가며 공간 분포를 확인할 수 있습니다.")
    else:
        st.warning("현재 필터 조건에서 위도/경도 정보가 부족하여 지도를 시각화할 수 없습니다.")

with tab3:
    st.subheader('상세 데이터 (100행)')
    st.dataframe(filtered.head(100))
    with st.expander("모든 데이터보기(확장)", expanded=False):
        st.dataframe(filtered)
    st.download_button(
        label="필터링된 데이터 다운로드",
        data=filtered.to_csv(index=False).encode('utf-8'),
        file_name='filtered_data.csv',
        mime='text/csv'
    )
