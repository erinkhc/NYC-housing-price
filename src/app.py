import pandas as pd
import requests
import geopandas as gpd
from shapely.geometry import Point
import dash
from dash import Dash, dcc, html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
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
data_dir = os.path.join(parent_dir, "data")
geojson_file = os.path.join(data_dir, "NYC_Borough_Boundary.geojson")
csv_file = os.path.join(data_dir, "NewYork_add_all.csv")

# load data
nyc_boroughs = gpd.read_file(geojson_file)
joined_data = pd.read_csv(csv_file)


# mapbox API key
mapbox_key = "pk.eyJ1IjoibWFudHVvbHVvYnVrdSIsImEiOiJjbHQ4OGJuaGowOXpuMmlvNHRxMjhwcjNwIn0.Ah-KdY3j7V0mm_86NfIJfg"

# google map API key
google_maps_api_key = "AIzaSyAfJnHO3vlmdTQdGEGBEUZXojhrQFqVjW8"

# calculate average price
average_prices = joined_data.groupby("BoroName")["PRICE"].mean().reset_index()
average_prices.columns = ["BoroName", "AveragePrice"]

# merge to nyc_boroughs_with_prices
nyc_boroughs_with_prices = nyc_boroughs.merge(average_prices, on="BoroName")
nyc_boroughs_with_prices["AveragePriceInMillions"] = (
    nyc_boroughs_with_prices["AveragePrice"] / 1000000
)
nyc_boroughs_with_prices["AveragePriceInMillions"] = nyc_boroughs_with_prices[
    "AveragePriceInMillions"
].round(2)

# group by both boro and type
grouped_data = (
    joined_data.groupby(["BoroName", "TYPE_VIZ"])["PRICE"]
    .agg(["mean", "count"])
    .reset_index()
)
grouped_data.columns = ["BoroName", "TYPE_VIZ", "AveragePrice", "Count"]

broker_count = (
    joined_data.groupby(["BoroName", "BROKERTITLE"])
    .size()
    .reset_index(name="Transactions")
)
top_brokers_per_boro = broker_count.groupby("BoroName").apply(
    lambda x: x.sort_values("Transactions", ascending=False).head(5)
)
top_brokers_per_boro["BROKERTITLE"] = top_brokers_per_boro["BROKERTITLE"].str.replace(
    "Brokered by ", "", regex=False
)

# Reset the index to make the DataFrame tidy
top_brokers_per_boro.reset_index(drop=True, inplace=True)
top_brokers_per_boro.head(20)

top_brokers_nyc = joined_data["BROKERTITLE"].value_counts().head(5).reset_index()
top_brokers_nyc.columns = ["BROKERTITLE", "Transactions"]

top_brokers_nyc["BROKERTITLE"] = top_brokers_nyc["BROKERTITLE"].str.replace(
    "Brokered by ", "", regex=False
)


top_brokers_nyc["BoroName"] = "All"

top_brokers_combined = pd.concat(
    [top_brokers_per_boro, top_brokers_nyc], ignore_index=True
)
top_brokers_combined.reset_index(drop=True, inplace=True)


overall_broker = top_brokers_combined[top_brokers_combined["BoroName"] == "All"]

overall_broker = top_brokers_combined[top_brokers_combined["BoroName"] == "All"]

# Initialize Dash app with Bootstrap CSS
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True,
)

# Declare server for Heroku deployment. Needed for Procfile.
server = app.server

border_style = {
    "borderRadius": "5px",
    "boxShadow": "2px 2px 5px rgba(0, 0, 0, 0.1)",  # a lighter color
    "margin": "10px",
    "border": "1px solid #eeeeee",
}

