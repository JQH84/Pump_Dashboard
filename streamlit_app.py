# create a sttreamlit app that will visualize ESP data from multiple files in a folder and display it in a dashboard

import streamlit as st
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
import plotly.io as pio
from plotly.subplots import make_subplots
# set page config to wide
st.set_page_config(layout="wide")


# set the title of the dashboard
st.title("Pump Operating Dashboard")

# set the subtitle of the dashboard
st.markdown("This dashboard will visualize various types of data that has been generated from a machine learning model predicting pump failures")

# add png image to the sidebar and make it align to the center

st.sidebar.image("DP_BlueLogo.png", width=150 ) 
# add a note that there is work in progress to implement a machine learning model to predict pump failures 
st.sidebar.markdown("<p style='font-style: italic; color: gray;'>Work in progress to implement a machine learning model to predict pump failures</p>", unsafe_allow_html=True)
st.sidebar.markdown("[Digital Petroleum Website](http://www.digitalpetroleum.com)")
# set the sidebar
# set the theme for the dashboard
theme = st.sidebar.selectbox("Select a theme", pio.templates.keys() , )
pio.templates.default = theme
st.sidebar.title("Menu Options")


# set the file upload
uploaded_file = st.sidebar.file_uploader("Upload your input CSV file", type=["csv"] , key='1')

#create button that when pressed will run an ML prediction function on the uploaded file and return the predictions as a dataframe




# read the file and then create a custom visualization that allows the user to chose which WELL_ID to plot against time from a drop down menu 

