from flask import Flask, jsonify, render_template, request
import altair as alt
import pandas as pd
import numpy as np
import datetime
from pytz import timezone
from scipy import stats



#####################
## Data Processing ##
#####################
def process_data(variable, aggregation_level, start_date=None, end_date=None):

    data = pd.read_csv('data/MorroBayHeights.csv')
    data['datetime'] = pd.to_datetime(data['datetime'], unit='s')
    
    # Filter data if start_date and end_date are provided
    if start_date and end_date:
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)
        data = data[(data['datetime'] >= start_date) & (data['datetime'] <= end_date)]
    
    # Define get_season function somewhere in your code
    def get_season(month):
        if month in [12, 1, 2]:
            return 'Winter'
        elif month in [3, 4, 5]:
            return 'Spring'
        elif month in [6, 7, 8]:
            return 'Summer'
        elif month in [9, 10, 11]:
            return 'Fall'
    
    # Aggregation logic
    if aggregation_level == 'Hour':
        data['time_period'] = data['datetime'].dt.to_period('H')
    elif aggregation_level == 'Day':
        data['time_period'] = data['datetime'].dt.to_period('D')
    elif aggregation_level == 'Week':
        data['time_period'] = data['datetime'].dt.to_period('W').apply(lambda r: r.start_time)
    elif aggregation_level == 'Month':
        data['time_period'] = data['datetime'].dt.to_period('M')
    elif aggregation_level == 'Season':
        data['time_period'] = data['datetime'].dt.month.apply(get_season)
    elif aggregation_level == 'Season_Year':
        data['year'] = data['datetime'].dt.year
        data['season'] = data['datetime'].dt.month.apply(get_season)
        data['time_period'] = data['season'] + '-' + data['year'].astype(str)
    elif aggregation_level == 'Year':
        data['time_period'] = data['datetime'].dt.year


    # Init Dict
    agg_dict = {
        'lotusMinBWH_ft': 'mean',
        'lotusMaxBWH_ft': 'mean',
        'lotusSigh_mt' : 'mean',
    }

    if 'Part' in variable:
        partition_variables = [variable.replace("X",f"{i}") for i in range(6)]

        for var in partition_variables:
            if var in data.columns:
                agg_dict[var] = 'mean'
    else:
        if variable in data.columns:
            agg_dict[variable] = 'mean'
    
    aggregated_data = data.groupby('time_period').agg(agg_dict).reset_index()
    aggregated_data['time_period'] = aggregated_data['time_period'].astype(str)
    
    return aggregated_data

####################
## Generate Chart ##
####################
def get_x_axis_type(aggregation_level):
    if aggregation_level in ['Day', 'Week', 'Month', 'Year']:
        return 'temporal'
    else:
        return 'nominal'
    
def generate_line_chart(aggregated_data, variable, aggregation_level):
    # Base chart configuration
    base = alt.Chart(aggregated_data).encode(
        x=alt.X('time_period', type=get_x_axis_type(aggregation_level), title='Time Period'),
    )
    
    if "Part" not in variable:
        base = base.properties(width=900, height=600)
        # Standard line chart for non-partitioned data
        chart = base.mark_line().encode(
            y=alt.Y(f'{variable}:Q', title='Value'),
            tooltip=[alt.Tooltip('time_period:N', title='Time Period'), alt.Tooltip(f'{variable}:Q', title='Value')]
        )
    else:
        base = base.properties(width=300, height=200)

        global_min = aggregated_data[[variable.replace("X", str(i)) for i in range(6)]].min().min()
        global_max = aggregated_data[[variable.replace("X", str(i)) for i in range(6)]].max().max()

        # Handling partitioned variables, assuming variable format "PartX" where X is the partition number
        partition_charts = []
        for i in range(6):  # For partitions 0-5
            partition_variable = variable.replace("X",f"{i}")
            partition_chart = base.mark_line().encode(
                y=alt.Y(f'{partition_variable}:Q', scale=alt.Scale(domain=[global_min, global_max]), title=f'Value (Partition {i})'),
                tooltip=[alt.Tooltip('time_period:N', title='Time Period'), alt.Tooltip(f'{partition_variable}:Q', title=f'Value (Partition {i})')]
            )
            partition_charts.append(partition_chart)
                
        # Assuming we always have 6 charts ready to be displayed
        top_row = alt.hconcat(*partition_charts[:3])  # First 3 charts
        bottom_row = alt.hconcat(*partition_charts[3:])  # Last 3 charts

        chart = alt.vconcat(top_row, bottom_row).resolve_scale(
            x='shared',
            y='shared'
        )
        
    return chart

