from flask import Flask, jsonify, render_template, request
import altair as alt
import pandas as pd



#####################
## Data Processing ##
#####################
def process_data(variable, aggregation_level, start_date=None, end_date=None):
    data = pd.read_csv('MorroBayHeights.csv')
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
    if aggregation_level == 'Day':
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

    print(aggregated_data)
    
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
        base = base.properties(width=800, height=400)
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
        
        #chart = alt.layer(*partition_charts)  # Combine all partition charts into a single chart
        
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
        base = base.properties(width=800, height=400)
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
        
        #chart = alt.layer(*partition_charts)  # Combine all partition charts into a single chart
        
        # Assuming we always have 6 charts ready to be displayed
        top_row = alt.hconcat(*partition_charts[:3])  # First 3 charts
        bottom_row = alt.hconcat(*partition_charts[3:])  # Last 3 charts

        chart = alt.vconcat(top_row, bottom_row).resolve_scale(
            x='shared',
            y='shared'
        )
        
    return chart

import altair as alt

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
        base = base.properties(width=800, height=400)
        # User Variable Chart (non-partitioned)
        user_var_chart = base.mark_line(color='green').encode(
            y=alt.Y(f'{user_variable}:Q', title=f'{user_variable}'),
            tooltip=[alt.Tooltip(f'{user_variable}:Q', title=f'{user_variable}')]
        )
        chart = alt.layer(min_bwh, max_bwh, user_var_chart).resolve_scale(
            y='shared'
        ).properties(width=800, height=400)
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
        base = base.properties(width=800, height=400)
        # User Variable Chart (non-partitioned)
        user_var_chart = base.mark_bar(color='green').encode(
            y=alt.Y(f'{user_variable}:Q', title=f'{user_variable}'),
            tooltip=[alt.Tooltip(f'{user_variable}:Q', title=f'{user_variable}')]
        )
        chart = alt.layer(min_bwh, max_bwh, user_var_chart).resolve_scale(
            y='shared'
        ).properties(width=800, height=400)
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

    return render_template('index.html',
                           chart1_spec=chart1_spec,
                           chart2_spec=chart2_spec,
                           chart3_spec=chart2_spec,
                           # Pass additional chart specs as needed
                           )

if __name__ == '__main__':
    app.run(debug=True)
