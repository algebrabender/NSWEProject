import altair as alt
import pandas as pd

map_df = pd.read_csv('uk_hex.csv', encoding="latin-1")
data_df = pd.read_csv('ge_2017.csv', encoding="latin-1")
df = data_df.merge(map_df, on="Constituency")

parties = ["Conservative", "Labour", "Lib Dem", "Green", "Scottish National Party", 
           "Plaid Cymru", "Sinn Fein", "Speaker", "Democratic Unionist Party", "Independent"]
party_colours = ["darkblue", "red", "orange", "green", "yellow", "#98df8a", "darkgreen", "lightgray", "#ad494a", "gold"]
colours_obj = alt.Color("Party:N", scale=alt.Scale(domain=parties, range=party_colours), legend=None)
selector = alt.selection_single(empty='all', fields=['Party'])
colours_condition = alt.condition(selector, colours_obj, alt.value("white"))

hexmap = alt.Chart(df).mark_circle().encode(
        x="q",
        y="r",
        color=colours_condition,
        size=alt.value(50),
        tooltip=["Constituency:N"],
    ).interactive().add_selection(selector)

legend = alt.Chart(df).mark_circle().encode(
            y=alt.Y("Party:N", axis=alt.Axis(orient="right")), color=colours_obj
        ).add_selection(selector)

df["threshold"] = 325.
bars = alt.Chart(df).mark_bar().encode(
            x="Party:N",
            y=alt.Y("count()", title="Number of MPs"),
            color=colours_condition
        ).add_selection(selector)

majority = alt.Chart(df).mark_rule(color="black", strokeDash=[1, 1]).encode(
    y="threshold:Q",
    size=alt.value(3)
)

legend | hexmap | (bars + majority)


from bokeh.plotting import figure, show
from bokeh.models import ColumnDataSource, NumeralTickFormatter, CategoricalColorMapper
from bokeh.layouts import gridplot
import pandas as pd
# Read the csv files
team_stats = pd.read_csv('2017-18_teamBoxScore.csv', parse_dates=['gmDate'])
phi_gm_stats_2 = (team_stats[(team_stats['teamAbbr'] == 'PHI') & (team_stats['seasTyp'] == 'Regular')]
                  .loc[:, ['gmDate', 'team2P%', 'team3P%', 'teamPTS', 'opptPTS']]
                  .sort_values('gmDate'))
# Store the data in a ColumnDataSource
gm_stats_cds = ColumnDataSource(phi_gm_stats_2)
# Create a CategoricalColorMapper that assigns specific colors to wins and losses
win_loss_mapper = CategoricalColorMapper(factors = ['W', 'L'], palette=['Green', 'Red'])
# Specify the tools
toolList = ['lasso_select', 'tap', 'reset', 'save']
# Create a figure relating the percentages
pctFig = figure(title='2PT FG % vs 3PT FG %, 2017-18 Regular Season',
                plot_height=400, plot_width=400, tools=toolList,
                x_axis_label='2PT FG%', y_axis_label='3PT FG%')
# Draw with circle markers
pctFig.circle(x='team2P%', y='team3P%', source=gm_stats_cds, size=12, color='black')
# Format the y-axis tick labels as percenages
pctFig.xaxis[0].formatter = NumeralTickFormatter(format='00.0%')
pctFig.yaxis[0].formatter = NumeralTickFormatter(format='00.0%')
# Create a figure relating the totals
totFig = figure(title='Team Points vs Opponent Points, 2017-18 Regular Season',
                plot_height=400, plot_width=400, tools=toolList,
                x_axis_label='Team Points', y_axis_label='Opponent Points')
# Draw with square markers
totFig.square(x='teamPTS', y='opptPTS', source=gm_stats_cds, size=10,
              color=dict(field='winLoss', transform=win_loss_mapper))
# Create layout
grid = gridplot([[pctFig, totFig]])
# Visualize
show(grid)


player_stats = pd.read_csv('2017-18_playerBoxScore.csv', parse_dates=['gmDate'])
# Store the data in a ColumnDataSource
player_gm_stats = ColumnDataSource(player_stats)
# Create a view for each player
lebron_filters = [GroupFilter(column_name='playFNm', group='LeBron'),
                  GroupFilter(column_name='playLNm', group='James')]
lebron_view = CDSView(source=player_gm_stats,
                      filters=lebron_filters)
durant_filters = [GroupFilter(column_name='playFNm', group='Kevin'),
                  GroupFilter(column_name='playLNm', group='Durant')]
durant_view = CDSView(source=player_gm_stats,
                      filters=durant_filters)
# Consolidate the common keyword arguments in dicts
common_figure_kwargs = {'plot_width': 400, 'x_axis_label': 'Points', 'toolbar_location': None }
common_circle_kwargs = {'x': 'playPTS', 'y': 'playTRB', 'source': player_gm_stats, 'size': 12, 'alpha': 0.7 }
common_lebron_kwargs = {'view': lebron_view, 'color': '#002859', 'legend': 'LeBron James' }
common_durant_kwargs = {'view': durant_view, 'color': '#FFC324', 'legend': 'Kevin Durant' }
# Create the two figures and draw the data
hide_fig = figure(**common_figure_kwargs, title='Click Legend to HIDE Data', y_axis_label='Rebounds')
hide_fig.circle(**common_circle_kwargs, **common_lebron_kwargs)
hide_fig.circle(**common_circle_kwargs, **common_durant_kwargs)
mute_fig = figure(**common_figure_kwargs, title='Click Legend to MUTE Data')
mute_fig.circle(**common_circle_kwargs, **common_lebron_kwargs, muted_alpha=0.1)
mute_fig.circle(**common_circle_kwargs, **common_durant_kwargs, muted_alpha=0.1)
# Add interactivity to the legend
hide_fig.legend.click_policy = 'hide'
mute_fig.legend.click_policy = 'mute'
# Visualize
show(row(hide_fig, mute_fig))