def generate_bar_chart(aggregated_data, variable, aggregation_level):
    # Base chart configuration
    base = alt.Chart(aggregated_data).encode(
        x=alt.X('time_period', type=get_x_axis_type(aggregation_level), title='Time Period'),
    )
    
    if "Part" not in variable:
        base = base.properties(width=900, height=600)
        # Standard bar chart for non-partitioned data
        chart = base.mark_bar().encode(
            y=alt.Y(f'{variable}:Q', title='Value'),
            tooltip=[alt.Tooltip('time_period:N', title='Time Period'), alt.Tooltip(f'{variable}:Q', title='Value')]
        )
    else:
        base = base.properties(width=300, height=200)

        global_min = aggregated_data[[variable.replace("X", str(i)) for i in range(6)]].min().min()
        global_max = aggregated_data[[variable.replace("X", str(i)) for i in range(6)]].max().max()

        # Handling partitioned variables, assuming variable format "PartX" where X is the partition number
        partition_charts = []
        for i in range(6):  # For partitions 0-5
            partition_variable = variable.replace("X",f"{i}")
            partition_chart = base.mark_bar().encode(
                y=alt.Y(f'{partition_variable}:Q', scale=alt.Scale(domain=[global_min, global_max]), title=f'Value (Partition {i})'),
                tooltip=[alt.Tooltip('time_period:N', title='Time Period'), alt.Tooltip(f'{partition_variable}:Q', title=f'Value (Partition {i})')]
            )
            partition_charts.append(partition_chart)
                
        # Assuming we always have 6 charts ready to be displayed
        top_row = alt.hconcat(*partition_charts[:3])  # First 3 charts
        bottom_row = alt.hconcat(*partition_charts[3:])  # Last 3 charts

        chart = alt.vconcat(top_row, bottom_row).resolve_scale(
            x='shared',
            y='shared'
        )
        
    return chart


def generate_composite_line_chart(aggregated_data, user_variable, aggregation_level):
    base = alt.Chart(aggregated_data).encode(
        x=alt.X('time_period', type=get_x_axis_type(aggregation_level), title='Time Period')
    )
    
    # Min and Max BWH Charts (always included)
    min_bwh = base.mark_line(color='blue').encode(y=alt.Y('lotusMinBWH_ft:Q', title='Breaking Wave Height (ft)'),
        tooltip=[alt.Tooltip('time_period:N', title='Time Period'), alt.Tooltip('lotusMinBWH_ft:Q', title='Min Breaking Wave Height')]
    )
    max_bwh = base.mark_line(color='red').encode(y=alt.Y('lotusMaxBWH_ft:Q', title='Max Breaking Wave Height (ft)'),
        tooltip=[alt.Tooltip('lotusMaxBWH_ft:Q', title='Max Breaking Wave Height')]
    )
    
    if "Part" not in user_variable:
        base = base.properties(width=900, height=600)
        # User Variable Chart (non-partitioned)
        user_var_chart = base.mark_line(color='green').encode(
            y=alt.Y(f'{user_variable}:Q', title=f'{user_variable}'),
            tooltip=[alt.Tooltip(f'{user_variable}:Q', title=f'{user_variable}')]
        )
        chart = alt.layer(min_bwh, max_bwh, user_var_chart).resolve_scale(
            y='shared'
        ).properties(width=900, height=600)
    else:
        base = base.properties(width=300, height=200)

        charts = []
        for i in range(6):
            partition_variable = f'{user_variable.replace("X", str(i))}'
            partition_chart = base.mark_line().encode(
                y=alt.Y(f'{partition_variable}:Q', title=f'Value (Partition {i})'),
                tooltip=[alt.Tooltip('time_period:N', title='Time Period'), alt.Tooltip(f'{partition_variable}:Q', title=f'Value (Partition {i})')]
            )
            chart = alt.layer(min_bwh, max_bwh, partition_chart)
            charts.append(chart)
        
        top_row = alt.hconcat(*charts[:3])  
        bottom_row = alt.hconcat(*charts[3:])

        chart = alt.vconcat(top_row, bottom_row).resolve_scale(
            x='shared',
            y='shared'
        )
    
    return chart


