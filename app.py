import matplotlib.pyplot as plt
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

    with st.sidebar.expander('General'):
        delta_h_min = st.number_input('Delta h', value=0.01)
        sy_min = st.number_input('Sy min', value=0.0)
        sy_max = st.number_input('Sy max', value=1)

    with st.sidebar.expander('Sy filter'):
        precipitation_min = st.number_input('Precipitation Sum min', value=10)
        precipitation_max = st.number_input('Precipitation Sum max', value=100)
        depth_min = st.number_input('Depth min [m]', value=0)
        depth_max = st.number_input('Depth max [m]', value=100)
        date_beginning_min = st.date_input('Date beginning min', value=sy['date_beginning'].min())
        date_beginning_max = st.date_input('Date beginning max', value=sy['date_beginning'].max())
        date_ending_min = st.date_input('Date ending min', value=sy['date_ending'].min())
        date_ending_max = st.date_input('Date ending max', value=sy['date_ending'].max())

    sy = filter_sy(
        sy=sy,
        sy_min=sy_min,
        sy_max=sy_max,
        delta_h_min=delta_h_min,
        precipitation_sum_min=precipitation_min,
        precipitation_sum_max=precipitation_max,
        depth_min=depth_min,
        depth_max=depth_max,
        date_beginning_min=pandas.Timestamp(date_beginning_min),
        date_beginning_max=pandas.Timestamp(date_beginning_max),
        date_ending_min=pandas.Timestamp(date_ending_min),
        date_ending_max=pandas.Timestamp(date_ending_max),
    )
    st.write(sy)

    # Allow the users to download the Sy CSV
    download.make_download_button(sy)

    # Remove rows in the Sy Dataframe using indexes
    removed_indexes = st.multiselect('Remove rows (by index) when plotting:', options=[i for i in sy.index])
    sy = sy.drop(removed_indexes)

    st.sidebar.header('Plots')
    with st.sidebar.expander('Water level'):
        event_index = st.slider('Event Index', 0, len(sy), 10)
        hour_before = st.slider('Hour before', 0, 100, 10)
        hour_after = st.slider('Hour after', 0, 100, 20)

    with st.sidebar.expander('Depth'):
        # Show indexes in Depth graph
        show_indexes = st.checkbox('Show indexes in Depth plot', False)
        x_lim = st.slider('Limits Sy axis', 0.1, 2.0, value=(0.0, 1.0), step=0.1)
        y_lim = st.slider('Limits Depth axis [cm]', -120, 10, value=(-100, 0), step=1)
        as_power_law_axis = st.checkbox('Sy as power law axis', value=False)
        show_equation = st.checkbox('Show equation', value=True)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader('Water level in function of time')
        st.markdown('##')  # Simply making a space
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
        fig_depth = visualization.show_depth(
            sy,
            show_plot=False,
            show_indexes=show_indexes,
            x_limits=x_lim, y_limits=y_lim,
            show_legend=show_equation,
            power_law_x_axis=as_power_law_axis
        )

        st.pyplot(fig_depth)
