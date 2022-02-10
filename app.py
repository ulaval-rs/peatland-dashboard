import pandas
import streamlit as st
from peatland_time_series import calculate_sy, filter_sy, visualization

from peatland_dashboard import download, upload

st.set_page_config(layout='wide')
st.sidebar.title('Peatland analysis')

st.title('Peatland time series analysis')
uploaded_file = upload.uploader()

if uploaded_file is not None:
    time_series = upload.read_time_series_from_file(uploaded_file)

    sy = calculate_sy(time_series)

    st.sidebar.header('Sy filter')
    sy_min = st.sidebar.number_input('Sy min', value=0.0)
    sy_max = st.sidebar.number_input('Sy max', value=1)
    delta_h_min = st.sidebar.number_input('Delta h', value=0.01)
    precipitation_min = st.sidebar.number_input('Precipitation Sum min', value=10)
    precipitation_max = st.sidebar.number_input('Precipitation Sum max', value=100)

    sy = filter_sy(
        sy=sy,
        sy_min=sy_min,
        sy_max=sy_max,
        delta_h_min=delta_h_min,
        precipitation_sum_min=precipitation_min,
        precipitation_sum_max=precipitation_max
    )
    st.write(sy)

    # Allow the users to download the Sy CSV
    download.make_download_button(sy)

    # Show indexes in Depth graph
    show_indexes = st.checkbox('Show indexes in Depth plot', False)

    # Remove rows in the Sy Dataframe using indexes
    removed_indexes = st.multiselect('Remove rows (by index) when plotting:', options=[i for i in sy.index])
    sy = sy.drop(removed_indexes)

    st.sidebar.header('Water level')
    event_index = st.sidebar.slider('Event Index', 0, len(sy), 10)
    hour_before = st.sidebar.slider('Hour before', 0, 100, 10)
    hour_after = st.sidebar.slider('Hour after', 0, 100, 20)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader('Water level in function of time')
        st.markdown('##')
        fig_water_level = visualization.show_water_level(
            time_series=time_series,
            sy=sy,
            event_index=event_index,
            time_before=pandas.Timedelta(hours=hour_before),
            time_after=pandas.Timedelta(hours=hour_after),
            show_plot=False
        )
        st.pyplot(fig_water_level)

    with col2:
        st.subheader('Depth')
        fig_depth = visualization.show_depth(sy, show_plot=False, show_indexes=show_indexes)
        st.pyplot(fig_depth)
