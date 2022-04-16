from email.policy import default
from tkinter import Y
from unicodedata import name
import dash
from dash import dcc , html
from dash.dependencies import Input, Output, State
import numpy as np
import pandas as pd
import plotly.graph_objs as go
import plotly.express as px
from plotly.subplots import make_subplots
import urllib.request
from PIL import Image
import requests
from io import BytesIO

# https://htmlcheatsheet.com/css/

######################################################Data##############################################################

path_data = 'https://raw.githubusercontent.com/Dioguini97/DataView_42/main/Data/'

df_players = pd.read_csv(path_data + 'NBA_Players_With_Team.csv')
df_teams = pd.read_csv(path_data + 'NBA_Teams.csv')
shooting_stats = pd.read_csv(path_data + 'NBA_Active_Players_Data_14-04-2022.csv')
players_stats = pd.read_csv(path_data + 'NBA_Players_Stats_Data_14-04-2022.csv')
players_avg_stats = pd.read_csv(path_data + 'Season_Players_Stats.csv')
teams_avg_stats = pd.read_csv(path_data + 'Season_Teams_Stats.csv')
season_team_standings = pd.read_csv(path_data + 'NBA_Season_Team_Standings.csv')

path_img = 'https://raw.githubusercontent.com/Dioguini97/DataView_42/main/img/'
urllib.request.urlretrieve(path_img + 'nba_court.jpg', "nba_court.jpg")

img_court = Image.open("nba_court.jpg")

nba_logo = path_img + 'NBA_LOGO.png'

shooting_categories = ['FGM', 'FGA', 'FG3M', 'FG3A',  'FTM', 'FTA']
shooting_categories_percent = ['FG_PCT' , 'FG3_PCT' , 'FT_PCT']


######################################################Interactive Components############################################

players_options = [dict(label=player, value=player) for player in df_players['full_name'].unique()]


dropdown_players = dcc.Dropdown(
        id='players_drop',
        value='LeBron James',
        options=players_options
    )

dropdown_quarters = dcc.Dropdown(
        id='quarters_drop',
        options=['All Quarters','1st Quarter','2nd Quarter','3rd Quarter','4th Quarter','5th Quarter','6th Quarter','7th Quarter'],
        value='All Quarters'
    )


##################################################APP###################################################################

app = dash.Dash(__name__)

server = app.server

app.layout = html.Div([

    html.Div([
            html.H1('NBA Current Season Dashboard'), html.Img(src=nba_logo, id='nba_logo'), html.Hr()]
       , id='1st_row'),

    html.Div([
        html.Div([
            html.Div(
                html.Label('Player Choice')
            ),
            html.Div(
                dropdown_players
            )
        ], className='DropdownDiv'),

        html.Div([
            html.Div(
                html.Label('Quarter Choice')
            ),
            html.Div(
                dropdown_quarters
            )
        ], className='DropdownDiv'),
        html.Hr()], id='filterDiv'
    ),
    
    html.Div([

        html.Div([
            html.Img(id='player_img'),
            html.Div(
               [html.P(html.Label('Player Name', id='Player_Name')), html.P(html.Label('Player Height', id='Player_Height')),
                html.P(html.Label('Player Team', id='Player_Team')), html.P(html.Label('MVP Prize', id='MVP_Prize'))], id='player_text'
            )], id='player_info'),

        html.Div([
            html.Label('Player Sucess Shooting Performance'),
            dcc.Graph(
                    id='player_sucess_shooting_graph'
                    )
            ],style={'width': '49%', 'display': 'inline-block'}),
        html.Div([
            html.Label('Player Fail Shooting Performance'),
            dcc.Graph(
                    id='player_fail_shooting_graph'
                    )
            ],style={'width': '49%', 'display': 'inline-block'}),

        
    ], id='showDiv'),
    html.Div([
            html.Label('Player Shooting Stats'),
            dcc.Graph(
                    id='player_shootings_stats'
                    ),
            dcc.Graph(
                    id='player_shootings_stats(%)'
                    ),
            dcc.Graph(
                    id='player_others_stats'
                    )
            ]),
            
])