def generate_composite_bar_chart(aggregated_data, user_variable, aggregation_level):
    base = alt.Chart(aggregated_data).encode(
        x=alt.X('time_period', type=get_x_axis_type(aggregation_level), title='Time Period')
    )
    
    # Min and Max BWH Charts (always included)
    min_bwh = base.mark_bar(color='blue').encode(y=alt.Y('lotusMinBWH_ft:Q', title='Breaking Wave Height (ft)'),
        tooltip=[alt.Tooltip('time_period:N', title='Time Period'), alt.Tooltip('lotusMinBWH_ft:Q', title='Min Breaking Wave Height')]
    )
    max_bwh = base.mark_bar(color='red').encode(y=alt.Y('lotusMaxBWH_ft:Q', title='Max Breaking Wave Height (ft)'),
        tooltip=[alt.Tooltip('lotusMaxBWH_ft:Q', title='Max Breaking Wave Height')]
    )
    
    if "Part" not in user_variable:
        base = base.properties(width=900, height=600)
        # User Variable Chart (non-partitioned)
        user_var_chart = base.mark_bar(color='green').encode(
            y=alt.Y(f'{user_variable}:Q', title=f'{user_variable}'),
            tooltip=[alt.Tooltip(f'{user_variable}:Q', title=f'{user_variable}')]
        )
        chart = alt.layer(min_bwh, max_bwh, user_var_chart).resolve_scale(
            y='shared'
        ).properties(width=900, height=600)
    else:
        base = base.properties(width=300, height=200)

        charts = []
        for i in range(6):
            partition_variable = f'{user_variable.replace("X", str(i))}'
            partition_chart = base.mark_bar().encode(
                y=alt.Y(f'{partition_variable}:Q', title=f'Value (Partition {i})'),
                tooltip=[alt.Tooltip('time_period:N', title='Time Period'), alt.Tooltip(f'{partition_variable}:Q', title=f'Value (Partition {i})')]
            )
            chart = alt.layer(min_bwh, max_bwh, partition_chart)
            charts.append(chart)
        
        top_row = alt.hconcat(*charts[:3])  
        bottom_row = alt.hconcat(*charts[3:])

        chart = alt.vconcat(top_row, bottom_row).resolve_scale(
            x='shared',
            y='shared'
        )
    
    return chart

def generate_seasonal_chart():
    variable = 'lotusMaxBWH_ft'
    aggregation = 'Season_Year'
    start_date = request.args.get('startDate', None)
    end_date = request.args.get('endDate', None)

    # Process the data
    aggregated_data = process_data(variable, aggregation, start_date, end_date)

    season_order = {'Winter': 0,'Spring': 1,'Summer': 2,'Fall': 3}

    aggregated_data['season'] = aggregated_data['time_period'].str.extract(r'(Winter|Spring|Summer|Fall)')
    aggregated_data['year'] = aggregated_data['time_period'].str.extract(r'(\d{4})').astype(int)
    
    aggregated_data['season_order'] = aggregated_data['season'].map(season_order)
    aggregated_data.sort_values(by=['year', 'season_order'], inplace=True)

    # Create the chart
    chart = alt.Chart(aggregated_data).mark_bar().encode(
        x=alt.X('time_period:N', title='Time Period', sort=list(aggregated_data['time_period'])),
        y=alt.Y(f'{variable}:Q', title='Value'),
        color=alt.Color('season:N', sort=list(season_order), legend=alt.Legend(title="Season")),
        tooltip=[alt.Tooltip('time_period:N', title='Time Period'), alt.Tooltip(f'{variable}:Q', title='Value')]
    ).properties(
        width=900,
        height=600
    )
    
    return chart

def generate_tide_influence_chart():
    variable = 'tide_ft'
    aggregation = 'Week'
    start_date = request.args.get('startDate', None)
    end_date = request.args.get('endDate', None)

    # Process the data
    aggregated_data = process_data(variable, aggregation, start_date, end_date)

    base = alt.Chart(aggregated_data).encode(
        alt.X('time_period:T', axis=alt.Axis(title='Time'))
    )
    
    tide_line = base.mark_line(color='blue').encode(
        alt.Y('tide_ft:Q', axis=alt.Axis(title='Tide Level (ft)'))
    )
    
    wave_line = base.mark_line(color='red').encode(
        alt.Y('lotusMaxBWH_ft:Q', axis=alt.Axis(title='Max Breaking Wave Height (ft)'))
    )
    
    final_chart = alt.layer(tide_line, wave_line).resolve_scale(
        y='independent'
    ).properties(
        width=900,
        height=600
    )

    return final_chart

