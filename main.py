import dash
from dash import dcc, html, dash_table
import dash_bootstrap_components as dbc
import pandas as pd

import plotly.express as px

# Import data
sales = pd.read_csv("sales.csv")
product_info = pd.read_csv("product_info.csv")

# Merge tables into one
orders = pd.merge(sales, product_info)
total_orders = ""

# Create pie chart
bar_chart = px.bar(
    data_frame=sales,
    x="Region",
    y="Units",
    title="Number of units by region",
    orientation="v",
    barmode="relative",
)

# Create total sales graph


# Create an app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.QUARTZ])
server = app.server # Needed for Gunicorn

# Create app layou
app.layout = dbc.Container(
    [
        html.H1("Sales Dashboard", className="text-center my-4"),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            [   html.Br(),
                                dbc.Card(
                                    dbc.CardBody(
                                        [
                                            html.H4(
                                                "Total Sales", className="card-title"
                                            ),
                                            html.P(
                                                total_orders,
                                                id="total-sales",
                                                className="card-text",
                                            ),
                                        ]
                                    ),
                                    className="mb-4 shadow-sm",
                                ),
                                html.H4("Filters", className="mb-3 text-white"),
                                dcc.Dropdown(
                                    className="text-black",
                                    id="product-dropdown",
                                    options=[
                                        {"label": item, "value": item}
                                        for item in sorted(sales["Item"].unique())
                                    ],
                                    multi=True,
                                    placeholder="Select product(s)",
                                ),
                                html.Br(),
                                dcc.Slider(
                                    className="text-black",
                                    id="slider",
                                    min=0,
                                    max=100,
                                    step=1,
                                    value=10,
                                    marks={i: f"{i} units" for i in range(0, 101, 20)},
                                ),
                                html.Br(),
                                dcc.Graph(id="pie-chart", figure=bar_chart),
                            ]
                        ),
                        className="shadow-sm",
                    ),
                ),
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            dash_table.DataTable(
                                id="table",
                                columns=[{"name": i, "id": i} for i in orders.columns],
                                data=orders.to_dict("records"),
                                editable=True,
                                filter_action="native",
                                sort_action="native",
                                column_selectable="single",
                                row_selectable="multi",
                                selected_columns=[],
                                selected_rows=[],
                                page_action="native",
                                page_current=0,
                                page_size=10,
                                style_header={
                                    "backgroundColor": "#9E4995",
                                    "color": "white",
                                    "fontWeight": "bold",
                                },
                                style_data={
                                    "backgroundColor": "#5D63B0",
                                    "color": "white",
                                    "whiteSpace": "normal",
                                    "height": "auto",
                                },
                                style_cell={
                                    "minWidth": 95,
                                    "maxWidth": 180,
                                    "textAlign": "left",
                                    "padding": "8px",
                                },
                            )
                        ),
                        className="shadow-sm",
                    ),
                    width=8,
                ),
            ]
        ),
    ],
    fluid=True,
)


@app.callback(
    [
        dash.dependencies.Output("table", "data"),
        dash.dependencies.Output("pie-chart", "figure"),
        dash.dependencies.Output("total-sales", "children"),
    ],
    [
        dash.dependencies.Input("product-dropdown", "value"),
        dash.dependencies.Input("slider", "value"),
    ],
)
def update_data(selected_items, slider):
    filtered = orders.copy()
   

    if selected_items:
        filtered = filtered[filtered["Item"].isin(selected_items)]

    if slider is not None:
        filtered = filtered[filtered["Units"] >= slider]
        
    total_orders = filtered["Units"].sum()

    updated_chart = px.bar(
        data_frame=filtered,
        x="Region",
        y="Units",
        title="Filtered units by region",
        orientation="v",
        barmode="relative",
    )

    return filtered.to_dict("records"), updated_chart, f"{total_orders} units"


if __name__ == "__main__":
    app.run()
