import io

import streamlit as st
from peatland_time_series import read_time_series


def uploader():
    return st.file_uploader(
        label='Upload peatland time series:',
        type=['csv', 'txt'],
        accept_multiple_files=False,
    )


@st.cache
def read_time_series_from_file(uploaded_file):
    bytes_data = uploaded_file.getvalue()
    file = io.BytesIO(bytes_data)

    return read_time_series(file)