def generate_swell_direction_chart():
    variable = 'lotusPDirPartX_deg'
    aggregation = 'Week'
    start_date = request.args.get('startDate', None)
    end_date = request.args.get('endDate', None)

    # Process the data
    aggregated_data = process_data(variable, aggregation, start_date, end_date)
    direction_columns = [col for col in aggregated_data.columns if "Part" in col]
    aggregated_data['average_swell_direction_deg'] = aggregated_data[direction_columns].mean(axis=1)

    aggregated_data['wave_height'] = aggregated_data['lotusMaxBWH_ft']
    
    aggregated_data['direction_radians'] = np.deg2rad(aggregated_data['average_swell_direction_deg'])
    
    # Create a base chart
    base = alt.Chart(aggregated_data).encode(
        theta=alt.Theta('direction_radians:Q', stack=True), 
        radius=alt.Radius('wave_height:Q', scale=alt.Scale(type='sqrt', zero=True, rangeMin=20)), 
        color=alt.Color('wave_height:Q', scale=alt.Scale(scheme="inferno")),  
        tooltip=[
            alt.Tooltip('average_swell_direction_deg:N', title='Direction (degrees)'),
            alt.Tooltip('wave_height:Q', title='Wave Height (ft)')
        ]
    )
    
    chart = base.mark_arc(innerRadius=10).properties(
        width=390,
        height=390
    )
    
    return chart

def generate_peak_period_chart():
    variable = 'lotusTPPartX_sec'
    aggregation = 'Week'
    start_date = request.args.get('startDate', None)
    end_date = request.args.get('endDate', None)

    # Process the data
    aggregated_data = process_data(variable, aggregation, start_date, end_date)
    direction_columns = [col for col in aggregated_data.columns if "Part" in col]
    aggregated_data['average_peak_period'] = aggregated_data[direction_columns].max(axis=1)

    min_peak_period = aggregated_data['average_peak_period'].min()
    max_peak_period = aggregated_data['average_peak_period'].max()

    base_chart = alt.Chart(aggregated_data).properties(
        width=900,
        height=600,
        title='Relationship between Average Peak Period and Wave Height'
    )
    
    # Define the scatter plot.
    scatter_chart = base_chart.mark_point().encode(
        x=alt.X('average_peak_period', title='Average Peak Period (s)', scale=alt.Scale(domain=(min_peak_period, max_peak_period))),
        y=alt.Y('lotusMaxBWH_ft', title='Max Breaking Wave Height (ft)'),
        tooltip=['time_period', 'average_peak_period', 'lotusMaxBWH_ft']
    )

    # Calculate the regression line manually
    slope, intercept, r_value, p_value, std_err = stats.linregress(
        aggregated_data['average_peak_period'],
        aggregated_data['lotusMaxBWH_ft']
    )
    
    # Create a new DataFrame for the regression line
    regression_df = pd.DataFrame({
        'average_peak_period': aggregated_data['average_peak_period'],
        'regression_line': (aggregated_data['average_peak_period'] * slope) + intercept
    })
    
    # Create an Altair chart for the regression line
    regression_chart = alt.Chart(regression_df).mark_line(color='firebrick').encode(
        x='average_peak_period',
        y='regression_line'
    )
    
    # Combine the scatter chart with the regression line chart
    final_chart = scatter_chart + regression_chart
    
    # Return the final combined chart
    return final_chart

def generate_peak_period_line_chart():
    variable = 'lotusTPPartX_sec'
    aggregation = 'Month'
    start_date = request.args.get('startDate', None)
    end_date = request.args.get('endDate', None)

    # Process the data
    aggregated_data = process_data(variable, aggregation, start_date, end_date)
    direction_columns = [col for col in aggregated_data.columns if "Part" in col]
    aggregated_data['average_peak_period'] = aggregated_data[direction_columns].max(axis=1)

    min_peak_period = aggregated_data['average_peak_period'].min()
    max_peak_period = aggregated_data['average_peak_period'].max()

    line_chart = alt.Chart(aggregated_data).mark_line().encode(
        x=alt.X('time_period:T', title='Time Period'),
        y=alt.Y('average_peak_period:Q', title='Average Peak Period (seconds)' ,scale=alt.Scale(domain=(min_peak_period, max_peak_period))), 
        tooltip=[alt.Tooltip('time_period:T', title='Time Period'), alt.Tooltip('average_peak_period:Q', title='Average Peak Period')]
    ).properties(
        width=900,
        height=600,
        title='Average Peak Period Over Time'
    )
    
    return line_chart