app.layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H4(
                            "Categories",
                            style={
                                "textAlign": "center",
                                "margin-top": "40px",
                                "fontWeight": "bold",
                                "color": "#007bff",
                            },
                        ),
                        html.P(
                            "Explore comprehensive analytics on housing prices across New York's diverse neighborhoods.",
                            style={
                                "textAlign": "justified",
                                "color": "#5DADE2",
                                "margin-bottom": "20px",
                            },
                        ),
                        dbc.Tabs(
                            [
                                dbc.Tab(label="Map", tab_id="tab-1"),
                                dbc.Tab(label="By Types", tab_id="tab-2"),
                                dbc.Tab(label="By Regions", tab_id="tab-3"),
                            ],
                            id="tabs",
                            active_tab="tab-1",
                            #vertical=True,
                            #style={'width': '100%'}
                            className="vertical-tabs"

                        ),
                    ],
                    width=2,
                    style={
                        "height": "100vh",
                        "backgroundColor": "#f8f9fa",
                        "overflowY": "scroll",
                    },
                ),
                dbc.Col(
                    [
                        html.Div(
                            [
                                html.H1(
                                    "Welcome to New York Housing Market",
                                    style={
                                        "textAlign": "center",
                                        "margin-top": "20px",
                                        "fontWeight": "bold",
                                        "color": "#007bff",
                                    },
                                ),
                                html.Div(
                                    id="top-bar",
                                    style={
                                        "textAlign": "center",
                                        "margin": "10px 0",
                                        "fontWeight": "bold",
                                        "fontSize": "20px",
                                        "color": "#007bff",
                                    },
                                ),
                            ]
                        ),
                        html.Div(id="tabs-content"),
                    ],
                    width=10,
                ),
            ]
        )
    ],
    fluid=True,
)


@app.callback(
    [Output("tabs-content", "children"), Output("top-bar", "children")],
    [Input("tabs", "active_tab")],
)
def render_tab_content(active_tab):
    if active_tab == "tab-1":
        top_bar_content = "House Section"
        tab_content = html.Div(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            html.Div([dcc.Graph(id="map-graph", figure=fig)]),
                            width=12, lg=8,
                            #style={'height': '150vh'},
                            #style={'height': '5000px'}


                        ),
                        dbc.Col(
                            [
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            [
                                                html.Label("Select house locality:",
                                                           style={'font-size': '18px',
                                                                  'font-weight': 'bold',
                                                                  'color': '#2D5FF1',
                                                                  'margin-left': '5px',
                                                                  'margin-bottom': '10px'}),
                                                filter_region,
                                            ],
                                            style={'marginRight': '0px'},
                                            width=6,  # half width
                                        ),
                                        dbc.Col(
                                            [
                                                html.Label("Select house type:",
                                                           style={'font-size': '18px',
                                                                  'font-weight': 'bold',
                                                                  'color': '#2D5FF1',
                                                                  'margin-left': '5px',
                                                                  'margin-bottom': '10px'}),
                                                filter_type,
                                            ],
                                            style={'marginLeft': '0px'},
                                            width=6,  # half width
                                        ),
                                    ],
                                    className="d-flex flex-row justify-content-between",  #horizontal flex
                                    style={'margin-top': '20px'},
                                ),




                                html.Div(style={'height': '15px'}),
                                #html.Label("Select price range:"),
                                html.Label("Select price range:",
                                           style={'font-size': '18px',
                                                  'font-weight': 'bold',
                                                  'color': '#2D5FF1',
                                                  'margin-left': '10px'}),
                                html.Div(style={'height': '15px'}),
                                #dbc.Row(price_slider, style=price_slider_style),
                                dbc.Row(
                                    dbc.Col(price_slider, width=12),
                                ),
                                html.Div(style={'height': '15px'}),

                                html.Div(id='click-info', children=default_content),


                                html.Button('Close Nearby Information', id='clear-button', n_clicks=0,
                                            className='btn btn-primary btn-sm',
                                            style={'display': 'none'}
                                            )

                            ],
                            width=12, lg=4,
                            style={'height': 'auto', 'margin-left': '0px'},
                        ),

                    ],
                    className="mb-4 g-0",
                ),
                
                
            ],
            style = {'margin': '20px'}
        )
    elif active_tab == "tab-3":
        top_bar_content = "Region Section: Detailed Information"
        tab_content = dbc.Container(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            dcc.Graph(
                                id="nyc-map",
                                figure={},
                                style={"height": "60vh", **border_style},
                            ),
                            md=6,
                        ),
                        dbc.Col(
                            dcc.Graph(
                                id="bubble-chart",
                                figure={},
                                style={"height": "42vh", **border_style},
                            ),
                            md=6,
                        ),
                    ]
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.Label("Number of Bedrooms:"),
                                dcc.Dropdown(
                                    id="num-bedrooms-dropdown",
                                    options=[{"label": "Any", "value": "any"}]
                                    + [
                                        {"label": str(i), "value": i}
                                        for i in range(1, 6)
                                    ]
                                    + [{"label": "5+", "value": "5+"}],
                                    value="any",
                                ),
                                html.Label("Number of Bathrooms:"),
                                dcc.Dropdown(
                                    id="num-bathrooms-dropdown",
                                    options=[{"label": "Any", "value": "any"}]
                                    + [
                                        {"label": str(i), "value": i}
                                        for i in range(1, 6)
                                    ]
                                    + [{"label": "5+", "value": "5+"}],
                                    value="any",
                                ),
                                html.Div(
                                    id="price-range-display",
                                    children="Select an area and set filters to see price range",
                                    style={
                                        "border": "1px solid #ddd",
                                        "padding": "10px",
                                        "margin-top": "10px",
                                        "margin-bottom": "10px",
                                        "border-radius": "5px",
                                        "background-color": "#f9f9f9",
                                    },
                                ),
                            ],
                            md=6,
                            style={"transform": "translateY(-120px)"},
                        ),
                        dbc.Col(
                            dcc.Graph(
                                id="broker-histogram",
                                figure={},
                                style={
                                    "height": "42vh",
                                    **border_style,
                                    "transform": "translateY(-120px)",
                                },
                            ),
                            md=6,
                        ),
                        # put broker-histogram at right side
                    ],
                    align="end",
                ),
            ],
            fluid=True,
            style={"backgroundColor": "#f8f9fa", "height": "auto", "width": "auto"},
        )  # 'height': 'calc(100vh - 56px)'
    elif active_tab == "tab-2":
        top_bar_content = "Type Section"
        tab_content = html.Div(
            [
               
                dbc.Col(
                    [
                        html.Label("Select house type:"),
                        dcc.Dropdown(
                            id="type_viz_dropdown",
                            options=[
                                {"label": i, "value": i}
                                for i in sorted(joined_data["TYPE_VIZ"].unique())
                            ]
                            + [{"label": "All", "value": "All"}],
                            value="All",  # Default value
                            placeholder="Select a type...",  # This sets the placeholder text
                            clearable=False,
                        ),
                        html.Br(),
                        html.Div(id="chart_container"),
                    ]
                ),
            ]
        )
    return tab_content, top_bar_content


