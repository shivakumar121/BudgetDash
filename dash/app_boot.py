import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
from Transactions import Transactions
import pandas as pd
import plotly.figure_factory as ff
import plotly.graph_objects as go # or plotly.express as px



# df = px.data.iris()
transactions = Transactions(statements_dir='/Users/shivakumar/Documents/GitHubRepos/BudgetDash/data')
transactions.gather_all_statements()
transactions.generate_month_labels()
transactions.mark_duplicates_2()
all_transactions = transactions.transaction_df
summary_df = transactions.get_net_expense(df_to_use=all_transactions)
cols_to_exclude = ['Month_string', 'isDuplicate']
display_cols_bools = pd.Series(all_transactions.columns.values).isin(cols_to_exclude)
cols_to_display = all_transactions.columns[~display_cols_bools.values]

navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Link", href="#")),
        dbc.DropdownMenu(
            nav=True,
            in_navbar=True,
            label="Menu",
            children=[
                dbc.DropdownMenuItem("Entry 1"),
                dbc.DropdownMenuItem("Entry 2"),
                dbc.DropdownMenuItem(divider=True),
                dbc.DropdownMenuItem("Entry 3"),
            ],
        ),
    ],
    brand="Demo",
    brand_href="#",
    sticky="top",
)
fnameDict = {'chriddy': ['opt1_c', 'opt2_c', 'opt3_c'], 'jackp': ['opt1_j', 'opt2_j']}

# names = list(fnameDict.keys())
names = all_transactions['Month_string'].unique()
# table_kwargs = {'style_table': {'overflowX': 'scroll'}}
body = dbc.Container(
    [
        dbc.Row(
            [
            dbc.Col(
                [
                    html.H2("Graph"),
                    dcc.Graph(
                        # figure={"data": [{"x": [1, 2, 3], "y": [1, 4, 9]}]}
                        # figure=px.scatter(df, x="sepal_width", y="sepal_length")
                        figure=px.pie(data_frame=summary_df, names=summary_df.index.values, values='Amount_abs',
                                      hole=.3),
                        id='Graph'
                    ),
                ], width={'size': 6, 'offset': 3},
            ),
            ]
        )
    ],
    className="mt-4",
)
html_body = html.Div([
    dcc.Dropdown(
        id='name-dropdown',
        options=[{'label': name, 'value': name} for name in names],
        value=None
    ),
    html.Div(id='my-div')
], style={'width': '20%', 'display': 'inline-block'})
body_table = dbc.Container(
    [
         dbc.Row(
             [
                 dbc.Col(
                    [
                        html.H2("Transaction table"),
                        dcc.Graph(figure = ff.create_table(all_transactions[1:10]), id='Table'),
                    ],
                    width={'size': 12, 'oder': 'first'},
                 ),
             ]
         )
    ], className="mt-5"
)

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.config.suppress_callback_exceptions = True

app.layout = html.Div([navbar, body, html_body, body_table])

####

@app.callback(
    Output(component_id='Graph', component_property='figure'),
    [dash.dependencies.Input('name-dropdown', 'value')])
def update_graph(value):
    filtered_df = transactions.filter_by_month_string(month_string=value)
    summary_df = transactions.get_net_expense(df_to_use=filtered_df)
    print (summary_df)
    print (filtered_df)
    return px.pie(data_frame=summary_df, names=summary_df.index.values, values='Amount_abs',
                                          hole=.3)
#### Update table ####
@app.callback(
    Output(component_id='Table', component_property='figure'),
    [dash.dependencies.Input('name-dropdown', 'value')])
def update_table(value):
    filtered_df = transactions.filter_by_month_string(month_string=value)
    # summary_df = transactions.get_net_expense(df_to_use=filtered_df)
    # print (summary_df)
    # print (filtered_df)
    # table = dbc.Table.from_dataframe(df=all_transactions[cols_to_display], id='Table')
    table = ff.create_table(filtered_df)
    return table

if __name__ == "__main__":
    app.run_server()