def generate_swell_partitions_chart():
    variable = 'lotusSighPartX_mt'
    aggregation = 'Month'
    start_date = request.args.get('startDate', None)
    end_date = request.args.get('endDate', None)

    aggregated_data = process_data(variable, aggregation, start_date, end_date)
    
    # Base chart configuration
    base = alt.Chart(aggregated_data).encode(
        x=alt.X('time_period', type=get_x_axis_type(aggregation), title='Time Period'),
    ).properties(width=300, height=200)

    global_min = aggregated_data[[variable.replace("X", str(i)) for i in range(6)]].min().min()
    global_max = aggregated_data[[variable.replace("X", str(i)) for i in range(6)]].max().max()
    
    # Handling partitioned variables, assuming variable format "PartX" where X is the partition number
    partition_charts = []
    for i in range(6):  # For partitions 0-5
        partition_variable = variable.replace("X",f"{i}")
        partition_chart = base.mark_line().encode(
            y=alt.Y(f'{partition_variable}:Q', scale=alt.Scale(domain=[global_min, global_max]), title=f'Partition {i}'),
            tooltip=[alt.Tooltip('time_period:N', title='Time Period'), alt.Tooltip(f'{partition_variable}:Q', title=f'Partition {i}')]
        )
        partition_charts.append(partition_chart)
        
    # Assuming we always have 6 charts ready to be displayed
    top_row = alt.hconcat(*partition_charts[:3])  # First 3 charts
    bottom_row = alt.hconcat(*partition_charts[3:])  # Last 3 charts
    
    chart = alt.vconcat(top_row, bottom_row).resolve_scale(
        x='shared',
        y='shared'
    )
    
    return chart


def generate_swell_partitions_chart2():
    variable = 'lotusSighPartX_mt'
    aggregation = 'Month'
    start_date = request.args.get('startDate', None)
    end_date = request.args.get('endDate', None)

    aggregated_data = process_data(variable, aggregation, start_date, end_date)
    
    # Calculate the max and sum of partitions
    partition_columns = [variable.replace("X", str(i)) for i in range(6)]

    weights = [1, 0.6, 0.5, 0.4, 0.3, 0.2]
    aggregated_data['sum_of_partitions'] = sum(
        aggregated_data[variable.replace("X", str(i))] * weight for i, weight in enumerate(weights)
    )
    
    min_value = min(aggregated_data['sum_of_partitions'].min(), aggregated_data['lotusSigh_mt'].min())
    max_value = max(aggregated_data['sum_of_partitions'].max(), aggregated_data['lotusSigh_mt'].max())
    padding = (max_value - min_value) * 0.05
    max_value += padding
    min_value -= padding

    # Base chart configuration
    base = alt.Chart(aggregated_data).encode(
        x=alt.X('time_period:T', title='Time Period'),
        y=alt.Y('sum_of_partitions:Q', scale=alt.Scale(domain=(min_value, max_value)), title='Sum of Partitions (meters)'),
    ).properties(
        width=900,
        height=600,
        title='Weighted Sum of Wave Partitions vs. Total Significant Wave Height'
    )
    
    # Create a line chart with dots for sum of partitions
    sum_chart = base.mark_line(color='green', strokeWidth=3).encode(
        y=alt.Y('sum_of_partitions:Q', title='Sum of Partitions (meters)', scale=alt.Scale(domain=(min_value, max_value))),
        tooltip=[alt.Tooltip('time_period:T', title='Time Period'), alt.Tooltip('sum_of_partitions:Q', title='Sum of Partitions')]
    )
    sum_points = base.mark_point(color='green', size=50).encode(
        y=alt.Y('sum_of_partitions:Q', scale=alt.Scale(domain=(min_value, max_value))),
        tooltip=[alt.Tooltip('time_period:T', title='Time Period'), alt.Tooltip('sum_of_partitions:Q', title='Sum of Partitions')]
    )
    
    # Create a line chart with dots for total significant wave height
    total_wave_height_chart = base.mark_line(color='blue', strokeWidth=3).encode(
        y=alt.Y('lotusSigh_mt:Q', title='Total Significant Wave Height (meters)', scale=alt.Scale(domain=(min_value, max_value))),
        tooltip=[alt.Tooltip('time_period:T', title='Time Period'), alt.Tooltip('lotusSigh_mt:Q', title='Total Significant Wave Height')]
    )
    total_points = base.mark_point(color='blue', size=50).encode(
        y=alt.Y('lotusSigh_mt:Q', scale=alt.Scale(domain=(min_value, max_value))),
        tooltip=[alt.Tooltip('time_period:T', title='Time Period'), alt.Tooltip('lotusSigh_mt:Q', title='Total Significant Wave Height')]
    )
    
    # Combine the line charts and point charts
    combined_chart = alt.layer(sum_chart, sum_points, total_wave_height_chart, total_points).resolve_scale(
        y='shared'
    )
    
    # Return the combined chart
    return combined_chart