@app.callback(
    [
        Output("nyc-map", "figure"),
        Output("bubble-chart", "figure"),
        Output("broker-histogram", "figure"),
        Output("price-range-display", "children"),
    ],
    [
        Input("nyc-map", "clickData"),
        Input("num-bedrooms-dropdown", "value"),
        Input("num-bathrooms-dropdown", "value"),
    ],
)
#     return fig_map, fig_bubble, fig_histogram, price_range_text
def update_content(clickData, num_bedrooms, num_bathrooms):
    price_range_text = "Select an area and set filters to see price range"
    # Placeholder for updated opacities
    opacities = [0.5 if not clickData else 0.2 for _ in nyc_boroughs_with_prices.index]

    if clickData:
        clicked_boro = clickData["points"][0]["customdata"][0]
        opacities = [
            0.5 if boro == clicked_boro else 0.2
            for boro in nyc_boroughs_with_prices["BoroName"]
        ]
        if num_bedrooms == "5+":
            filtered_data_prices = joined_data[
                (joined_data["BEDS"] >= 5) & (joined_data["BoroName"] == clicked_boro)
            ]
        elif num_bedrooms != "any":
            filtered_data_prices = joined_data[
                (joined_data["BEDS"] == num_bedrooms)
                & (joined_data["BoroName"] == clicked_boro)
            ]
        else:
            # If 'any' is selected, include all data for the clicked borough
            filtered_data_prices = joined_data[joined_data["BoroName"] == clicked_boro]

        if num_bathrooms == "5+":
            filtered_data_prices = filtered_data_prices[
                filtered_data_prices["BATH"] >= 5
            ]
        elif num_bathrooms != "any":
            filtered_data_prices = filtered_data_prices[
                filtered_data_prices["BATH"] == num_bathrooms
            ]
        # Calculate the price range
        min_price = filtered_data_prices["PRICE"].min()
        max_price = filtered_data_prices["PRICE"].max()
        price_range_text = (
            f"Price Range: ${min_price:,.0f} - ${max_price:,.0f}"
            if not filtered_data_prices.empty
            else "No data for selected filters"
        )

    fig = px.choropleth_mapbox(
        nyc_boroughs_with_prices,
        geojson=nyc_boroughs_with_prices.geometry,
        locations=nyc_boroughs_with_prices.index,
        color="AveragePrice",
        color_continuous_scale=px.colors.sequential.Viridis,
        mapbox_style="carto-positron",
        zoom=9,
        center={"lat": 40.730610, "lon": -73.935242},
        opacity=opacities,
        custom_data=["BoroName"],
        hover_data={"BoroName": True, "AveragePriceInMillions": ":.2f"},
    )
    fig.update_layout(clickmode="event+select")
    fig.update_traces(
        hovertemplate="Borough Name: %{customdata[0]}<br>Average Price: $%{customdata[1]} Million <br>"
    )

    fig.update_layout(
        mapbox_zoom=9, mapbox_center={"lat": 40.730610, "lon": -73.935242}
    )
    fig.update_layout(margin={"r": 3, "t": 3, "l": 3, "b": 3})
    fig.update_layout(coloraxis_colorbar=dict(thickness=10, title_font_size=10))

    # Update bubble chart based on clickData
    # Placeholder for bubble chart logic
    if not clickData:
        overall_avg_price_count = (
            joined_data.groupby("TYPE_VIZ")["PRICE"]
            .agg(["mean", "count"])
            .reset_index()
        )
        overall_avg_price_count.columns = ["TYPE_VIZ", "AveragePrice", "Count"]
        bubble_fig = px.scatter(
            overall_avg_price_count,
            x="TYPE_VIZ",
            y="AveragePrice",
            size="Count",
            color="TYPE_VIZ",
            hover_name="TYPE_VIZ",
            size_max=45,
            title="Overall Properties in NYC",
        )
        hist_fig = px.bar(
            overall_broker,
            x="Transactions",
            y="BROKERTITLE",
            color="BoroName",
            title=f"Top 5 Brokers in NYC",
            labels={"BROKERTITLE": "Broker", "Transactions": "Transaction Count"},
        )
    else:
        boro_name = clicked_boro
        filtered_data = grouped_data[grouped_data["BoroName"] == boro_name]
        bubble_fig = px.scatter(
            filtered_data,
            x="TYPE_VIZ",
            y="AveragePrice",
            size="Count",
            color="TYPE_VIZ",
            hover_name="TYPE_VIZ",
            size_max=45,
            title=f"Properties in {boro_name}",
        )
        filtered_data_broker = top_brokers_per_boro[
            top_brokers_combined["BoroName"] == boro_name
        ]
        hist_fig = px.bar(
            filtered_data_broker,
            x="Transactions",
            y="BROKERTITLE",
            color="BoroName",
            title=f"Top 5 Brokers in {boro_name}",
            labels={"BROKERTITLE": "Broker", "Transactions": "Transaction Count"},
        )

    # bubble_fig = px.scatter()  # Update this with actual data
    # bubble_fig.update_layout(title_text='Property Analysis', title_font_size=16)
    bubble_fig.update_traces(selector=dict(mode="markers"), showlegend=False)
    bubble_fig.update_layout(hoverlabel=dict(namelength=-1))
    bubble_fig.update_layout(
        margin={"r": 20, "t": 38, "l": 3, "b": 3},
        xaxis_title="",
        xaxis_tickangle=0,
        xaxis_tickfont=dict(size=11),
        yaxis_title_font=dict(size=15),
    )
    bubble_fig.update_traces(
        hovertemplate="Property Number: %{marker.size}<br>Average Price: %{y}",
        showlegend=False,
    )

    hist_fig.update_layout(barmode="group", xaxis={"categoryorder": "total descending"})
    hist_fig.update_layout(margin={"r": 0, "t": 30, "l": 0, "b": 0})
    hist_fig.update_layout(showlegend=False)

    return fig, bubble_fig, hist_fig, price_range_text


