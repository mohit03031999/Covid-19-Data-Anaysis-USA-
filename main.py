#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import streamlit as st
import plotly.express as px
import json
import plotly.io as pio
from urllib.request import urlopen

Path = "./"  # Path for reading the files

new_covid_cases = pd.read_csv(Path + 'covid_confirmed_usafacts.csv')  # Reading confirmed cases file
county_population = pd.read_csv(Path + 'covid_county_population_usafacts.csv')  # Reading the countywise population file
covid_deaths = pd.read_csv(Path + 'covid_deaths_usafacts.csv')  # Reading the covid death data file

# Get counties where feature.id is the FIPS Code
with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
    counties = json.load(response)


# Question 1
# Produce a line plot of the weekly new cases of Covid-19 in the USA from the start of the
# pandemic. Weeks start on Sunday and end on Saturday. Only include full weeks.

state_cases = new_covid_cases.drop(['countyFIPS', 'StateFIPS'], axis=1)  #Drop the columns as we don't need them and store it new dataframe
state_cases = state_cases.groupby(['State'])  # Grouping up the dataframe by States
state_cases = state_cases.sum().reset_index()

weekly_cases = state_cases.loc[:, '2020-01-25'::7].diff(axis=1)  # Obtaining the total number of cases till the weekend and converting cumulative data to per week data
weekly_cases = weekly_cases.drop(['2020-01-25'], axis=1)  # Getting rid of partial week count of first weekend

question1_table = pd.merge(state_cases['State'], weekly_cases, left_index=True, right_index=True).set_index('State')  # merging the two dataframe based on State
question1_table = question1_table.transpose()  # Making it compatible to plot
question1_table = question1_table.rename_axis("Week")

question1_table['Total Cases'] = question1_table.sum(axis=1)

fig_cases = px.line(question1_table, y=question1_table['Total Cases'], title='Weekly New Cases of Covid-19 in the USA')
fig_cases.update_traces(line_color="black")
st.plotly_chart(fig_cases)


# Question 2
# Produce a line plot of the weekly deaths due to Covid-19 in the USA from the start of the
# pandemic. Weeks start on Sunday and end on Saturday. Only include full weeks.

state_death = covid_deaths.drop(['countyFIPS', 'StateFIPS', 'County Name'], axis=1)  # Drop the columns as we don't need them and store it new dataframe
state_death = state_death.groupby(['State'])  # Grouping up the dataframe by States
state_death = state_death.sum().reset_index()

weekly_death = state_death.loc[:, '2020-01-25'::7].diff(axis=1)  # Obtaining the total number of cases till the weekend and converting cumulative data to per week data
weekly_death = weekly_death.drop(['2020-01-25'], axis=1)  # Getting rid of partial week count of first weekend

question2_table = pd.merge(state_death['State'], weekly_death, left_index=True, right_index=True).set_index('State')  # merging the two dataframe based on State
question2_table = question2_table.transpose().rename_axis("Week")
question2_table['Total Cases'] = question2_table.sum(axis=1)

fig_death = px.line(question2_table, y=question2_table['Total Cases'], title='Weekly Deaths due to Covid-19 in the USA')
fig_death.update_traces(line_color="red")

st.plotly_chart(fig_death)


# Question 3,4 and 5

# Getting the countywise cases for all the dates from the datset and storing it in dataframe
county_cases = new_covid_cases.drop(['State', 'StateFIPS'], axis=1)
county_cases = county_cases.drop(county_cases[county_cases['County Name'] == "Statewide Unallocated"].index)  # Removing the rows with countyname as Statewide Unallocated
county_cases = county_cases.set_index('countyFIPS')

county_weekly_cases = county_cases.loc[:, '2020-01-25'::7].diff(axis=1)  # Obtaining the total number of cases till the weekend and converting cumulative data to per week data
county_weekly_cases = county_weekly_cases.drop(['2020-01-25'], axis=1)  # Getting rid of partial week count of first weekend

week_columns = county_weekly_cases.columns  # Getting the weeks and converting it into a list of weeks
week_col = list(week_columns)

c_population = county_population.groupby(['countyFIPS']).sum().reset_index()  # Getting the pouplation of a county
c_population = c_population.drop(c_population[c_population['countyFIPS'] == 0].index)

county_cases_merge = pd.merge(c_population, county_weekly_cases,on='countyFIPS')  # Merging the population and new cases dataframe
county_cases_merge = county_cases_merge.reset_index(drop=True)
county_cases_merge.loc[:, '2020-02-01':] = (county_cases_merge.loc[:, '2020-02-01':].mul(100000)).div(
    county_cases_merge['population'], axis=0)  # calculating new cases of covid per 100,000 population in a week