def degrees_to_compass(deg):
    compass_brackets = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW', 'N']
    compass_lookup = dict(zip(range(0, 361, 45), compass_brackets))
    deg_rounded = int(round(deg / 45) * 45)
    if deg_rounded == 360:
        deg_rounded = 0  # Handle the edge case where rounding leads to 360 degrees
    return compass_lookup[deg_rounded]

def generate_complex_chart(wave_set, tide, swell_dir, peak_period):
    wave_set = wave_set.add_suffix('_wave')
    tide = tide.add_suffix('_tide')
    swell_dir = swell_dir.add_suffix('_swell')
    peak_period = peak_period.add_suffix('_peak')

    # Assuming 'time_period' is the common column we're joining on
    # We'll remove the suffix from 'time_period' so it can be used for merging
    wave_set.rename(columns={'time_period_wave': 'time_period'}, inplace=True)
    tide.rename(columns={'time_period_tide': 'time_period'}, inplace=True)
    swell_dir.rename(columns={'time_period_swell': 'time_period'}, inplace=True)
    peak_period.rename(columns={'time_period_peak': 'time_period'}, inplace=True)

    # Now merge the DataFrames
    merged_data = (
        wave_set
        .merge(tide, on='time_period')
        .merge(swell_dir, on='time_period')
        .merge(peak_period, on='time_period')
    )
    merged_data['compass_direction'] = merged_data['average_swell_dir_swell'].apply(degrees_to_compass)
    
    swell_color_scale = alt.Scale(domain=['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'],
                                  range=['purple', 'orange', 'yellow', 'teal', 'brown', 'red', 'blue', 'green'])

    size_scale = alt.Scale(domain=[15, 25],  # Assuming the peak period goes from 0 to 20 seconds
                           range=[10, 200])  # Size range from small to large

    # Chart for Tide levels
    tide_chart = alt.Chart(merged_data).mark_line(color='orange').encode(
        x='time_period:T',
        y='tide_ft_tide:Q',
        tooltip=['time_period:T', 'tide_ft_tide:Q']
    ) + alt.Chart(merged_data).mark_point(opacity=0.5).encode(
        x='time_period:T',
        y='tide_ft_tide:Q',
        size=alt.Size('average_peak_period_peak:Q', scale=size_scale, title='Peak Period (sec)'),  # Dynamic size based on peak period
        color=alt.Color('compass_direction:N', scale=swell_color_scale, title='Swell Direction'),  # Color by swell direction
        tooltip=['time_period:T', 'tide_ft_tide:Q', 'compass_direction:N', 'average_peak_period_peak:Q']
    )
    
    # Chart for Wave heights
    wave_height_chart = alt.Chart(merged_data).mark_line(color='blue').encode(
        x='time_period:T',
        y='lotusMaxBWH_ft_wave:Q',
        tooltip=['time_period:T', 'lotusMaxBWH_ft_wave:Q']
    ) + alt.Chart(merged_data).mark_point(opacity=0.5).encode(
        x='time_period:T',
        y='lotusMaxBWH_ft_wave:Q',
        size=alt.Size('average_peak_period_peak:Q', scale=size_scale, title='Peak Period (sec)'),  # Dynamic size based on peak period
        color=alt.Color('compass_direction:N', scale=swell_color_scale, title='Swell Direction'),  # Color by swell direction
        tooltip=['time_period:T', 'lotusMaxBWH_ft_wave:Q', 'compass_direction:N', 'average_peak_period_peak:Q']
    )
    
    # Combine charts
    combined_chart = alt.layer(tide_chart, wave_height_chart).resolve_scale(
        y='shared'
    ).properties(
        title='Wave Height and Tide Over Time with Swell Direction and Peak Period',
        width=500,
        height=300
    )

    return combined_chart