# Define the function to create the charts
def create_charts(data, type_viz):
    if type_viz == "All":
        # If "All" is selected, use the entire dataset
        data_type_filtered = data.copy()
    else:
        # Otherwise, filter based on the selected TYPE_VIZ
        data_type_filtered = data[data["TYPE_VIZ"] == type_viz]

    # Here you may calculate aggregations or transformations as needed
    # For example, calculating price per square foot for each row
    data_type_filtered["PRICE_PER_SQFT"] = (
        data_type_filtered["PRICE"] / data_type_filtered["PROPERTYSQFT"]
    )

    # Define the color scheme for the Boroughs
    # Define the color scheme for the Boroughs with 70% opacity
    boro_colors = [
        "rgba(224, 138, 122, 1)",  # e08a7a with 70% opacity
        "rgba(133, 211, 180, 1)",  # 85d3b4 with 70% opacity
        "rgba(182, 142, 243, 1)",  # b68ef3 with 70% opacity
        "rgba(238, 178, 145, 1)",  # eeb291 with 70% opacity
        "rgba(138, 216, 240, 1)",  # 8ad8f0 with 70% opacity
    ]

    # Create a boxplot of price per square foot by BoroName
    boxplot = (
        alt.Chart(data_type_filtered)
        .transform_filter(alt.datum.PRICE_PER_SQFT <= 20000)  # Filter condition
        .mark_boxplot()
        .encode(
            x=alt.X(
                "PRICE_PER_SQFT:Q",
                title="Price Per Square Foot (USD)",
                scale=alt.Scale(domain=[0, 20000]),
            ),
            y=alt.Y("BoroName:N", title="Region"),
            color=alt.Color(
                "BoroName:N", legend=None, scale=alt.Scale(range=boro_colors)
            ),
            tooltip=[
                alt.Tooltip("PRICE_PER_SQFT:Q", title="Price Per Square Foot (USD)"),
                alt.Tooltip("BoroName:N", title="Region"),
            ],
        )
        .properties(
            title=f"Price per Square Foot by Region - {type_viz}", width=600, height=300
        )
    )

    # Create a pie chart of property count by BoroName for the selected type of visualization
    pie_chart_data = data_type_filtered["BoroName"].value_counts().reset_index()
    pie_chart_data.columns = ["BoroName", "count"]
    total_count = pie_chart_data["count"].sum()
    pie_chart_data["percentage"] = (pie_chart_data["count"] / total_count * 100).round(
        2
    )

    pie_chart = (
        alt.Chart(pie_chart_data)
        .mark_arc()
        .encode(
            theta=alt.Theta(field="count", type="quantitative"),
            color=alt.Color(
                field="BoroName",
                type="nominal",
                scale=alt.Scale(range=boro_colors),
                legend=alt.Legend(title="Region"),
            ),
            tooltip=[
                alt.Tooltip("BoroName:N", title="Region"),
                alt.Tooltip("count:N", title="Count"),
                alt.Tooltip("percentage:Q", title="Percentage", format=".2f"),
            ],
        )
        .properties(
            title=f"Property Count by Region - {type_viz}", width=300, height=300
        )
    )

    # Combine the boxplot and pie chart into a single visualization
    combined_chart = alt.hconcat(boxplot, pie_chart).resolve_scale(color="independent")

    return combined_chart.to_html()


