import os

import pandas
import streamlit as st
from peatland_time_series import calculate_sy, filter_sy, visualization, read_time_series

from peatland_dashboard import download, upload

# Session state
if 'time_series' not in st.session_state:
    st.session_state['time_series'] = None

# App
st.set_page_config(layout='wide')
st.markdown(
    """
    <style>
    [data-testid="stSidebar"][aria-expanded="true"] > div:first-child {
        width: 28em;
    }
    [data-testid="stSidebar"][aria-expanded="false"] > div:first-child {
        width: 28em;
        margin-left: -28em;
    }
    </style>
    """,
    unsafe_allow_html=True,
)
st.sidebar.title('Peatland analysis')

st.title('Peatland time series analysis')
uploaded_file = upload.uploader()

placeholder = st.empty()
default_button = placeholder.button(label='Or load default data')

if default_button:
    data_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'peatland_dashboard', 'data', 'default.csv')
    st.session_state['time_series'] = read_time_series(data_path)
elif uploaded_file is not None:
    st.session_state['time_series'] = upload.read_time_series_from_file(uploaded_file)

time_series = st.session_state['time_series']

if time_series is not None:
    placeholder.empty()

    with st.sidebar.expander('Hyperparameters'):
        gap = st.number_input('Gap', value=5)
        max_hour = st.number_input('Max hour', value=5)
        threshold = st.number_input('Precipitation threshold', value=0.3)
        resample = st.text_input('Resample', value='H')

    sy = calculate_sy(time_series, gap=int(gap), max_hour=int(max_hour), threshold=threshold, resample=resample)

    with st.sidebar.expander('Filters'):
        col1, col2 = st.columns(2)
        with col1:
            delta_h_min = st.number_input(label='Delta h min', value=0.01)
            sy_min = st.number_input(label='Sy value min', value=0.01)
            precipitation_sum_min = st.number_input(label='Precipitation Sum min', value=5.0)
            depth_min = st.number_input(label='Mean depth [m] min', value=-1.0)
            durations_min = st.number_input(label='Durations min', value=0.0)
            intensities_min = st.number_input(label='Intensities min', value=0.0)
            date_beginning_min = st.date_input(label='Date beginning min', value=sy['date_beginning'].min())
            date_ending_min = st.date_input(label='Date ending min', value=sy['date_ending'].min())

        with col2:
            delta_h_max = st.number_input(label='Delta h max', value=20.0)
            sy_max = st.number_input(label='Sy value max', value=1.0, step=0.1)
            precipitation_sum_max = st.number_input(label='Precipitation Sum max', value=40.0)
            depth_max = st.number_input(label='Mean depth [m] max', value=0.2)
            durations_max = st.number_input(label='Durations max', value=10.0)
            intensities_max = st.number_input(label='Intensities max', value=10.0)
            date_beginning_max = st.date_input(label='Date beginning max', value=sy['date_beginning'].max())
            date_ending_max = st.date_input(label='Date ending max', value=sy['date_ending'].max())

    sy = filter_sy(
        sy=sy,
        sy_min=sy_min,
        sy_max=sy_max,
        delta_h_min=delta_h_min,
        delta_h_max=delta_h_max,
        precipitation_sum_min=precipitation_sum_min,
        precipitation_sum_max=precipitation_sum_max,
        depth_min=depth_min,
        depth_max=depth_max,
        intensities_min=intensities_min,
        intensities_max=intensities_max,
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
        event_index = st.select_slider('Event Index', options=sy.index)
        hour_before = st.slider('Hour before', 0, 100, 10)
        hour_after = st.slider('Hour after', 0, 100, 20)

    with st.sidebar.expander('Depth'):
        # Show indexes in Depth graph
        show_indexes = st.checkbox('Show indexes in Depth plot', False)
        use_min_depth = st.checkbox('Use min depth rather than mean depth', True)
        x_lim = st.slider('Limits Sy axis', 0.0, 2.0, value=(0.01, 1.0), step=0.1)
        y_lim = st.slider('Limits Depth axis [cm]', -120, 20, value=(-100, 0), step=1)
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
            use_min_depth=use_min_depth,
            show_plot=False,
            show_indexes=show_indexes,
            x_limits=x_lim, y_limits=y_lim,
            show_legend=show_equation,
            power_law_x_axis=as_power_law_axis
        )

        st.pyplot(fig_depth)