def generate_top_biggest_waves():
    aggregated_data = process_data('lotusMaxBWH_ft', 'Week', None, None)

    # Use this to manually look at dates that have big waves
    # top_waves = aggregated_data.nlargest(5, 'lotusMaxBWH_ft')

    wave_set1 = process_data('lotusMaxBWH_ft', 'Hour', '2023-01-02', '2023-01-09')
    wave_set2 = process_data('lotusMaxBWH_ft', 'Hour', '2023-12-24', '2023-12-31')
    wave_set3 = process_data('lotusMaxBWH_ft', 'Hour', '2021-01-07', '2021-01-14')

    wave_set1_tide = process_data('tide_ft', 'Hour', '2023-01-02', '2023-01-09')
    wave_set2_tide = process_data('tide_ft', 'Hour', '2023-12-24', '2023-12-31')
    wave_set3_tide = process_data('tide_ft', 'Hour', '2021-01-07', '2021-01-14')

    wave_set1_swell_dir = process_data('lotusPDirPartX_deg', 'Hour', '2023-01-02', '2023-01-09')
    wave_set2_swell_dir = process_data('lotusPDirPartX_deg', 'Hour', '2023-12-24', '2023-12-31')
    wave_set3_swell_dir = process_data('lotusPDirPartX_deg', 'Hour', '2021-01-07', '2021-01-14')

    columns = [col for col in wave_set1_swell_dir.columns if "Part" in col]
    wave_set1_swell_dir['average_swell_dir'] = wave_set1_swell_dir[columns].max(axis=1)
    wave_set2_swell_dir['average_swell_dir'] = wave_set2_swell_dir[columns].max(axis=1)
    wave_set3_swell_dir['average_swell_dir'] = wave_set3_swell_dir[columns].max(axis=1)

    wave_set1_peak_period = process_data('lotusTPPartX_sec', 'Hour', '2023-01-02', '2023-01-09')
    wave_set2_peak_period = process_data('lotusTPPartX_sec', 'Hour', '2023-12-24', '2023-12-31')
    wave_set3_peak_period = process_data('lotusTPPartX_sec', 'Hour', '2021-01-07', '2021-01-14')

    columns = [col for col in wave_set1_peak_period.columns if "Part" in col]
    wave_set1_peak_period['average_peak_period'] = wave_set1_peak_period[columns].max(axis=1)
    wave_set2_peak_period['average_peak_period'] = wave_set2_peak_period[columns].max(axis=1)
    wave_set3_peak_period['average_peak_period'] = wave_set3_peak_period[columns].max(axis=1)

    chart1 = generate_complex_chart(wave_set1, wave_set1_tide, wave_set1_swell_dir, wave_set1_peak_period)
    chart2 = generate_complex_chart(wave_set2, wave_set2_tide, wave_set2_swell_dir, wave_set2_peak_period)
    chart3 = generate_complex_chart(wave_set3, wave_set3_tide, wave_set3_swell_dir, wave_set3_peak_period)
    
    return chart1 | chart2 #| chart3

def generate_top_smallest_waves():
    aggregated_data = process_data('lotusMinBWH_ft', 'Week', None, None)

    # Use this to manually look at dates that have small waves
    top_waves = aggregated_data.nsmallest(5, 'lotusMinBWH_ft')

    print(top_waves)

    wave_set1 = process_data('lotusMaxBWH_ft', 'Hour', '2021-07-26', '2021-08-01')
    wave_set2 = process_data('lotusMaxBWH_ft', 'Hour', '2019-11-04', '2019-11-11')
    wave_set3 = process_data('lotusMaxBWH_ft', 'Hour', '2022-07-25', '2022-08-01')

    wave_set1_tide = process_data('tide_ft', 'Hour', '2021-07-26', '2021-08-01')
    wave_set2_tide = process_data('tide_ft', 'Hour', '2019-11-04', '2019-11-11')
    wave_set3_tide = process_data('tide_ft', 'Hour', '2022-07-25', '2022-08-01')

    wave_set1_swell_dir = process_data('lotusPDirPartX_deg', 'Hour', '2021-07-26', '2021-08-01')
    wave_set2_swell_dir = process_data('lotusPDirPartX_deg', 'Hour', '2019-11-04', '2019-11-11')
    wave_set3_swell_dir = process_data('lotusPDirPartX_deg', 'Hour', '2022-07-25', '2022-08-01')

    columns = [col for col in wave_set1_swell_dir.columns if "Part" in col]
    wave_set1_swell_dir['average_swell_dir'] = wave_set1_swell_dir[columns].max(axis=1)
    wave_set2_swell_dir['average_swell_dir'] = wave_set2_swell_dir[columns].max(axis=1)
    wave_set3_swell_dir['average_swell_dir'] = wave_set3_swell_dir[columns].max(axis=1)

    wave_set1_peak_period = process_data('lotusTPPartX_sec', 'Hour', '2021-07-26', '2021-08-01')
    wave_set2_peak_period = process_data('lotusTPPartX_sec', 'Hour', '2019-11-04', '2019-11-11')
    wave_set3_peak_period = process_data('lotusTPPartX_sec', 'Hour', '2022-07-25', '2022-08-01')

    columns = [col for col in wave_set1_peak_period.columns if "Part" in col]
    wave_set1_peak_period['average_peak_period'] = wave_set1_peak_period[columns].max(axis=1)
    wave_set2_peak_period['average_peak_period'] = wave_set2_peak_period[columns].max(axis=1)
    wave_set3_peak_period['average_peak_period'] = wave_set3_peak_period[columns].max(axis=1)

    chart1 = generate_complex_chart(wave_set1, wave_set1_tide, wave_set1_swell_dir, wave_set1_peak_period)
    chart2 = generate_complex_chart(wave_set2, wave_set2_tide, wave_set2_swell_dir, wave_set2_peak_period)
    chart3 = generate_complex_chart(wave_set3, wave_set3_tide, wave_set3_swell_dir, wave_set3_peak_period)
    
    return chart1 | chart2 #| chart3

