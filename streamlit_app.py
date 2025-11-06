with tab2:
    st.subheader("사건 현장 지도 (시각화 옵션)")
    map_style = st.radio(
        "지도 스타일 선택", 
        ["carto-positron", "open-street-map", "satellite-streets"], 
        horizontal=True
    )
    group_option = st.selectbox(
        "지도 색상 기준",
        options=["victim_race", "disposition", "victim_sex", "year", "city"],
        index=0
    )
    size_option = st.selectbox(
        "마커 크기 기준",
        options=["victim_age", "year", None],
        index=0
    )

    if {'lat', 'lon'}.issubset(filtered.columns) and not filtered.empty:
        fig_geo = px.scatter_mapbox(
            filtered,
            lat='lat',
            lon='lon',
            color=group_option if group_option in filtered.columns else None,
            size=size_option if size_option in filtered.columns else None,
            hover_name='city' if 'city' in filtered.columns else None,
            hover_data={
                'victim_race': True,
                'victim_age': True,
                'victim_sex': True,
                'disposition': True,
                'year': True,
                'city': True
            },
            zoom=3,
            mapbox_style=map_style,
            size_max=15,
            opacity=0.6,
            title="미제 사건 지도 시각화"
        )
        st.plotly_chart(fig_geo, use_container_width=True)
        st.caption(
            "색상과 마커 크기를 원하는 기준(피해자 특성, 사건 상태 등)으로 바꿔가며 공간 분포 트렌드를 볼 수 있습니다."
        )
    else:
        st.info("지도 시각화를 위해서는 위도/경도 정보가 필요합니다.")

