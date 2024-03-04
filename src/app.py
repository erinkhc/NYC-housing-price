import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import dash
from dash import Dash,dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import altair as alt
import dash_bootstrap_components as dbc
import numpy as np
import plotly.graph_objects as go
import os



# # path build
# geojson_file = os.path.join(current_dir, 'NYC_Borough_Boundary.geojson')
# csv_file = os.path.join(current_dir, 'NewYork_add_all.csv')
#
# # load data
# nyc_boroughs = gpd.read_file(geojson_file)
# joined_data = pd.read_csv(csv_file)

# get current and parent dir
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# path build
data_dir = os.path.join(parent_dir, 'data')
geojson_file = os.path.join(data_dir, 'NYC_Borough_Boundary.geojson')
csv_file = os.path.join(data_dir, 'NewYork_add_all.csv')

# load data
nyc_boroughs = gpd.read_file(geojson_file)
joined_data = pd.read_csv(csv_file)


# mapbox API key
mapbox_key = "pk.eyJ1IjoibWFudHVvbHVvYnVrdSIsImEiOiJjbHQ4OGJuaGowOXpuMmlvNHRxMjhwcjNwIn0.Ah-KdY3j7V0mm_86NfIJfg"

# calculate average price
average_prices = joined_data.groupby('BoroName')['PRICE'].mean().reset_index()
average_prices.columns = ['BoroName', 'AveragePrice']

# merge to nyc_boroughs_with_prices
nyc_boroughs_with_prices = nyc_boroughs.merge(average_prices, on='BoroName')
nyc_boroughs_with_prices['AveragePriceInMillions'] = nyc_boroughs_with_prices['AveragePrice'] / 1000000
nyc_boroughs_with_prices['AveragePriceInMillions'] = nyc_boroughs_with_prices['AveragePriceInMillions'].round(2)

# group by both boro and type
grouped_data = joined_data.groupby(['BoroName', 'TYPE_VIZ'])['PRICE'].agg(['mean', 'count']).reset_index()
grouped_data.columns = ['BoroName', 'TYPE_VIZ', 'AveragePrice', 'Count']

broker_count = joined_data.groupby(['BoroName', 'BROKERTITLE']).size().reset_index(name='Transactions')
top_brokers_per_boro = broker_count.groupby('BoroName').apply(lambda x: x.sort_values('Transactions', ascending=False).head(5))
top_brokers_per_boro['BROKERTITLE'] = top_brokers_per_boro['BROKERTITLE'].str.replace("Brokered by ", "", regex=False)

# Reset the index to make the DataFrame tidy
top_brokers_per_boro.reset_index(drop=True, inplace=True)
top_brokers_per_boro.head(20)

top_brokers_nyc = joined_data['BROKERTITLE'].value_counts().head(5).reset_index()
top_brokers_nyc.columns = ['BROKERTITLE', 'Transactions']

top_brokers_nyc['BROKERTITLE'] = top_brokers_nyc['BROKERTITLE'].str.replace("Brokered by ", "", regex=False)


top_brokers_nyc['BoroName'] = 'All'

top_brokers_combined = pd.concat([top_brokers_per_boro, top_brokers_nyc], ignore_index=True)
top_brokers_combined.reset_index(drop=True, inplace=True)


overall_broker = top_brokers_combined[top_brokers_combined["BoroName"]=="All"]

overall_broker = top_brokers_combined[top_brokers_combined["BoroName"]=="All"]

# Initialize Dash app with Bootstrap CSS
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)

# Declare server for Heroku deployment. Needed for Procfile.
server = app.server