app = Flask(__name__)

@app.route('/update_chart', methods=['GET'])
def update_chart():
    variable = request.args.get('variable', 'lotusSigh_mt')
    aggregation = request.args.get('aggregation', 'Month')
    start_date = request.args.get('startDate', None)
    end_date = request.args.get('endDate', None)
    chart_type = request.args.get('chartType', 'line')

    aggregated_data = process_data(variable, aggregation, start_date, end_date)
    if chart_type == 'line':
        chart_spec = generate_line_chart(aggregated_data, variable, aggregation).to_dict()
    elif chart_type == 'bar':
        chart_spec = generate_bar_chart(aggregated_data, variable, aggregation).to_dict()
    

    return jsonify(chart_spec)

@app.route('/update_composite_chart', methods=['GET'])
def update_composite_chart():
    user_variable = request.args.get('variable', 'lotusSigh_mt')
    aggregation = request.args.get('aggregation', 'Month')
    start_date = request.args.get('startDate', None)
    end_date = request.args.get('endDate', None)
    chart_type = request.args.get('chartType', 'line')

    aggregated_data = process_data(user_variable, aggregation, start_date, end_date)

    if chart_type == 'line':
        chart_spec = generate_composite_line_chart(aggregated_data, user_variable, aggregation).to_dict()
    elif chart_type == 'bar':
        chart_spec = generate_composite_bar_chart(aggregated_data, user_variable, aggregation).to_dict()
    

    return jsonify(chart_spec)


@app.route('/')
def home():

    seasonal_chart_spec = generate_seasonal_chart().to_dict()

    tide_influence_chart_spec = generate_tide_influence_chart().to_dict()

    swell_direction_chart_spec = generate_swell_direction_chart().to_dict()
    
    peak_period_line_chart_spec = generate_peak_period_line_chart().to_dict()
    
    peak_period_chart_spec = generate_peak_period_chart().to_dict()

    swell_partitions_chart_spec = generate_swell_partitions_chart().to_dict()

    swell_partitions_chart_spec2 = generate_swell_partitions_chart2().to_dict()

    big_chart1 = generate_top_biggest_waves().to_dict()

    small_chart1 = generate_top_smallest_waves().to_dict()

    # Show vars of top 3 largest waves and smallest waves and what the conditions were
    
    # Prepare data for Chart 1
    variable1 = request.args.get('variable1', default='lotusSigh_mt')
    aggregation1 = request.args.get('aggregation1', default='Month')
    aggregated_data1 = process_data(variable1, aggregation1)
    chart1_spec = generate_line_chart(aggregated_data1, variable1, aggregation1).to_dict()

    # Prepare data for Chart 2
    variable2 = request.args.get('variable2', default='lotusSigh_mt')
    aggregation2 = request.args.get('aggregation2', default='Month')
    aggregated_data2 = process_data(variable2, aggregation2)
    chart2_spec = generate_composite_line_chart(aggregated_data2, variable2, aggregation2).to_dict()

    # Prepare data for Chart 3
    variable3 = request.args.get('variable3', default='lotusSigh_mt')
    aggregation3 = request.args.get('aggregation3', default='Month')
    aggregated_data3 = process_data(variable3, aggregation3)
    chart3_spec = generate_line_chart(aggregated_data3, variable3, aggregation3).to_dict()

    # Add more charts as needed

    return render_template('index2.html',
                           seasonal_chart_spec=seasonal_chart_spec,
                           tide_influence_chart_spec=tide_influence_chart_spec,
                           swell_direction_chart_spec=swell_direction_chart_spec,
                           peak_period_line_chart_spec=peak_period_line_chart_spec,
                           peak_period_chart_spec=peak_period_chart_spec,
                           swell_partitions_chart_spec=swell_partitions_chart_spec,
                           swell_partitions_chart_spec2=swell_partitions_chart_spec2,
                           big_chart1=big_chart1,
                           small_chart1=small_chart1,
                           chart1_spec=chart1_spec,
                           chart2_spec=chart2_spec,
                           chart3_spec=chart2_spec,
                           # Pass additional chart specs as needed
                           )

if __name__ == '__main__':
    app.run(debug=True)