######################################################Callbacks#########################################################

@app.callback(
    [
    Output(component_id='player_img', component_property='src'),
    Output(component_id='Player_Name', component_property='children'),
    Output(component_id='Player_Height', component_property='children'),
    Output(component_id='Player_Team', component_property='children'),
    Output(component_id='MVP_Prize', component_property='children'),
    Output(component_id='player_sucess_shooting_graph', component_property='figure'),
    Output(component_id='player_fail_shooting_graph', component_property='figure'),
    Output(component_id='player_shootings_stats', component_property='figure'),
    Output(component_id='player_shootings_stats(%)', component_property='figure'),
    Output(component_id='player_others_stats', component_property='figure'),
    ],
    [Input(component_id='players_drop', component_property='value'),
    Input(component_id='quarters_drop', component_property='value')]
)


def shooting_plots(selected_player,quarter):
    #Set player image
    player_id=df_players[df_players['full_name']==selected_player]['id'].values[0]
    player_img_url='https://cdn.nba.com/headshots/nba/latest/1040x760/'+str(player_id)+'.png'

    player_name = df_players[df_players['id'] == player_id]['full_name'].values[0]



    #Create sucess shooting graph
    img_width = 500
    img_height = 418-(-52)

    shooting_player=shooting_stats[shooting_stats['PLAYER_NAME']==selected_player]
    shooting_player=shooting_player[shooting_player['EVENT_TYPE']=='Made Shot']
    #Update period/quarter 
    if quarter != 'All Quarters':
        Q = int(quarter[0])
        shooting_player=shooting_player[shooting_player['PERIOD']==Q]
    

    fig_sucess = px.scatter(shooting_player, x="LOC_X", y="LOC_Y",opacity=0.1)
    fig_sucess.update_traces(marker={'size': 8,'color':'green'})
    fig_sucess.update_layout(yaxis_range=[-52,418])
    fig_sucess.update_layout(xaxis_range=[-0.5*img_width,0.5*img_width])
    fig_sucess.update_layout(showlegend=False)
    fig_sucess.update_xaxes(visible=False)    
    fig_sucess.update_yaxes(visible=False)
    fig_sucess.add_layout_image(
        dict(
            x=-0.5*img_width,
            sizex=img_width,
            y=418,
            sizey=img_height,
            xref="x",
            yref="y",
            opacity=1,
            layer="below",
            sizing="stretch",
            source=img_court)
    )

    #Create failled shooting graph
    shooting_player=shooting_stats[shooting_stats['PLAYER_NAME']==selected_player]
    shooting_player=shooting_player[shooting_player['EVENT_TYPE']=='Missed Shot']
    #Update period/quarter 
    if quarter != 'All Quarters':
        Q = int(quarter[0])
        shooting_player=shooting_player[shooting_player['PERIOD']==Q]

    fig_fail = px.scatter(shooting_player, x="LOC_X", y="LOC_Y",opacity=0.1)
    fig_fail.update_traces(marker={'size': 8,'color':'red'})
    fig_fail.update_layout(yaxis_range=[-52,418])
    fig_fail.update_layout(xaxis_range=[-0.5*img_width,0.5*img_width])
    fig_fail.update_layout(showlegend=False)
    fig_fail.update_xaxes(visible=False)    
    fig_fail.update_yaxes(visible=False)
    fig_fail.add_layout_image(
        dict(
            x=-0.5*img_width,
            sizex=img_width,
            y=418,
            sizey=img_height,
            xref="x",
            yref="y",
            opacity=1,
            layer="below",
            sizing="stretch",
            source=img_court)
    )
    
    #Create RadarPlot for Shooting Statistics
    categories = ['FGM', 'FGA', 'FG3M', 'FG3A',  'FTM', 'FTA'] #Shooting Statistics
    categories_percent = ['FG_PCT' , 'FG3_PCT' , 'FT_PCT'] #Shooting Statistics Percentage

    team_selected_player=df_players[df_players['full_name']==selected_player]['team_id'].values[0]

    selected_player_stats=players_avg_stats[players_avg_stats['Player_ID']==player_id][categories].values.flatten().tolist()
    team_selected_player_stats=teams_avg_stats[teams_avg_stats['Team_ID']==team_selected_player][categories].values.flatten().tolist()

    season_players_stats=players_stats.mean()[['FGM', 'FGA', 'FG_PCT', 'FG3M', 'FG3A', 'FG3_PCT', 'FTM', 'FTA',
       'FT_PCT', 'OREB', 'DREB', 'REB', 'AST', 'STL', 'BLK', 'TOV', 'PF','PTS']].round(2)#.values.flatten().tolist()
        
    radar_plot_stats = go.Figure()
    radar_plot_stats.add_trace(go.Scatterpolar(
        r=selected_player_stats,
        theta=categories,
        fill='toself',
        name=selected_player
    ))
    radar_plot_stats.add_trace(go.Scatterpolar(
        r=team_selected_player_stats,
        theta=categories,
        fill='toself',
        name='Team Stats'
    ))
    radar_plot_stats.add_trace(go.Scatterpolar(
        r=season_players_stats[categories],
        theta=categories,
        fill='toself',
        name='Season Stats'
    ))
    radar_plot_stats.update_layout(
        polar=dict(
            radialaxis=dict(
            visible=True,
            range=[0, max(players_avg_stats['FGA'].max(),players_avg_stats['FTA'].max(),players_avg_stats['FG3A'].max())]
            )),
        showlegend=False
    )

    #Radar plot with Shootings Stats %
    selected_player_stats_percent=players_avg_stats[players_avg_stats['Player_ID']==player_id][categories_percent].values.flatten().tolist()
    team_selected_player_stats_percent=teams_avg_stats[teams_avg_stats['Team_ID']==team_selected_player][categories_percent].values.flatten().tolist()

    radar_plot_stats_perc = go.Figure()
    radar_plot_stats_perc.add_trace(go.Scatterpolar(
        r=selected_player_stats_percent,
        theta=categories_percent,
        fill='toself',
        name=selected_player
    ))
    radar_plot_stats_perc.add_trace(go.Scatterpolar(
        r=team_selected_player_stats_percent,
        theta=categories_percent,
        fill='toself',
        name='Team Stats'
    ))
    radar_plot_stats_perc.add_trace(go.Scatterpolar(
        r=season_players_stats[categories_percent],
        theta=categories_percent,
        fill='toself',
        name='Season Stats'
    ))
    radar_plot_stats_perc.update_layout(
        polar=dict(
            radialaxis=dict(
            visible=True,
            range=[0, 1]
            )),
        showlegend=False
    )

    #Create Data and Bar Plot with Statistics
    other_stats=['OREB', 'DREB', 'REB', 'AST', 'STL', 'BLK', 'TOV','PF', 'PTS']
    arr_who=[]
    arr_val=[]
    arr_stat=[]
    for col in other_stats:
        arr_who.append(selected_player)
        arr_stat.append(col)
        arr_val.append(players_avg_stats[players_avg_stats['Player_ID']==player_id][col].values[0])

    for col in other_stats:
        arr_who.append(df_teams[df_teams['id']==int(team_selected_player)]['full_name'].values[0])
        arr_stat.append(col)
        arr_val.append(teams_avg_stats[teams_avg_stats['Team_ID']==team_selected_player][col].values[0])

    for col in other_stats:
        arr_who.append("Season")
        arr_stat.append(col)
        arr_val.append(season_players_stats[col])
    comparison_df=pd.DataFrame([pd.Series(arr_who,name='Who'),pd.Series(arr_stat,name='Stat'),pd.Series(arr_val,name='Avg Value')]).T
    print(comparison_df)
    bar_plot_other_stats = px.bar(comparison_df, y="Stat", x="Avg Value", 
                 color="Who", barmode="group" ,orientation='h' )


    print(player_id)

    return player_img_url,player_name,player_name,player_name,player_name,fig_sucess,fig_fail,radar_plot_stats,radar_plot_stats_perc,bar_plot_other_stats

   


if __name__ == '__main__':
    app.run_server(debug=True)
