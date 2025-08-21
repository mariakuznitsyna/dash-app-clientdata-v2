# ===============================
# IMPORTS
# ===============================
import dash
from dash import dcc, html, dash_table, Input, Output, State, no_update
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

# Coerce types
orders["OrderDate"] = pd.to_datetime(orders["OrderDate"], format="%m/%d/%y", errors="coerce")
orders["Units"] = pd.to_numeric(orders["Units"], errors="coerce").fillna(0)


# ===============================
# UTILITIES (formatters & helpers)
# ===============================
def fmt_units(n) -> str:
    return f"{int(n):,} units"

def fmt_money(x) -> str:
    try:
        return f"${float(x):,.2f}"
    except Exception:
        return "$0.00"

# ===============================
# APP & SERVER
# ===============================
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.COSMO, dbc.icons.BOOTSTRAP],
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)
load_figure_template("bootstrap")
server = app.server

# ===============================
# FILTERS UI (single source of truth)
# ===============================
def filters_content():
    return html.Div(
        [
            html.H4("Filters", className="fw-semibold mb-1"),

            dbc.Label("Date range"),
            dcc.DatePickerRange(
                id="date",
                minimum_nights=0,
                min_date_allowed=orders["OrderDate"].min().date(),
                max_date_allowed=orders["OrderDate"].max().date(),
                start_date=orders["OrderDate"].min().date(),
                end_date=orders["OrderDate"].max().date(),
                className="date-range w-100",
            ),

            dbc.Label("Products"),
            dcc.Dropdown(
                id="product-dropdown",
                options=[{"label": i, "value": i} for i in sorted(orders["Item"].dropna().unique())],
                multi=True,
                placeholder="Select product(s)",
                className="text-black",
            ),

            dbc.Label("Minimum units"),
            dcc.Slider(
                id="slider", min=0, max=100, step=1, value=10,
                marks={i: f"{i} units" for i in range(0, 101, 20)},
                className="text-black",
            ),

            dbc.Button("Reset filters", id="reset-filters", color="secondary", outline=True, className="mt-2"),
        ],
        className="d-grid gap-3",
    )

# ===============================
# LAYOUT
# ===============================
app.layout = dbc.Container(
    [
        # Row 1: Header + KPIs
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H1("Sales Dashboard", className="text-primary p-3 rounded mt-4 mb-1 fw-bold"),
                        html.H2("Wally's Office", className="text-primary rounded p-3 d-none d-sm-block"),
                    ],
                    xs=12, md=3,
                ),
                dbc.Col(
                    dbc.Row(
                        [
                            # KPI: Total Sales (Units)
                            dbc.Col(
                                dbc.Card(
                                    dbc.CardBody(
                                        [
                                            html.H4(
                                                [html.I(className="bi bi-graph-up-arrow me-2"), "Total Sales"],
                                                className="card-title",
                                            ),
                                            html.P(id="total-sales", className="card-text fs-4 mb-0"),
                                        ]
                                    ),
                                    className="kpi-card shadow-sm rounded h-100",
                                    color="primary", inverse=True,
                                ),
                                xs=12, sm=6, md=4,
                            ),
                            # KPI: Total Revenue
                            dbc.Col(
                                dbc.Card(
                                    dbc.CardBody(
                                        [
                                            html.H4(
                                                [html.I(className="bi bi-cash-stack me-2"), "Total Revenue"],
                                                className="card-title",
                                            ),
                                            html.P(id="total-revenue", className="card-text fs-4 mb-0"),
                                        ]
                                    ),
                                    className="kpi-card shadow-sm rounded h-100",
                                    color="primary", inverse=True,
                                ),
                                xs=12, sm=6, md=4,
                            ),
                            # KPI: Top Product (by revenue)
                            dbc.Col(
                                dbc.Card(
                                    dbc.CardBody(
                                        [
                                            html.H4([html.I(className="bi bi-trophy me-2"), "Top Product"], className="card-title"),
                                            html.P(id="top-product", className="card-text fs-4 mb-0"),
                                        ]
                                    ),
                                    className="kpi-card shadow-sm rounded h-100",
                                    color="primary", inverse=True,
                                ),
                                xs=12, sm=6, md=4,
                            ),
                        ],
                        className="g-3 my-4",
                    ),
                    xs=12, md=9,
                ),
            ],
            align="center",
        ),

        # Row 2: Filters (left, collapsible) + Charts (right)
        dbc.Row(
            [
                # LEFT: Filters (single instance, collapsible on mobile)
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            html.Div(
                                [
                                    dbc.Button("Filters", id="toggle-filters", color="primary",
                                               className="d-md-none mb-2"),
                                    dbc.Collapse(filters_content(), id="filters-collapse", is_open=True),
                                ],
                                className="w-100",
                            )
                        ),
                        className="shadow-sm rounded h-100 w-100 sticky-card",
                    ),
                    xs=12, md=3,
                    className="d-flex",
                ),

                # RIGHT: Charts grid
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            [
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            dcc.Loading(
                                                dcc.Graph(id="product-pie", config={"responsive": True}),
                                                type="circle",
                                            ),
                                            xs=12, md=6,
                                        ),
                                        dbc.Col(
                                            dcc.Loading(
                                                dcc.Graph(id="region-chart", config={"responsive": True}),
                                                type="circle",
                                            ),
                                            xs=12, md=6,
                                        ),
                                    ],
                                    className="g-3",
                                ),
                                html.Br(),
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            dcc.Loading(
                                                dcc.Graph(id="trend-chart", config={"responsive": True}),
                                                type="circle",
                                            ),
                                            xs=12,
                                        )
                                    ]
                                ),
                            ]
                        ),
                        className="shadow-sm rounded h-100 w-100",
                    ),
                    xs=12, md=9,
                    className="d-flex",
                ),
            ],
            className="align-items-stretch g-3 mb-4",
        ),

        # Row 3: Table full-width
        dbc.Row(
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
                            export_format="csv",
                            export_headers="names",
                            style_table={"overflowX": "auto"},
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
                            style_cell={"minWidth": 95, "maxWidth": 220, "textAlign": "left", "padding": "8px"},
                        )
                    ),
                    className="shadow-sm rounded",
                ),
                xs=12,
            )
        ),
    ],
    fluid=True,
)