# Define the callback function to update charts
@app.callback(
    Output("chart_container", "children"), [Input("type_viz_dropdown", "value")]
)
def update_charts(type_viz):
    chart_html = create_charts(joined_data, type_viz)
    return html.Iframe(
        srcDoc=chart_html,
        style={"width": "100%", "height": "500px", "border-width": "0"},
    )


# Create Map filters
# create sublocaility filter
NewYork = joined_data
mapbox_access_token = mapbox_key

sub_locality = NewYork["BoroName"].unique()
dropdown_options_sub_locality = [
    {"label": value, "value": value} for value in sub_locality
]

filter_region = dcc.Dropdown(
    id="filter_sublocality",
    options=dropdown_options_sub_locality,
    placeholder="Select a locality...",
    # value=sub_locality[0],
    # clearable=False,
    #style={"width": "150px"},
)

# create type filter
type_viz = NewYork["TYPE_VIZ"].unique()
dropdown_options_type_viz = [{"label": value, "value": value} for value in type_viz]

filter_type = dcc.Dropdown(
    id="filter_typeviz",
    options=dropdown_options_type_viz,
    placeholder="Select a type...",
    #style={"width": "150px"},
)

price_slider = dcc.RangeSlider(
    id="price-slider",
    min=NewYork["PRICE"].min(),
    max=min(NewYork["PRICE"].max(), 5000000),
    step=500000,
    value=[
        NewYork["PRICE"].min(),
        min(NewYork["PRICE"].max(), 1000000),
    ],  # Default value range
    marks={
        i * 500000: f"{i * 0.5}M" if i < 10 else "5M+"
        for i in range(
            NewYork["PRICE"].min() // 500000,
            min(NewYork["PRICE"].max() // 500000 + 1, 10000000 // 500000),
        )
    },
)
price_slider_style = {"width": "400px"}

# create Plotly Graph Objects
fig = go.Figure(
    go.Scattermapbox(
        lat=NewYork["LATITUDE"],
        lon=NewYork["LONGITUDE"],
        mode="markers",
        marker=dict(
            # size=9,
            size=np.log(NewYork["PROPERTYSQFT"] + 1) * 1.7,
            color=NewYork["PRICE"],
            colorscale="Viridis",
            colorbar=dict(title="PRICE"),
        ),
        text=NewYork[
            ["ADDRESS", "PRICE", "PROPERTYSQFT", "BROKERTITLE", "BEDS", "BATH"]
        ].apply(
            lambda x: f"Address: {x['ADDRESS']}</span><br>Price: ${x['PRICE']}<br>House Area: {x['PROPERTYSQFT']} sqft<br>Broker: {x['BROKERTITLE'].replace('Brokered by ', '')}<br>Beds: {int(x['BEDS'])}<br>Bath: {int(x['BATH'])}",
            axis=1,
        ),
        hoverinfo="text",
    )
)

# create google info layout

default_content = html.Div([
    html.H4('Please click map for more nearby information.',
            style={'fontSize': '22px', 'color': '#2D5FF1', 'fontWeight': 'bold', 'text-align': 'center', 'margin-top': '20px'}),
    html.Img(src='/assets/NYC_label.png', style={'width': '60%', 'max-width': '400px', 'margin-top': '5px', 'display': 'block', 'margin-left': 'auto', 'margin-right': 'auto'})
], style={'text-align': 'center'})



def get_address(lat, lon):
    matched_row = NewYork[(NewYork["LATITUDE"] == lat) & (NewYork["LONGITUDE"] == lon)]
    if not matched_row.empty:
        return matched_row.iloc[0]["MAIN_ADDRESS"]
    else:
        return "Address not found"
def print_address(lat, lon):
    address = get_address(lat, lon)
    return html.Div([
        html.Div([
            html.Img(src='/assets/map_marker.png',
                     style={'height': '25px', 'width': '25px', 'marginRight': '10px'}),
            html.P(f'{address}', style={'margin': '0'})
        ], style={'display': 'flex', 'alignItems': 'center'})
    ], style={'padding': '10px'})


@app.callback(
    [Output('click-info', 'children'),
     Output('clear-button', 'style')],
    [Input('map-graph', 'clickData'),
     Input('clear-button', 'n_clicks')],
    prevent_initial_call=True
)
def display_click_data(clickData, clear_clicks):
    ctx = dash.callback_context

    if not ctx.triggered:
        raise PreventUpdate

    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if triggered_id == 'map-graph' and clickData is not None:
        lat = clickData['points'][0]['lat']
        lon = clickData['points'][0]['lon']

        address_info = print_address(lat, lon)

        hospital_results = query_nearest_hospital(lat, lon)
        if hospital_results:
            hospital_name = hospital_results[0]['name']
            hospital_lat = hospital_results[0]['geometry']['location']['lat']
            hospital_lon = hospital_results[0]['geometry']['location']['lng']
            hospital_info = display_hospital_info(hospital_name, lat, lon, hospital_lat, hospital_lon)
        else:
            hospital_info = html.P('No hospitals found within 7km.')

        lat,lon,park_name, park_lat, park_lon = query_nearest_park(lat, lon)
        if park_name:
            park_info = display_park_info(lat, lon)
        else:
            park_info = html.P('No parks found within 2km.')

        lat,lon,shopping_center_name, shopping_center_lat, shopping_center_lon = query_nearest_shopping_center(lat, lon)
        if shopping_center_name:
            shopping_center_info = display_shopping_center_info(lat,lon)
        else:
            shopping_center_info = html.P('No shopping center found nearby.')

        clear_button_style = {'display': 'block'}

        return html.Div([
            html.Div(address_info, style={'margin-left': '25px', 'margin-top': '5px', 'margin-bottom': '5px','margin-right': '25px'}),
            html.Div(hospital_info, style={'margin-left': '25px', 'margin-top': '5px', 'margin-bottom': '5px','margin-right': '25px'}),
            html.Div(park_info, style={'margin-left': '25px', 'margin-top': '5px', 'margin-bottom': '5px','margin-right': '25px'}),
            html.Div(shopping_center_info, style={'margin-left': '25px', 'margin-top': '5px', 'margin-bottom': '5px','margin-right': '25px'}),
        ], style={
            'padding': '5px',
            'background-color': '#f7f8f9',
            'border-radius': '20px',
            'display': 'inline-block',
            'vertical-align': 'top'
        }), clear_button_style




    elif triggered_id == 'clear-button':
        return default_content, {'display': 'none'}

    raise PreventUpdate















## nearby hostipal

def query_nearest_hospital(lat, lon):
    # Places API requests URL
    places_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    places_params = {
        'location': f'{lat},{lon}',
        'radius': 7000,  # radius(m)
        'type': 'hospital',
        'key': google_maps_api_key
    }

    # Places API request
    places_response = requests.get(places_url, params=places_params)
    if places_response.status_code == 200:
        hospital_results = places_response.json()['results']
        return hospital_results

def display_hospital_info(hospital_name, lat, lon, hospital_lat, hospital_lon):
    # Directions API URL
    directions_url = "https://maps.googleapis.com/maps/api/directions/json"
    directions_params = {
        'origin': f'{lat},{lon}',
        'destination': f'{hospital_lat},{hospital_lon}',
        'mode': 'driving',
        'key': google_maps_api_key
    }

    # Directions API request
    directions_response = requests.get(directions_url, params=directions_params)
    if directions_response.status_code == 200:
        directions_results = directions_response.json()['routes'][0]['legs'][0]
        distance = directions_results['distance']['text']
        duration = directions_results['duration']['text']

        return html.Div([
            html.Div([
                html.Img(src='/assets/hospital_label.png',
                         style={'height': '25px', 'width': '25px', 'marginRight': '10px'}),
                html.P(f'{hospital_name}', style={'margin': '0'})
            ], style={'display': 'flex', 'alignItems': 'center'}),
            html.P(f'Driving: {distance}, {duration}',style={'font-size': '14px'})
        ], style={'padding': '10px'})

    else:
        return f'Failed to retrieve data from Google Directions API. Status code: {directions_response.status_code}'

## display nearby park

def query_nearest_park(lat, lon):
    # Places API URL
    places_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    places_params = {
        'location': f'{lat},{lon}',
        'radius': 2000,
        'type': 'park|square',
        'keyword': 'community garden | playground',
        'key': google_maps_api_key
    }

    places_response = requests.get(places_url, params=places_params)
    if places_response.status_code == 200:
        park_results = places_response.json()['results']
        if park_results:
            first_park = park_results[0]
            park_name = first_park['name']
            park_lat = first_park['geometry']['location']['lat']
            park_lon = first_park['geometry']['location']['lng']
            return lat, lon, park_name, park_lat, park_lon
    return None, None, None, None, None

def display_park_info(lat, lon):
    lat,lon, park_name, park_lat, park_lon = query_nearest_park(lat, lon)
    if park_name:
        # Directions API URL
        directions_url = "https://maps.googleapis.com/maps/api/directions/json"
        directions_params = {
            'origin': f'{lat},{lon}',
            'destination': f'{park_lat},{park_lon}',
            'mode': 'walking',
            'key': google_maps_api_key
        }


        directions_response = requests.get(directions_url, params=directions_params)
        if directions_response.status_code == 200:
            directions_results = directions_response.json()['routes'][0]['legs'][0]
            distance = directions_results['distance']['text']
            duration = directions_results['duration']['text']

            return html.Div([
                html.Div([
                    html.Img(src='/assets/parks_label.png',
                             style={'height': '25px', 'width': '25px', 'marginRight': '10px'}),
                    html.P(f'{park_name}', style={'margin': '0'})
                ], style={'display': 'flex', 'alignItems': 'center'}),
                html.P(f'Walking: {distance}, {duration}',style={'font-size': '14px'}),
            ], style={'padding': '10px'})

        else:
            return f'Failed to retrieve data from Google Directions API. Status code: {directions_response.status_code}'
    else:
        return 'No nearby park found.'


def query_nearest_shopping_center(lat, lon):

    places_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    places_params = {
        'location': f'{lat},{lon}',
        'radius': 5000,
        'type': 'shopping_mall',
        'key': google_maps_api_key
    }

    places_response = requests.get(places_url, params=places_params)
    if places_response.status_code == 200:
        shopping_center_results = places_response.json()['results']
        if shopping_center_results:
            first_shopping_center = shopping_center_results[0]
            #print(first_shopping_center)
            shopping_center_name = first_shopping_center['name']
            shopping_center_lat = first_shopping_center['geometry']['location']['lat']
            shopping_center_lon = first_shopping_center['geometry']['location']['lng']
            return lat,lon,shopping_center_name, shopping_center_lat, shopping_center_lon
    return None, None, None,None,None

def display_shopping_center_info(lat, lon):
    lat,lon,shopping_center_name, shopping_center_lat, shopping_center_lon = query_nearest_shopping_center(lat, lon)

    if shopping_center_name:
        # Directions API URL
        directions_url = "https://maps.googleapis.com/maps/api/directions/json"
        directions_params = {
            'origin': f'{lat},{lon}',
            'destination': f'{shopping_center_lat},{shopping_center_lon}',
            'mode': 'driving',
            'key': google_maps_api_key
        }

        directions_response = requests.get(directions_url, params=directions_params)
        if directions_response.status_code == 200:
            directions_results = directions_response.json()['routes'][0]['legs'][0]
            distance = directions_results['distance']['text']
            duration = directions_results['duration']['text']

            return html.Div([
                html.Div([
                    html.Img(src='/assets/shopping_center_label.jpg',
                             style={'height': '25px', 'width': '25px', 'marginRight': '10px'}),
                    html.P(f'{shopping_center_name}', style={'margin': '0'})
                ], style={'display': 'flex', 'alignItems': 'center'}),
                html.P(f'Driving: {distance}, {duration}',style={'font-size': '14px'}),
            ], style={'padding': '10px'})

        else:
            return f'Failed to retrieve data from Google Directions API. Status code: {directions_response.status_code}'
    else:
        return 'No nearby shopping center found.'










# inialize map
fig.update_layout(
    mapbox=dict(
        accesstoken=mapbox_access_token,
        style="light",
        zoom=9.5,
        #zoom = 10,
        center=dict(lat=NewYork["LATITUDE"].mean(), lon=NewYork["LONGITUDE"].mean()),
    ),
    margin={"r": 0, "t": 0, "l": 0, "b": 0},
    height = 550
)


@app.callback(
    Output("map-graph", "figure"),
    [
        Input("filter_sublocality", "value"),
        Input("filter_typeviz", "value"),
        Input("price-slider", "value"),
    ],
)
def update_map(selected_sublocality, selected_type, price_range):
    filtered_data = NewYork

    # filter house with locality
    if selected_sublocality:
        filtered_data = filtered_data[filtered_data["BoroName"] == selected_sublocality]

    # filter house with house type
    if selected_type:
        filtered_data = filtered_data[filtered_data["TYPE_VIZ"] == selected_type]

    # filter house with price
    if price_range:
        filtered_data = filtered_data[
            (filtered_data["PRICE"] >= price_range[0])
            & (filtered_data["PRICE"] <= price_range[1])
        ]

    # renew data
    fig = go.Figure(
        go.Scattermapbox(
            lat=filtered_data["LATITUDE"],
            lon=filtered_data["LONGITUDE"],
            mode="markers",
            marker=dict(
                # size=12,
                size=np.log(filtered_data["PROPERTYSQFT"]) * 1.7,
                color=filtered_data["PRICE"],
                colorscale="Viridis",
                colorbar=dict(title="PRICE"),
                opacity=0.5,
            ),
            text=filtered_data[
                ["ADDRESS", "PRICE", "PROPERTYSQFT", "BROKERTITLE", "BEDS", "BATH"]
            ].apply(
                lambda x: f"Address: {x['ADDRESS']}</span><br>Price: ${x['PRICE']}<br>House Area: {x['PROPERTYSQFT']} sqft<br>Broker: {x['BROKERTITLE'].replace('Brokered by ', '')}<br>Beds: {int(x['BEDS'])}<br>Bath: {int(x['BATH'])}",
                axis=1,
            ),
            hoverinfo="text",
        )
    )

    # update map
    fig.update_layout(
        mapbox=dict(
            accesstoken=mapbox_access_token,
            style="light",
            zoom=9.5,
            #zoom = 10
            center=dict(
                lat=filtered_data["LATITUDE"].mean(),
                lon=filtered_data["LONGITUDE"].mean(),
            ),
        ),
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        height = 550
    )
    return fig


if __name__ == "__main__":
    app.run_server(debug=True)
