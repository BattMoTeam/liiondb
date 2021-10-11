import streamlit as st
import psycopg2
import inspect
import sys
import os
import importlib
import functions.fn_db as fn_db
import functions.fn_plot as fn_plot
import pandas as pd
import numpy as np
import webbrowser
import markdown
import base64
import streamlit_gui.elements.query_box
import streamlit_gui.elements.choose_advanced
import streamlit_gui.elements.single_parameter
import streamlit_gui.elements.multiparameter_comparison
import streamlit_gui.elements.example_advanced_queries
# DASHBOARD PAGE ====================
def write():
    session_state = st.session_state
    if 'df_display' not in st.session_state:
        st.session_state.df_display = []
    if 'df_result' not in st.session_state:
        st.session_state.df_result = []
    if 'dispdf' not in st.session_state:
        st.session_state.dispdf = []
    if 'count' not in st.session_state:
        st.session_state.count = 0
    if 'count_array' not in st.session_state:
        st.session_state.count_array = [0]
    # append_current_count()
    st.title(":rocket: Advanced Queries")
    st.write("---")
    df_result,session_state = streamlit_gui.elements.query_box.write(st.session_state)
    st.session_state = session_state
    # st.write(type(df_result))
    st.write("---")

    if 'data_id' in df_result:
        st.markdown('<h5>Select data_id to display:</h5>', unsafe_allow_html=True)
        selections, submit_button, session_state = streamlit_gui.elements.choose_advanced.write(df_result,st.session_state)
        st.session_state = session_state

        if len(selections)==1: #only a single parameter chosen to display
            if submit_button:
                append_current_count()
                streamlit_gui.elements.single_parameter.write(selections,st.session_state)
            elif check_refresh()==False:
                try:
                    streamlit_gui.elements.single_parameter.write(selections,st.session_state)
                except UnboundLocalError: #no selection yet
                    st.session_state
        elif len(selections)>1:
            streamlit_gui.elements.multiparameter_comparison.write(selections,session_state)
    # except TypeError:
    #     st.caption('No options in results table')
    #     submit_button = False

#
def append_current_count():
    st.session_state.count_array.append(st.session_state.count)

def check_refresh():
    refresh = False
    if len(st.session_state.count_array)>1:
        if st.session_state.count_array[-2]!=st.session_state.count_array[-1]:
            refresh = True
    return refresh