if uploaded_file  is not None:
    # create a dropdown menu based on the well names  in the file that have the column name WELL_ID
    
    df = pd.read_csv(uploaded_file , index_col='DATE', parse_dates=True , low_memory=False)
    df.index = pd.to_datetime(df.index)
    # calculate the power consumption of the pump 
    df["Power"] = df["OUT_VOLT"].mean() * df["CURRENT"].mean() * 0.7 
    wells = df["WELL_ID"].unique().tolist()
    columns = df.columns.tolist()
    columns.insert(0, "Select a column")
    selected_well = st.sidebar.selectbox("Select a well", wells)
    # create a multi select box that allows the user to select multiple columns to plot against time
    selected_column = st.sidebar.multiselect("Select columns", columns ,default=["FREQUENCY", "VIBRATION", "CURRENT"])
    #selected_column = st.sidebar.selectbox("Select a column", columns)  
    
    # based on the slected well, plot the data against time ( which is the index of the dataframe)
    if selected_column != "Select a column" and selected_well is not None:
        df_well = df.loc[df['WELL_ID'] == selected_well]
        # create 3 graphs side by side in a 1X3 layout that show min avg and max values of the selected column
        col1 , col2 , col3 = st.columns(spec=3)
        
        with col1:
            fig = go.Figure(go.Indicator(   mode = "gauge+number",      
                            value = df_well[selected_column[0]].min(),
                            domain = {'x': [0, 1], 'y': [0, 1]},
                            title = {'text': f"Minimum {selected_column[0]}"},
                            gauge = {'axis': {'range': [None, 100]},
                                'bar': {'color': "green"},
                                'steps' :  [ {'range': [0, 50], 'color': "lightblue"},   {'range': [50, 100], 'color': "blue"}],
                                'threshold' : {'line': {'color': "green", 'width': 5}, 'thickness': 1, 'value': df_well[selected_column[0]].min()}}))
            fig.update_layout(width=300 , height=300)
            st.plotly_chart(fig)
                
        with col2:
            fig = go.Figure(go.Indicator(   mode = "gauge+number",      
                                            value = df_well[selected_column[0]].mean(),
                                            domain = {'x': [0, 1], 'y': [0, 1]},
                                            title = {'text': f"Average {selected_column[0]}"},
                                            gauge = {'axis': {'range': [None, 100]},
                                                    'bar': {'color': "green"},
                                                    'steps' : [ {'range': [0, 50], 'color': "lightblue"},   {'range': [50, 100], 'color': "blue"}],
                                                    'threshold' : {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': df_well[selected_column[0]].mean()}}))
            fig.update_layout(width=300 , height=300)
            st.plotly_chart(fig)
                
        with col3:
            fig = go.Figure(go.Indicator(   mode = "gauge+number",      
                                            value = df_well[selected_column[0]].max(),
                                            domain = {'x': [0, 1], 'y': [0, 1]},
                                            title = {'text': f"Maximum {selected_column[0]}"},
                                            gauge = {'axis': {'range': [None, 100]},
                                                    'bar': {'color': "green"},
                                                    'steps' : [ {'range': [0, 50], 'color': "lightblue"},   {'range': [50, 100], 'color': "blue"}],
                                                    'threshold' : {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': df_well[selected_column[0]].max()}}))
            fig.update_layout(width=300 , height=300)
            st.plotly_chart(fig)
        # create a multi compnent dashboard that will display a scatter plot, a line plot and a bar chart and a geographical map in  4X4 layout 
        
        # create a geographical map that displays the location of the ESPs pumps
        st.header("ESP Locations")
        st.markdown("### This map displays the location of the ESPs pumps")
        
        # Create the dataset to plot faluires on a map
        grouped_data = df.groupby(["WELL_ID" , "lat" ,'lon']).count()[["WellFailure", "FAILURE"]].reset_index()
        grouped_data['well_status'] = np.where(grouped_data['WellFailure'] == 1, 'Failure Event', np.where(grouped_data['WellFailure'] == 2, 'Manual Shutoff', 'No Failure Event'))

        fig = px.scatter_mapbox(grouped_data, 
                                lat="lat",
                                lon="lon",
                                color='well_status', 
                                color_discrete_sequence=["red" , "yellow" , "green"],
                                size='FAILURE',
                                hover_name="WELL_ID",
                                hover_data=["WELL_ID", "lat", "lon"],
                                zoom=8)
        fig.update_layout(mapbox_style='open-street-map')
        fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        fig.update_layout(width=1500 , height=500)
        fig.update_layout(title='ESP Locations')
        st.plotly_chart(fig)
        
        # well failure events 
        st.header("Well Failure Events")
        well_failure_events = df.groupby('WELL_ID')['WellFailure'].sum().reset_index()
        st.dataframe(well_failure_events , width=1000 , height=200)
        
        # create a scatter plot that displays the relationship between the ESPs pumps
        
        st.header('Time Series Plots') 
        plot1 , plot2 , plot3  = st.columns(3)
        with plot1:
            fig = px.histogram(df_well, x=selected_column[0])
            fig.update_layout(width=400 , height=400 , title=f"{selected_column[0]}")
            st.plotly_chart(fig, style={'border': '3px solid #fff'})
        with plot2:
            # create a bar chart that displays the ESPs pumps
            fig = px.bar(df_well, x=selected_column[0], y=selected_column[1], color_discrete_sequence=['rgb(80,82,249)'] )
            fig.update_layout(width=400 , height=400, bargap=0.1, bargroupgap=0.1, uniformtext_minsize=8, uniformtext_mode='hide')
            fig.update_traces(marker=dict(line=dict(width=1, color='DarkSlateGrey')), opacity=0.8, width=0.5)
            st.plotly_chart(fig)
        
        
        with plot3:
            # create a line plot that displays the ESPs pumps
            fig = px.line(df_well, x=df_well.index, y=selected_column[0])
            fig.update_layout(width=400 , height=400)
            st.plotly_chart(fig)
            
        
       
    

        # Create a Streamlit dropdown to select the well ID
        well_ids = df['WELL_ID'].unique()
        selected_well_id = st.selectbox('Select Well ID', well_ids)
        # Filter the data based on the selected well ID
        filtered_data = df[df['WELL_ID'] == selected_well_id]
        
        
        # Create subplots using Plotly
        fig = make_subplots(rows=2, cols=2, subplot_titles=('Current', 'Pressure Intake', 'Vibration', 'Fluid Production'))
        # Add traces for each subplot
        fig.add_trace(go.Scatter(x=filtered_data.index, y=filtered_data['CURRENT'], name='Current'), row=1, col=1)
        fig.add_trace(go.Scatter(x=filtered_data.index, y=filtered_data['PRESS_INT'], name='Pressure Intake'), row=1, col=2)
        fig.add_trace(go.Scatter(x=filtered_data.index, y=filtered_data['VIBRATION'], name='Vibration'), row=2, col=1)
        fig.add_trace(go.Scatter(x=filtered_data.index, y=filtered_data['BFPD'], name='BFPD'), row=2, col=2)
        fig.add_trace(go.Scatter(x=filtered_data.index, y=filtered_data['BOPD'], name='BOPD'), row=2, col=2)
        fig.add_trace(go.Scatter(x=filtered_data.index, y=filtered_data['BWPD'], name='BWPD'), row=2, col=2)
        # Update layout
        fig.update_layout(height=600, width=1500, title={
            'text': f'Performance Metrics for Well ID {selected_well_id}',
            'font': {'size': 30},
            'x': 0.5,
            'y': 0.95,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        xaxis=dict(title='Date'), yaxis=dict(title='Metric Value'))
        # Display the subplot figure
        st.plotly_chart(fig)
        
        

    else:
        st.write("Please select a column to plot against time")
else:
    st.write("Please upload a file to plot against time or click the Demo button below to load an existing file")
    demo_button = st.button('Demo')
    df = None
    if df is None:
            st.write('have a look at how ML model can be used to predict the failure') 
            st.video('https://www.youtube.com/watch?v=9JpdAg6uMXs')
    if demo_button:
            df = pd.read_csv('data.csv' , index_col='DATE', parse_dates=True , low_memory=False)
            df.index = pd.to_datetime(df.index)
        # calculate the power consumption of the pump 
            df["Power"] = df["OUT_VOLT"].mean() * df["CURRENT"].mean() * 0.7 
            wells = df["WELL_ID"].unique().tolist()
            columns = df.columns.tolist()
            columns.insert(0, "Select a column")
            selected_well = st.sidebar.selectbox("Select a well", wells)
            # create a multi select box that allows the user to select multiple columns to plot against time
            selected_column = st.sidebar.multiselect("Select columns", columns ,default=["FREQUENCY", "VIBRATION", "CURRENT"])
            #selected_column = st.sidebar.selectbox("Select a column", columns)  
    
            # based on the slected well, plot the data against time ( which is the index of the dataframe)
            if selected_column != "Select a column" and selected_well is not None:
                df_well = df.loc[df['WELL_ID'] == selected_well]
                # create 3 graphs side by side in a 1X3 layout that show min avg and max values of the selected column
                col1 , col2 , col3 = st.columns(spec=3)
    
                with col1:
                    fig = go.Figure(go.Indicator(   mode = "gauge+number",      
                                    value = df_well[selected_column[0]].min(),
                                    domain = {'x': [0, 1], 'y': [0, 1]},
                                    title = {'text': f"Minimum {selected_column[0]}"},
                                    gauge = {'axis': {'range': [None, 100]},
                                        'bar': {'color': "green"},
                                        'steps' :  [ {'range': [0, 50], 'color': "lightblue"},   {'range': [50, 100], 'color': "blue"}],
                                        'threshold' : {'line': {'color': "green", 'width': 5}, 'thickness': 1, 'value': df_well[selected_column[0]].min()}}))
                    fig.update_layout(width=300 , height=300)
                    st.plotly_chart(fig)
    
                with col2:
                    fig = go.Figure(go.Indicator(   mode = "gauge+number",      
                                                    value = df_well[selected_column[0]].mean(),
                                                    domain = {'x': [0, 1], 'y': [0, 1]},
                                                    title = {'text': f"Average {selected_column[0]}"},
                                                    gauge = {'axis': {'range': [None, 100]},
                                                            'bar': {'color': "green"},
                                                            'steps' : [ {'range': [0, 50], 'color': "lightblue"},   {'range': [50, 100], 'color': "blue"}],
                                                            'threshold' : {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': df_well[selected_column[0]].mean()}}))
                    fig.update_layout(width=300 , height=300)
                    st.plotly_chart(fig)
    
                with col3:
                    fig = go.Figure(go.Indicator(   mode = "gauge+number",      
                                                    value = df_well[selected_column[0]].max(),
                                                    domain = {'x': [0, 1], 'y': [0, 1]},
                                                    title = {'text': f"Maximum {selected_column[0]}"},
                                                    gauge = {'axis': {'range': [None, 100]},
                                                            'bar': {'color': "green"},
                                                            'steps' : [ {'range': [0, 50], 'color': "lightblue"},   {'range': [50, 100], 'color': "blue"}],
                                                            'threshold' : {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': df_well[selected_column[0]].max()}}))
                    fig.update_layout(width=300 , height=300)
                    st.plotly_chart(fig)
                # create a multi compnent dashboard that will display a scatter plot, a line plot and a bar chart and a geographical map in  4X4 layout 
    
                # create a geographical map that displays the location of the ESPs pumps
                st.header("ESP Locations")
                st.markdown("### This map displays the location of the ESPs pumps")
    
                # Create the dataset to plot faluires on a map
                grouped_data = df.groupby(["WELL_ID" , "lat" ,'lon']).count()[["WellFailure", "FAILURE"]].reset_index()
                grouped_data['well_status'] = np.where(grouped_data['WellFailure'] == 1, 'Failure Event', np.where(grouped_data['WellFailure'] == 2, 'Manual Shutoff', 'No Failure Event'))
    
                fig = px.scatter_mapbox(grouped_data, 
                                        lat="lat",
                                        lon="lon",
                                        color='well_status', 
                                        color_discrete_sequence=["red" , "yellow" , "green"],
                                        size='FAILURE',
                                        hover_name="WELL_ID",
                                        hover_data=["WELL_ID", "lat", "lon"],
                                        zoom=8)
                fig.update_layout(mapbox_style='open-street-map')
                fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
                fig.update_layout(width=1500 , height=500)
                fig.update_layout(title='ESP Locations')
                st.plotly_chart(fig)
    
                # well failure events 
                st.header("Well Failure Events")
                well_failure_events = df.groupby('WELL_ID')['WellFailure'].sum().reset_index()
                st.dataframe(well_failure_events , width=1000 , height=200)
    
                # create a scatter plot that displays the relationship between the ESPs pumps
    
                st.header('Time Series Plots') 
                plot1 , plot2 , plot3  = st.columns(3)
                with plot1:
                    fig = px.histogram(df_well, x=selected_column[0])
                    fig.update_layout(width=400 , height=400 , title=f"{selected_column[0]}")
                    st.plotly_chart(fig, style={'border': '3px solid #fff'})
                with plot2:
                    # create a bar chart that displays the ESPs pumps
                    fig = px.bar(df_well, x=selected_column[0], y=selected_column[1], color_discrete_sequence=['rgb(80,82,249)'] )
                    fig.update_layout(width=400 , height=400, bargap=0.1, bargroupgap=0.1, uniformtext_minsize=8, uniformtext_mode='hide')
                    fig.update_traces(marker=dict(line=dict(width=1, color='DarkSlateGrey')), opacity=0.8, width=0.5)
                    st.plotly_chart(fig)
    
    
                with plot3:
                    # create a line plot that displays the ESPs pumps
                    fig = px.line(df_well, x=df_well.index, y=selected_column[0])
                    fig.update_layout(width=400 , height=400)
                    st.plotly_chart(fig)
    
    
    
    
    
                # Create a Streamlit dropdown to select the well ID
                well_ids = df['WELL_ID'].unique()
                selected_well_id = st.selectbox('Select Well ID', well_ids)
                # Filter the data based on the selected well ID
                filtered_data = df[df['WELL_ID'] == selected_well_id]
    
    
                # Create subplots using Plotly
                fig = make_subplots(rows=2, cols=2, subplot_titles=('Current', 'Pressure Intake', 'Vibration', 'Fluid Production'))
                # Add traces for each subplot
                fig.add_trace(go.Scatter(x=filtered_data.index, y=filtered_data['CURRENT'], name='Current'), row=1, col=1)
                fig.add_trace(go.Scatter(x=filtered_data.index, y=filtered_data['PRESS_INT'], name='Pressure Intake'), row=1, col=2)
                fig.add_trace(go.Scatter(x=filtered_data.index, y=filtered_data['VIBRATION'], name='Vibration'), row=2, col=1)
                fig.add_trace(go.Scatter(x=filtered_data.index, y=filtered_data['BFPD'], name='BFPD'), row=2, col=2)
                fig.add_trace(go.Scatter(x=filtered_data.index, y=filtered_data['BOPD'], name='BOPD'), row=2, col=2)
                fig.add_trace(go.Scatter(x=filtered_data.index, y=filtered_data['BWPD'], name='BWPD'), row=2, col=2)
                # Update layout
                fig.update_layout(height=600, width=1500, title={
                    'text': f'Performance Metrics for Well ID {selected_well_id}',
                    'font': {'size': 30},
                    'x': 0.5,
                    'y': 0.95,
                    'xanchor': 'center',
                    'yanchor': 'top'
                },
                xaxis=dict(title='Date'), yaxis=dict(title='Metric Value'))
                # Display the subplot figure
                st.plotly_chart(fig)
    