border_style = {
    'borderRadius': '5px',
    'boxShadow': '2px 2px 5px rgba(0, 0, 0, 0.1)',  # a lighter color
    'margin': '10px',
    'border': '1px solid #eeeeee'
}

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(
            [
                html.H4("Categories",
                        style={'textAlign': 'center', 'margin-top': '40px', 'fontWeight': 'bold', 'color': '#007bff'}),
                html.P(
                    "Choose to explore the housing market based on property types or by boroughs.",
                    style={'textAlign': 'justify', 'color': '#5DADE2', 'margin-bottom': '20px'}
                ),
                dbc.Tabs([
                    dbc.Tab(label="Types", tab_id="tab-1"),
                    dbc.Tab(label="Boroughs", tab_id="tab-2"),
                ], id="tabs", active_tab="tab-1"),
            ],
            width=2, style={'height': '100vh', 'backgroundColor': '#f8f9fa', 'overflowY': 'scroll'}
        ),
        dbc.Col([
            html.Div([
                html.H1("Welcome to New York Housing Market",
                        style={'textAlign': 'center', 'margin-top': '20px', 'fontWeight': 'bold', 'color': '#007bff'}),
                html.P(
                    "Explore comprehensive analytics on housing prices across New York's diverse neighborhoods. "
                    "Dive into detailed market trends, from the bustling boroughs to the tranquil suburbs. "
                    "Whether you're a prospective buyer, a real estate enthusiast, or a data analyst, "
                    "our interactive dashboards offer valuable insights to inform your decisions.",
                    style={'textAlign': 'justify', 'color': '#5DADE2'}
                ),
                html.Div(id='top-bar',
                         style={'textAlign': 'center', 'margin': '10px 0', 'fontWeight': 'bold', 'fontSize': '20px',
                                'color': '#007bff'}),
            ]),
            html.Div(id='tabs-content')
        ], width=10),
    ])
], fluid=True)


@app.callback(
    [Output('tabs-content', 'children'),
     Output('top-bar', 'children')],
    [Input('tabs', 'active_tab')]
)
def render_tab_content(active_tab):
    if active_tab == "tab-1":
        top_bar_content = "House Section"
        tab_content = html.Div([
            dbc.Row([
                dbc.Col(
                    html.Div([dcc.Graph(id='map-graph', figure=fig)]),
                    #width=8
                    md = 6,style={'marginLeft': '20px'}
                    #, style={'border': '1px solid #d3d3d3', 'border-radius': '10px'}
                ),
                dbc.Col([
                    html.Div([
                        html.Label("Select house locality:"),
                        filter_region,
                        html.Br(),
                        html.Label("Select house type:"),
                        filter_type,
                        html.Br(),
                        html.Label("Select price range:"),
                        dbc.Row(price_slider, style=price_slider_style),
                    ]),
                ], md = 5, style={'marginLeft': '20px'})#, md = 4, style = {'border': '1px solid #d3d3d3', 'border-radius': '10px'})
            ], className="mb-4"),
            dbc.Row([
                dcc.Dropdown(
                    id='type_viz_dropdown',
                    options=[{'label': i, 'value': i} for i in sorted(joined_data['TYPE_VIZ'].unique())] + [
                        {'label': 'All', 'value': 'All'}],
                    value='All',  # Default value
                    clearable = False
                ),
                html.Br()
            ]),
            dbc.Row([
                html.Div(id='chart_container')  # Container for charts
            ])
        ])
    elif active_tab == "tab-2":
        top_bar_content = "Boro Section: Detailed Information"
        tab_content = dbc.Container([
            dbc.Row([
                dbc.Col(dcc.Graph(id='nyc-map', figure={}, style={'height': '60vh', **border_style}), md=6),
                dbc.Col(dcc.Graph(id='bubble-chart', figure={}, style={'height': '40vh', **border_style}), md=6),
            ]),
            dbc.Row([
                dbc.Col([
                    html.Label('Number of Bedrooms:'),
                    dcc.Dropdown(
                        id='num-bedrooms-dropdown',
                        options=[{'label': str(i), 'value': i} for i in range(1, 6)] + [{'label': '5+', 'value': '5+'}],
                        value=1
                    ),
                    html.Label('Number of Bathrooms:'),
                    dcc.Dropdown(
                        id='num-bathrooms-dropdown',
                        options=[{'label': str(i), 'value': i} for i in range(1, 6)] + [{'label': '5+', 'value': '5+'}],
                        value=1
                    ),
                    html.Div(id='price-range-display', children='Select an area and set filters to see price range'),
                ], md=6, style={'transform': 'translateY(-150px)'}),
                dbc.Col(dcc.Graph(id='broker-histogram', figure={},
                                  style={'height': '40vh', **border_style, 'transform': 'translateY(-150px)'}, ), md=6),
                # 将 broker-histogram 放回右侧
            ], align="end")
        ], fluid=True,
            style={'backgroundColor': '#f8f9fa', 'height': 'auto', 'width': 'auto'})  # 'height': 'calc(100vh - 56px)'

    return tab_content, top_bar_content