county_cases_merge.loc[:, '2020-02-01':] = county_cases_merge.loc[:, '2020-02-01':].round(2)  # Rounding the values upto 2 decimal places

county_cases_merge = county_cases_merge.drop(["population"], axis=1)
county_cases_merge['countyFIPS'] = pd.Series(county_cases_merge['countyFIPS']).astype(str).str.zfill(5)


# Function to print the weekly cases in USA
def weekly_cases_map(week):
    pio.renderers.default = "colab"

    min_value = min(county_cases_merge[week])
    max_value = max(county_cases_merge[week])

    fig = px.choropleth(county_cases_merge,  # Input Pandas DataFrame
                        locations="countyFIPS",  # DataFrame column with locations
                        geojson=counties,
                        color=week,
                        color_continuous_scale='Viridis_r',
                        range_color=(min_value, max_value)
                        )  # Set to plot as US States
    fig.update_layout(
        title_text='Covid Cases per 100,000 population in a week',  # Create a Title
        geo_scope='usa',  # Plot only the USA
    )
    return fig


#Getting the countywise deaths for all the dates from the datset and storing it in dataframe
county_deaths = covid_deaths.drop(['State', 'StateFIPS'], axis=1)
county_deaths = county_deaths.drop(county_deaths[county_deaths['County Name'] == "Statewide Unallocated"].index) # Removing the rows with countyname as Statewide Unallocated
county_deaths = county_deaths.set_index('countyFIPS')  #Setting the CountyFIPS as index

county_weekly_deaths = county_deaths.loc[:, '2020-01-25'::7].diff(axis=1)
county_weekly_deaths = county_weekly_deaths.drop(['2020-01-25'], axis=1)

county_deaths_merge = pd.merge(c_population, county_weekly_deaths, on='countyFIPS') # Merging the population and weekly deaths dataframe
county_deaths_merge = county_deaths_merge.reset_index(drop=True)
county_deaths_merge.loc[:, '2020-02-01':] = (county_deaths_merge.loc[:, '2020-02-01':].mul(100000)).div(
    county_deaths_merge['population'], axis=0) # calculating new deaths of covid per 100,000 population in a week
county_deaths_merge.loc[:, '2020-02-01':] = county_deaths_merge.loc[:, '2020-02-01':].round(2)

county_deaths_merge = county_deaths_merge.drop(["population"], axis=1)
county_deaths_merge['countyFIPS'] = pd.Series(county_deaths_merge['countyFIPS']).astype(str).str.zfill(5)


# Function to print the weekly deaths in USA
def weekly_deaths_map(week):
    pio.renderers.default = "colab"
    min_range = min(county_deaths_merge[week])
    max_range = max(county_deaths_merge[week])

    fig1 = px.choropleth(county_deaths_merge,  # Input Pandas DataFrame
                         locations="countyFIPS",  # DataFrame column with locations
                         geojson=counties,
                         color=week,
                         color_continuous_scale='Viridis_r',
                         range_color=(min_range, max_range)
                         )  # Set to plot as US States
    fig1.update_layout(
        title_text='Covid deaths per 100,000 population in a week',  # Create a Title
        geo_scope='usa',  # Plot only the USA
    )
    return fig1


# Function to get input from user for week as a slider and plotting corresponding graph in streamlit
def input_week():
    st.header('Weekly New Cases and Deaths in each County')
    week = st.select_slider(label='Select the week to be plotted',  #Slider to get the user input
                            options=week_col,
                            value=week_col[0])

    fig1 = weekly_cases_map(week)
    st.plotly_chart(fig1,use_container_width=True)

    fig2 = weekly_deaths_map(week)
    st.plotly_chart(fig2,use_container_width=True)

input_week()

button = st.button("Auto Play")  #Button to auto play the maps

#Function to plot the map for all the weeks

def auto_play():
    if button:  #If the button is pressed then plot the maps
        spot1 = st.empty()
        spot2 = st.empty()
        for week_input in week_col:
            fig1 = weekly_cases_map(week_input)
            fig2 = weekly_deaths_map(week_input)
            # Sleep for a bit before displaying the next map
            with spot1:
                st.plotly_chart(fig1, use_container_width=True)
            with spot2:
                st.plotly_chart(fig2, use_container_width=True)

auto_play()
