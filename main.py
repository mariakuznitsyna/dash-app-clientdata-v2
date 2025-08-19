# ===============================
# IMPORTS
# ===============================
import dash
from dash import dcc, html, dash_table, Input, Output
from dash_bootstrap_templates import load_figure_template
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px

# ===============================
# DATA LOAD & PREP
# (read once; keep a clean df to filter later)
# ===============================
sales = pd.read_csv("sales.csv")
product_info = pd.read_csv("product_info.csv")
orders = pd.merge(sales, product_info, how="left")

orders["OrderDate"] = pd.to_datetime(orders["OrderDate"], format="%m/%d/%y", errors="coerce")
orders["Units"] = pd.to_numeric(orders["Units"], errors="coerce").fillna(0)


# ===============================
# UTILITIES (formatters & helpers)
# ===============================
def fmt_units(n) -> str:
    return f"{int(n):,} units"


def fmt_money(x) -> str:
    if x is None:
        return "—"
    try:
        return f"${float(x):,.0f}"
    except Exception:
        return "—"


# ===============================
# APP & SERVER
# ===============================
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.COSMO])
load_figure_template("bootstrap")
server = app.server

# Base chart (units by region)
region_bar = px.bar(
    data_frame=orders,
    x="Region",
    y="Units",
    title="Number of units by region",
    orientation="v",
    barmode="relative",
)

# ===============================
# LAYOUT (all visible components live here)
#  - Header
#  - KPI cards (with IDs)
#  - Filters
#  - Graphs
#  - Table
# ===============================
app.layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col([
                    html.H1(
                        "Sales Dashboard",
                        className="text-primary p-3 rounded mt-4 mb-1 fw-bold"
                    ),
                    html.H2(
                        "Wally's Office",
                        className="text-primary rounded p-3"
                    ),],
                    width=4
                ),

                dbc.Col(
                    # Nested row to place three KPI cards side-by-side
                    dbc.Row(
                        [
                            dbc.Col(
                                dbc.Card(
                                    dbc.CardBody([
                                        html.H4("Total Sales", className="card-title"),
                                        html.P(id="total-sales", className="card-text fs-4 mb-0"),
                                    ]),
                                    className="shadow-sm rounded h-100",
                                     color="primary", inverse=True
                                ),
                                xs=12, md=4
                            ),
                            dbc.Col(
                                dbc.Card(
                                    dbc.CardBody([
                                        html.H4("Total Revenue", className="card-title"),
                                        html.P(id="total-revenue", className="card-text fs-4 mb-0"),
                                    ]),
                                    className="shadow-sm rounded h-100",
                                     color="primary", inverse=True
                                ),
                                xs=12, md=4
                            ),
                            dbc.Col(
                                dbc.Card(
                                    dbc.CardBody([
                                        html.H4("Top Product", className="card-title"),
                                        html.P(id="top-product", className="card-text fs-4 mb-0"),
                                    ]),
                                    className="shadow-sm rounded h-100",
                                     color="primary", inverse=True
                                ),
                                xs=12, md=4
                            ),
                        ],
                        className="g-3 my-4"
                    ),
                    width=8
                ),
            ],
            align="center"  # vertically center header with KPI row
        ),
                
        dbc.Row(
            [
                # ========= LEFT COLUMN (filters + KPIs + charts)
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            [
                                # ---- Filters
                                html.H4("Filters", className="mb-3 fw-semibold"),
                                # Date picker (replace your existing one)
                                dcc.DatePickerRange(
                                    id="date",
                                    minimum_nights=0,
                                    min_date_allowed=orders["OrderDate"].min().date(),
                                    max_date_allowed=orders["OrderDate"].max().date(),
                                    start_date=orders["OrderDate"].min().date(),
                                    end_date=orders["OrderDate"].max().date(),
                                ),
                                html.Br(),
                                dcc.Dropdown(
                                    id="product-dropdown",
                                    options=[
                                        {"label": i, "value": i}
                                        for i in sorted(
                                            orders["Item"].dropna().unique()
                                        )
                                    ],
                                    multi=True,
                                    placeholder="Select product(s)",
                                    className="text-black mb-3",
                                ),
                                html.Br(),
                                dcc.Slider(
                                    id="slider",
                                    min=0,
                                    max=100,
                                    step=1,
                                    value=10,
                                    marks={i: f"{i} units" for i in range(0, 101, 20)},
                                    className="text-black mb-3",
                                ),
                                html.Br(),
                                # ---- Charts
                                # Product pie
                                dcc.Loading(
                                    dcc.Graph(id="product-pie"),
                                    type="circle",
                                ),
                                dcc.Loading(dcc.Graph(id="trend-chart"), type="circle"),
                                # Region bar
                                dcc.Loading(
                                    dcc.Graph(id="region-chart", figure=region_bar),
                                    type="circle",
                                ),
                                html.Br(),
                            ]
                        ),
                        className="shadow-sm rounded",
                    ),
                    width=4,
                ),
                # ========= RIGHT COLUMN (table)
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            dash_table.DataTable(
                                id="table",
                                columns=[{"name": c, "id": c} for c in orders.columns],
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
                                    "backgroundColor": "var(--bs-primary)",
                                    "color": "var(--bs-light)",
                                    "fontWeight": "bold",
                                },
                                style_data={
                                    "backgroundColor": "var(--bs-body-bg)",
                                    "color": "var(--bs-body-color)",
                                    "whiteSpace": "normal",
                                    "height": "auto",
                                },
                                style_cell={
                                    "minWidth": 95,
                                    "maxWidth": 220,
                                    "textAlign": "left",
                                    "padding": "8px",
                                },
                                export_format="csv", 
                                export_headers="names"
                            )
                        ),
                        className="shadow-sm rounded",
                    ),
                    width=8,
                ),
            ]
        ),
    ],
    fluid=True,
)