# ===============================
# CALLBACKS
# ===============================

# Mobile toggle for filters Collapse
@app.callback(
    Output("filters-collapse", "is_open"),
    Input("toggle-filters", "n_clicks"),
    State("filters-collapse", "is_open"),
    prevent_initial_call=True,
)
def toggle_filters(n, is_open):
    return (not is_open) if n else is_open

# Reset filters to defaults
@app.callback(
    Output("date", "start_date"),
    Output("date", "end_date"),
    Output("product-dropdown", "value"),
    Output("slider", "value"),
    Input("reset-filters", "n_clicks"),
    prevent_initial_call=True,
)
def reset_filters(n):
    if not n:
        return no_update, no_update, no_update, no_update
    start = orders["OrderDate"].min().date()
    end = orders["OrderDate"].max().date()
    return start, end, None, 10

# Main update: table + charts + KPIs
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

    # Date filter
    if start_date and end_date:
        start = pd.to_datetime(start_date)
        end = pd.to_datetime(end_date)
        df = df[(df["OrderDate"] >= start) & (df["OrderDate"] <= end)]

    # Product + min units filters
    if selected_items:
        df = df[df["Item"].isin(selected_items)]
    if min_units is not None:
        df = df[df["Units"] >= int(min_units)]

    # Empty state
    if df.empty:
        empty_bar = px.bar(title="No data for current filters")
        empty_pie = px.pie(title="No data for current filters")
        empty_line = px.line(title="No data for current filters")
        return [], empty_bar, empty_pie, empty_line, "0 units", "$0.00", "—"

    # KPIs (after filters)
    total_units   = int(df["Units"].sum())
    total_revenue = (df["Units"] * df["Unit Price"]).sum()
    top_product   = (
        df.assign(Revenue=df["Units"] * df["Unit Price"])
          .groupby("Item")["Revenue"].sum().idxmax()
    )

    # Region bar (Units by Region)
    region_fig = px.bar(
        df, x="Region", y="Units",
        title="Filtered units by region", barmode="relative", orientation="v",
    )

    # Pie: Top 5 by REVENUE + Other
    by_item = (
        df.assign(Revenue=df["Units"] * df["Unit Price"])
          .groupby("Item", as_index=False)["Revenue"].sum()
          .sort_values("Revenue", ascending=False)
    )
    N = 5
    if len(by_item) > N:
        other_val = by_item["Revenue"].iloc[N:].sum()
        by_item = pd.concat(
            [by_item.iloc[:N], pd.DataFrame({"Item": ["Other"], "Revenue": [other_val]})],
            ignore_index=True,
        )
    pie_fig = px.pie(
        by_item, names="Item", values="Revenue",
        title=f"Product mix (top {N} by revenue)", hole=0.35,
    )

    # Trend: Monthly Revenue
    trend = (
        df.assign(Revenue=df["Units"] * df["Unit Price"])
          .set_index("OrderDate").resample("MS")["Revenue"].sum().reset_index()
    )
    trend_fig = px.line(trend, x="OrderDate", y="Revenue", title="Monthly revenue")

    # Consistent layout polish
    for fig in (region_fig, pie_fig, trend_fig):
        fig.update_layout(
            height=340,
            margin=dict(l=10, r=10, t=40, b=10),
            legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
        )
    pie_fig.update_traces(textposition="inside", textinfo="percent+label", insidetextorientation="radial")

    # Return
    return (
        df.to_dict("records"),
        region_fig,
        pie_fig,
        trend_fig,
        fmt_units(total_units),
        fmt_money(total_revenue),
        top_product,
    )

# ===============================
# RUN
# ===============================
if __name__ == "__main__":
    app.run()
