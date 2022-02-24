import pandas
import streamlit as st
from peatland_time_series import calculate_sy, filter_sy, visualization

from peatland_dashboard import download, upload
from peatland_dashboard.util import round_values

st.set_page_config(layout='wide')
st.sidebar.title('Peatland analysis')

st.title('Peatland time series analysis')
uploaded_file = upload.uploader()

if uploaded_file is not None:
    time_series = upload.read_time_series_from_file(uploaded_file)

    with st.sidebar.expander('Hyperparameters'):
        gap = st.number_input('Gap', value=5)
        max_hour = st.number_input('Max hour', value=5)
        threshold = st.number_input('Precipitation threshold', value=0.3)
        resample = st.text_input('Resample', value='H')

    sy = calculate_sy(time_series, gap=int(gap), max_hour=int(max_hour), threshold=threshold, resample=resample)

    with st.sidebar.expander('Filters'):
        delta_h = st.select_slider(
            label='Delta h',
            options=round_values(sy['delta_h'].dropna().sort_values()),
            value=(round_values(sy['delta_h'].min()), round_values(sy['delta_h'].max()))
        )
        sy_min_max = st.select_slider(
            label='Sy value',
            options=round_values(sy['sy'].dropna().sort_values()),
            value=(round_values(sy['sy'].min()), round_values(sy['sy'].max()))
        )
        precipitation_sum = st.select_slider(
            label='Precipitation Sum',
            options=round_values(sy['precipitation_sum'].dropna().sort_values()),
            value=(5, 40)
        )
        depth = st.select_slider(
            label='Mean depth [m]',
            options=round_values(sy['depth'].dropna().sort_values()),
            value=(round_values(sy['depth'].min()), round_values(sy['depth'].max()))
        )
        durations = st.select_slider(
            label='Durations',
            options=round_values(sy['durations'].dropna().sort_values()),
            value=(round_values(sy['durations'].min()), round_values(sy['durations'].max()))
        )
        intensities = st.select_slider(
            label='Intensities',
            options=round_values(sy['intensities'].dropna().sort_values()),
            value=(round_values(sy['intensities'].min()), round_values(sy['intensities'].max()))
        )
        date_beginning = st.select_slider('Date beginning', options=sy['date_beginning'].sort_values(), value=(sy['date_beginning'].min(), sy['date_beginning'].max()))
        date_ending = st.select_slider('Date ending', options=sy['date_ending'].sort_values(), value=(sy['date_ending'].min(), sy['date_ending'].max()))

    sy = filter_sy(
        sy=sy,
        sy_min=sy_min_max[0],
        sy_max=sy_min_max[1],
        delta_h_min=delta_h[0],
        delta_h_max=delta_h[1],
        precipitation_sum_min=precipitation_sum[0],
        precipitation_sum_max=precipitation_sum[1],
        depth_min=depth[0],
        depth_max=depth[1],
        intensities_min=intensities[0],
        intensities_max=intensities[1],
        date_beginning_min=pandas.Timestamp(date_beginning[0]),
        date_beginning_max=pandas.Timestamp(date_beginning[1]),
        date_ending_min=pandas.Timestamp(date_ending[0]),
        date_ending_max=pandas.Timestamp(date_ending[1]),
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
        x_lim = st.slider('Limits Sy axis', 0.0, 2.0, value=(0.1, 1.0), step=0.1)
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