# ===============================
# CALLBACKS (logic/wiring)
#  - Take Inputs (filters)
#  - Filter dataframe
#  - Compute KPIs
#  - Build figures
#  - Return outputs in the SAME ORDER as declared
# ===============================
@app.callback(
    Output("table", "data"),
    Output("region-chart", "figure"),
    Output("product-pie", "figure"),
    Output("trend-chart", "figure"), 
    Output("total-sales", "children"),
    Output("total-revenue", "children"),
    Output("top-product", "children"),
    Input("product-dropdown", "value"),
    Input("date", "start_date"),
    Input("date", "end_date"),
    Input("slider", "value"),
)
def update(selected_items, start_date, end_date, min_units):
    # --- filter base df
    df = orders.copy()
    
    # --- filter by date
    if start_date and end_date:
        start = pd.to_datetime(start_date)
        end = pd.to_datetime(end_date)
        df = df[(df["OrderDate"] >= start) & (df["OrderDate"] <= end)]


    # --- filter by product
    if selected_items:
        df = df[df["Item"].isin(selected_items)]
    if min_units is not None:
        df = df[df["Units"] >= int(min_units)]

    # --- handle empty state (must return all outputs)
    if df.empty:
        empty_bar = px.bar(title="No data for current filters")
        empty_pie = px.pie(title="No data for current filters")
        return [], empty_bar, empty_pie, "0 units", "$0.00", "—"

    # --- compute KPIs on the *filtered* df
    total_units = int(df["Units"].sum())
    total_revenue = round((df["Units"] * df["Unit Price"]).sum(), 2)
    top_product   = (
    df.groupby("Item")["Units"].sum()
      .sort_values(ascending=False)
      .index[0]
    if not df.empty else "—"
)

    # --- build figures from filtered df
    region_fig = px.bar(
        df,
        x="Region",
        y="Units",
        title="Filtered units by region",
        barmode="relative",
        orientation="v",
    )

    # Pie: which products did best (by units)
    by_item = ( df.groupby("Item", as_index=False)["Units"] .sum() .sort_values("Units", ascending=False) ) 
    pie_fig = px.pie( by_item, names="Item", values="Units", title="Product mix (units)", hole=0.35,)
    
    # --- trend 
    trend = df.set_index("OrderDate").resample("MS")["Units"].sum().reset_index()
    trend_fig = px.line(trend, x="OrderDate", y="Units", title="Monthly units")

    # --- format KPIs and return in the SAME ORDER as Outputs
    return (
        df.to_dict("records"), 
        region_fig, 
        pie_fig,
        trend_fig, 
        f"{total_units} units",
        f"{total_revenue} $",
        f"{top_product}",
    )
    

if __name__ == "__main__":
    app.run()
    
