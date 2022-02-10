import io

import pandas
import streamlit as st


def make_download_button(sy: pandas.DataFrame):
    sy_bytes = io.BytesIO()
    sy.to_csv(sy_bytes, index=False)
    sy_bytes.seek(0)

    st.download_button('Download the Sy Dataframe as a CSV', sy_bytes, file_name='sy.csv', mime='text/csv')