@app.callback(
    [Output('nyc-map', 'figure'),
     Output('bubble-chart', 'figure'),
     Output('broker-histogram', 'figure'),
     Output('price-range-display', 'children')],
    [Input('nyc-map', 'clickData'),
     Input('num-bedrooms-dropdown', 'value'),
     Input('num-bathrooms-dropdown', 'value')]
)
#     return fig_map, fig_bubble, fig_histogram, price_range_text
def update_content(clickData, num_bedrooms, num_bathrooms):
    price_range_text = 'Select an area and set filters to see price range'
    # Placeholder for updated opacities
    opacities = [0.5 if not clickData else 0.2 for _ in nyc_boroughs_with_prices.index]

    if clickData:
        clicked_boro = clickData['points'][0]['customdata'][0]
        opacities = [0.5 if boro == clicked_boro else 0.2 for boro in nyc_boroughs_with_prices['BoroName']]
        if num_bedrooms == '5+':
            filtered_data_prices = joined_data[(joined_data['BEDS'] >= 5) &
                                               (joined_data['BoroName'] == clicked_boro)]
        else:
            filtered_data_prices = joined_data[(joined_data['BEDS'] == num_bedrooms) &
                                               (joined_data['BoroName'] == clicked_boro)]

        if num_bathrooms == '5+':
            filtered_data_prices = filtered_data_prices[filtered_data_prices['BATH'] >= 5]
        else:
            filtered_data_prices = filtered_data_prices[filtered_data_prices['BATH'] == num_bathrooms]
        # Calculate the price range
        min_price = filtered_data_prices['PRICE'].min()
        max_price = filtered_data_prices['PRICE'].max()
        price_range_text = f"Price Range: ${min_price:,.0f} - ${max_price:,.0f}" if not filtered_data_prices.empty else "No data for selected filters"

    fig = px.choropleth_mapbox(nyc_boroughs_with_prices,
                               geojson=nyc_boroughs_with_prices.geometry,
                               locations=nyc_boroughs_with_prices.index,
                               color="AveragePrice",
                               color_continuous_scale=px.colors.sequential.Viridis,
                               mapbox_style="carto-positron",
                               zoom=9, center={"lat": 40.730610, "lon": -73.935242},
                               opacity=opacities,
                               custom_data=["BoroName"],
                               hover_data={'BoroName': True, 'AveragePriceInMillions': ':.2f'})
    fig.update_layout(clickmode='event+select')
    fig.update_traces(hovertemplate="Borough Name: %{customdata[0]}<br>Average Price: $%{customdata[1]} Million <br>")

    fig.update_layout(mapbox_zoom=9, mapbox_center={"lat": 40.730610, "lon": -73.935242})
    fig.update_layout(margin={"r": 3, "t": 3, "l": 3, "b": 3})
    fig.update_layout(coloraxis_colorbar=dict(thickness=10, title_font_size=10))

    # Update bubble chart based on clickData
    # Placeholder for bubble chart logic
    if not clickData:
        overall_avg_price_count = joined_data.groupby('TYPE_VIZ')['PRICE'].agg(['mean', 'count']).reset_index()
        overall_avg_price_count.columns = ['TYPE_VIZ', 'AveragePrice', 'Count']
        bubble_fig = px.scatter(overall_avg_price_count,
                                x='TYPE_VIZ',
                                y='AveragePrice',
                                size='Count',
                                color='TYPE_VIZ',
                                hover_name='TYPE_VIZ',
                                size_max=45,
                                title="Overall Properties in NYC")
        hist_fig = px.bar(overall_broker,
                          x='Transactions',
                          y='BROKERTITLE',
                          color='BoroName',
                          title=f"Top 5 Brokers in NYC",
                          labels={'BROKERTITLE': 'Broker', 'Transactions': 'Transaction Count'})
    else:
        boro_name = clicked_boro
        filtered_data = grouped_data[grouped_data['BoroName'] == boro_name]
        bubble_fig = px.scatter(filtered_data,
                                x='TYPE_VIZ',
                                y='AveragePrice',
                                size='Count',
                                color='TYPE_VIZ',
                                hover_name='TYPE_VIZ',
                                size_max=45,
                                title=f"Properties in {boro_name}")
        filtered_data_broker = top_brokers_per_boro[top_brokers_combined['BoroName'] == boro_name]
        hist_fig = px.bar(filtered_data_broker,
                          x='Transactions',
                          y='BROKERTITLE',
                          color='BoroName',
                          title=f"Top 5 Brokers in {boro_name}",
                          labels={'BROKERTITLE': 'Broker', 'Transactions': 'Transaction Count'})

    # bubble_fig = px.scatter()  # Update this with actual data
    # bubble_fig.update_layout(title_text='Property Analysis', title_font_size=16)
    bubble_fig.update_traces(
        selector=dict(mode='markers'), showlegend=False)
    bubble_fig.update_layout(hoverlabel=dict(namelength=-1))
    bubble_fig.update_layout(margin={"r": 20, "t": 38, "l": 3, "b": 3},
                             xaxis_title='',
                             xaxis_tickangle=0,
                             xaxis_tickfont=dict(size=11),
                             yaxis_title_font=dict(size=15))
    bubble_fig.update_traces(hovertemplate='Property Number: %{marker.size}<br>Average Price: %{y}', showlegend=False)

    hist_fig.update_layout(barmode='group', xaxis={'categoryorder': 'total descending'})
    hist_fig.update_layout(margin={"r": 0, "t": 30, "l": 0, "b": 0})
    hist_fig.update_layout(showlegend=False)

    return fig, bubble_fig, hist_fig, price_range_text


# Define the function to create the charts
def create_charts(data, type_viz):
    if type_viz == 'All':
        # If "All" is selected, use the entire dataset
        data_type_filtered = data.copy()
    else:
        # Otherwise, filter based on the selected TYPE_VIZ
        data_type_filtered = data[data['TYPE_VIZ'] == type_viz]

    # Here you may calculate aggregations or transformations as needed
    # For example, calculating price per square foot for each row
    data_type_filtered['PRICE_PER_SQFT'] = data_type_filtered['PRICE'] / data_type_filtered['PROPERTYSQFT']

    # Create a boxplot of price per square foot by BoroName
    boxplot = alt.Chart(data_type_filtered).mark_boxplot().encode(
        x='PRICE_PER_SQFT:Q',
        y='BoroName:N',
        color='BoroName:N',
        tooltip=['PRICE_PER_SQFT', 'BoroName']
    ).properties(
        title=f'Boxplot of Price per Square Foot by Locality - {type_viz}',
        width=300,
        height=200
    )

    # Create a pie chart of property count by BoroName for the selected type of visualization
    pie_chart_data = data_type_filtered['BoroName'].value_counts().reset_index()
    pie_chart_data.columns = ['BoroName', 'count']
    total_count = pie_chart_data['count'].sum()
    pie_chart_data['percentage'] = (pie_chart_data['count'] / total_count * 100).round(2)

    pie_chart = alt.Chart(pie_chart_data).mark_arc().encode(
        theta=alt.Theta(field="count", type="quantitative"),
        color=alt.Color(field="BoroName", type="nominal"),
        tooltip=[alt.Tooltip('BoroName:N', title='Borough'), alt.Tooltip('count:N', title='Count'),
                 alt.Tooltip('percentage:Q', title='Percentage', format='.2f')]
    ).properties(
        title=f'Pie Chart of Property Count by BoroName - {type_viz}',
        width=200,
        height=200
    )

    # Combine the boxplot and pie chart into a single visualization
    combined_chart = alt.hconcat(boxplot, pie_chart).resolve_scale(color='independent')

    return combined_chart.to_html()


# Define the callback function to update charts
@app.callback(
    Output('chart_container', 'children'),
    [Input('type_viz_dropdown', 'value')]
)
def update_charts(type_viz):
    chart_html = create_charts(joined_data, type_viz)
    return html.Iframe(srcDoc=chart_html, style={'width': '100%', 'height': '500px', 'border-width': '0'})


# Create Map filters
# create sublocaility filter
NewYork = joined_data
mapbox_access_token = mapbox_key

sub_locality = NewYork["BoroName"].unique()
dropdown_options_sub_locality = [{'label': value, 'value': value} for value in sub_locality]

filter_region = dcc.Dropdown(
    id='filter_sublocality',
    options=dropdown_options_sub_locality,
    placeholder='Select a locality...',
    # value=sub_locality[0],
    # clearable=False,
    style={'width': '200px'}
)

# create type filter
type_viz = NewYork["TYPE_VIZ"].unique()
dropdown_options_type_viz = [{'label': value, 'value': value} for value in type_viz]

filter_type = dcc.Dropdown(
    id='filter_typeviz',
    options=dropdown_options_type_viz,
    placeholder='Select a type...',
    style={'width': '200px'}
)

price_slider = dcc.RangeSlider(
    id='price-slider',
    min=NewYork['PRICE'].min(),
    max=min(NewYork['PRICE'].max(), 5000000),
    step=500000,
    value=[NewYork['PRICE'].min(), min(NewYork['PRICE'].max(), 1000000)],  # Default value range
    marks={i * 500000: f'{i * 0.5}M' if i < 10 else '5M+' for i in range(NewYork['PRICE'].min() // 500000,
                                                                         min(NewYork['PRICE'].max() // 500000 + 1,
                                                                             10000000 // 500000))},
)
price_slider_style = {'width': '400px'}

# create Plotly Graph Objects
fig = go.Figure(go.Scattermapbox(
    lat=NewYork['LATITUDE'],
    lon=NewYork['LONGITUDE'],
    mode='markers',
    marker=dict(
        # size=9,
        size=np.log(NewYork["PROPERTYSQFT"] + 1) * 1.7,
        color=NewYork["PRICE"],
        colorscale='Viridis',
        colorbar=dict(title="PRICE"),
    ),
    text=NewYork[['ADDRESS', "PRICE", 'PROPERTYSQFT', "BROKERTITLE", "BEDS", "BATH"]].apply(
        lambda
            x: f"Address: {x['ADDRESS']}</span><br>Price: ${x['PRICE']}<br>House Area: {x['PROPERTYSQFT']} sqft<br>Broker: {x['BROKERTITLE'].replace('Brokered by ', '')}<br>Beds: {int(x['BEDS'])}<br>Bath: {int(x['BATH'])}",
        axis=1
    ),
    hoverinfo='text'
))

# inialize map
fig.update_layout(
    mapbox=dict(
        accesstoken=mapbox_access_token,
        style='light',
        zoom=10,
        center=dict(lat=NewYork['LATITUDE'].mean(), lon=NewYork['LONGITUDE'].mean())
    ),
    margin={"r": 0, "t": 0, "l": 0, "b": 0},
    width=600,
    height=350
)


@app.callback(
    Output('map-graph', 'figure'),
    [Input('filter_sublocality', 'value'),
     Input("filter_typeviz", "value"),
     Input("price-slider", "value")]
)
def update_map(selected_sublocality, selected_type, price_range):
    filtered_data = NewYork

    # filter house with locality
    if selected_sublocality:
        filtered_data = filtered_data[filtered_data['BoroName'] == selected_sublocality]

    # filter house with house type
    if selected_type:
        filtered_data = filtered_data[filtered_data['TYPE_VIZ'] == selected_type]

    # filter house with price
    if price_range:
        filtered_data = filtered_data[
            (filtered_data['PRICE'] >= price_range[0]) & (filtered_data['PRICE'] <= price_range[1])]

    # renew data
    fig = go.Figure(go.Scattermapbox(
        lat=filtered_data['LATITUDE'],
        lon=filtered_data['LONGITUDE'],
        mode='markers',
        marker=dict(
            # size=12,
            size=np.log(filtered_data["PROPERTYSQFT"]) * 1.7,
            color=filtered_data["PRICE"],
            colorscale='Viridis',
            colorbar=dict(title="PRICE"),
            opacity=0.5
        ),
        text=filtered_data[['ADDRESS', "PRICE", 'PROPERTYSQFT', "BROKERTITLE", "BEDS", "BATH"]].apply(
            lambda
                x: f"Address: {x['ADDRESS']}</span><br>Price: ${x['PRICE']}<br>House Area: {x['PROPERTYSQFT']} sqft<br>Broker: {x['BROKERTITLE'].replace('Brokered by ', '')}<br>Beds: {int(x['BEDS'])}<br>Bath: {int(x['BATH'])}",
            axis=1
        ),

        hoverinfo='text'

    ))

    # update map
    fig.update_layout(
        mapbox=dict(
            accesstoken=mapbox_access_token,
            style='light',
            zoom=10,
            center=dict(lat=filtered_data['LATITUDE'].mean(), lon=filtered_data['LONGITUDE'].mean())
        ),
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        width=600,
        height=350
    )
    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
