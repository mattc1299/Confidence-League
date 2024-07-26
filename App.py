# -*- coding: utf-8 -*-
"""
Created on Thu Apr 18 15:36:38 2024

@author: Matt
"""

import streamlit as st
from streamlit_option_menu import option_menu
# from streamlit_custom_notification_box import custom_notification_box as popup
# from st_files_connection import FilesConnection
from streamlit_modal import Modal
from google.cloud import storage
from google.oauth2 import service_account
import pandas as pd
import numpy as np
import math
from datetime import datetime,date
import pytz
import pickle
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
#cd Documents\GitHub\Confidence-League
#streamlit run App.py
class User:
    def __init__(self, name):
        self.Name = name
        self.Data = {}
        self.Scores = {}
        self.Total = 0
        with open('C:/Users/Matt/Documents/Python Scripts/Confidence Users/Official/Team Totals Zero.pk1','rb') as f:
              self.Teams=pickle.load(f)
        with open('C:/Users/Matt/Documents/Python Scripts/Confidence Users/Official/Confidences.pk1','rb') as f:
              self.Confidences=pickle.load(f)
        
    def AddWeek(self, week, data):
        self.Data[week] = data
    
    def Score(self, week, winners):
        data = self.Data.get(week)
        comparison = np.where(data['Winner']==winners['Winner'], data['Confidence'],0)
        self.Scores[week] = int(np.sum(comparison))
        self.Total = sum(self.Scores.values())
        # self.Total=0 #=sum(scores.values())
        # for score in self.Scores.values():
        #     self.Total += score

    def TeamScores(self, week, winners):
        data = self.Data.get(week)
        self.Teams[f'Wk{week}'] = 0
        for i in range(0,len(data)): #update the number of occurences of each confidence for % correct and weekly track team rankings
            Con = int(data.iloc[i,1])
            self.Confidences.loc[Con,'Occurrences'] += 1
            team = data.iloc[i,0] #team assigned confidence
            self.Teams.loc[team, f'Wk{week}'] = Con
        Comparison = np.where(data['Winner']==winners['Winner'], data['Confidence'], 0) #gets confidence of each matchup
        for i in range(0,len(winners)):
            team = winners.iloc[i,0] #team that won
            self.Teams.loc[team,['Total']] += Comparison[i]
            if int(Comparison[i]) in self.Confidences.index: self.Confidences.loc[int(Comparison[i]),'Total'] += Comparison[i]
        #need to handel 0/0 nan result
        self.Confidences['Correct'] = round(self.Confidences['Total'] / (self.Confidences['Occurrences'] * self.Confidences.index),2)
        self.Confidences.fillna(value=0, inplace=True)
        hold = self.Teams[self.Teams.columns[3:]]
        self.Teams['Average'] = round(hold.mean(axis=1), 2)

@st.cache_resource
def loadBucket():
    credentials = service_account.Credentials.from_service_account_info(st.secrets)
    storage_client = storage.Client(project=st.secrets['project_id'], credentials=credentials)
    # bucket = storage_client.bucket('current-selections')
    bucket = storage_client.bucket('confidence-beta-1')
    return bucket
# st.session_state.weekSubmissions = list(bucket.list_blobs())

@st.cache_resource
def getBlob(name,week):
    bucket = loadBucket()
    return bucket.blob(f'Wk{week}/{name} Wk{week}.csv')

@st.cache_data
def establishInputs(today):
    startDate = date(2024,7,1,)
    # today=date.today()
    week=(today-startDate).days//7
    seasonWeeks=[]
    for i in range(1,week):
        seasonWeeks.append(i)
    # df = pd.read_csv(f'Matchups/Matchups Wk{week}.csv')
    # df = pd.read_csv('Matchups Wk1.csv')
    bucket = loadBucket()
    blob = bucket.blob(f'Wk{week}/Matchups Wk{week}.csv')
    with blob.open('r') as f:
        df = pd.read_csv(f)
    matchups = df[f'Wk{week}'].tolist()
    # matchups = df['Wk1'].tolist()
    userdf = pd.read_csv('Users.csv')
    users={}
    names=[]
    for i in range(0,len(userdf)):
        users[userdf.iloc[i,0]]=userdf.iloc[i,1]
        names.append(userdf.iloc[i,0])
    return week, seasonWeeks, users, names, matchups


def CheckTime(currentTime):
    dayOfWeek = currentTime.weekday()
    if dayOfWeek in [1,2,3]:
        if dayOfWeek == 3:
            if currentTime.hour <= 17:
                return True
            else:
                return False
        else:
            return True
    else:
        return False


def UserLeader(userList):
    data = [(user.Name,user.Total) for user in userList.values()]
    scores = pd.DataFrame(data, columns=['Name','Total'])
    scores = scores.sort_values(by=['Total'], ascending=True)
    plotScores = scores.tail(5)
    xmin = plotScores['Total'].min()-20
    xmax = plotScores['Total'].max()+20
    fig = px.bar(plotScores,x='Total',y='Name',orientation='h',title='<b>User Leaderboard</b>',text='Total')
    fig.update_traces(textposition='outside', hovertemplate='<b>%{y}</b><br>Total: %{x}<br><extra></extra>')
    fig.update_layout(xaxis_range=[xmin,xmax])
    return fig
    # st.plotly_chart(fig,use_container_width=True)


def TeamLeader(teamTotals):
    teamSorted = teamTotals[['Total','Average']].copy().reset_index()
    # teamSorted = teamSorted[['Name','Total']].copy()
    teamSorted = teamSorted.sort_values(by=['Total'], ascending=True)
    plotTeam = teamSorted.tail(5).reset_index()
    plotTeam=plotTeam.rename(columns={'Name':'Team'})
    xmin = plotTeam['Total'].min()-20
    xmax = plotTeam['Total'].max()+20
    fig = px.bar(plotTeam,x='Total',y='Team',orientation='h',title='<b>Team Leaderboard</b>',text='Total')
    fig.update_traces(textposition='outside', hovertemplate='<b>%{y}</b><br>Total: %{x}<br><extra></extra>')
    fig.update_layout(xaxis_range=[xmin,xmax])
    return fig
    # st.plotly_chart(fig,use_container_width=True)


def TeamTotals(teamTotals):
    data = teamTotals.copy().reset_index()
    # data = user.Teams.reset_index()
    # data['Conference'] = 0
    # for i in range(0, len(data)):
    #     val = math.floor(i/4) +1
    #     data.loc[i,'Conference'] = val
    data.sort_values(by=['Conference','Name'],ascending=[True,True],inplace=True)
    fig=go.Figure()
    for i,conf in enumerate(data['Conference'].unique()):
        dataPlot = data[data['Conference']==conf]
        fig.add_trace(
            go.Bar(x=dataPlot['Name'],y=dataPlot['Total'],name=str(conf),text=dataPlot['Total'],textposition='outside',hovertemplate='<b>%{x}</b><br>Total: %{y}<extra></extra>'))
    fig.update_layout(title='Points Scored Per Team',
        updatemenus=[
            dict(
                active=0,
                x=0.85,
                y=1.3,
                buttons=list([
                    dict(label="all",
                         method="update",
                         args=[{"visible": [True, True, True, True, True, True, True, True]},
                               {"title": 'Team Confidence Distribution'}]),
                    dict(label="AFC",
                         method="update",
                         args=[{"visible": [True, True, True, True, False, False, False, False]},
                               {"title": 'AFC Confidence Distribution'}]),
                                # "annotations": []}]),
                    dict(label="AFC East",
                         method="update",
                         args=[{"visible": [True, False, False, False, False, False, False, False]},
                               {"title": 'AFC East Confidence Distribution'}]),
                                # "annotations": []}]),
                    dict(label="AFC North",
                         method="update",
                         args=[{"visible": [False, True, False, False, False, False, False, False]},
                               {"title": 'AFC North Confidence Distribution'}]),
                                # "annotations": high_annotations}]),
                    dict(label="AFC South",
                         method="update",
                         args=[{"visible": [False, False, True, False, False, False, False, False]},
                               {"title": 'AFC South Confidence Distribution'}]),
                                # "annotations": low_annotations}]),
                    dict(label="AFC West",
                         method="update",
                         args=[{"visible": [False, False, False, True, False, False, False, False]},
                               {"title": 'AFC West Confidence Distribution'}]),
                                # "annotations": high_annotations + low_annotations}]),
                    dict(label="NFC",
                         method="update",
                         args=[{"visible": [False, False, False, False, True, True, True, True]},
                               {"title": 'NFC Confidence Distribution'}]),
                                # "annotations": []}]),
                    dict(label="NFC East",
                         method="update",
                         args=[{"visible": [False, False, False, False, True, False, False, False]},
                               {"title": 'NFC East Confidence Distribution'}]),
                                # "annotations": []}]),
                    dict(label="NFC North",
                         method="update",
                         args=[{"visible": [False, False, False, False, False, True, False, False]},
                               {"title": 'NFC North Confidence Distribution'}]),
                                # "annotations": high_annotations}]),
                    dict(label="NFC South",
                         method="update",
                         args=[{"visible": [False, False, False, False, False, False, True, False]},
                               {"title": 'NFC South Confidence Distribution'}]),
                                # "annotations": low_annotations}]),
                    dict(label="NFC West",
                         method="update",
                         args=[{"visible": [False, False, False, False, False, False, False, True]},
                               {"title": 'NFC West Confidence Distribution'}]),
                ]),
            )            
        ])
    ymax=math.ceil(data['Total'].max()/10)*10
    fig.update_layout(boxmode='group',
        yaxis=dict(title='Total',gridcolor='gray',range=[0,ymax+1]),#,tickvals=[i for i in range(0, ymax+1, int(ymax/5))]),
        xaxis=dict(title='Team',tickangle=45))
    fig.add_annotation(xref='paper',yref='paper',x=.6,y=1.28,text='Division:',font=dict(size=12), showarrow=False)
    # fig.show()
    return fig


def TeamBox(teamTotals):
    data = teamTotals.copy().reset_index()
    data.drop(columns=['Total','Average'],inplace=True)
    # teamTotals = teamTotals.drop(columns=['Total','Average']).reset_index()
    data = data.melt(id_vars=['Name','Conference'])
    data.sort_values(by=['Conference','Name'],ascending=[True,True],inplace=True)
    fig = go.Figure()
    for i,conf in enumerate(data['Conference'].unique()):
        dataPlot = data[data['Conference']==conf]
        fig.add_trace(go.Box(x=dataPlot['Name'], y=dataPlot['value'], name=str(conf), boxpoints='all', boxmean=True)) #boxpoints='outliers'
    
    fig.update_layout(
        updatemenus=[
            dict(
                active=0,
                x=0.85,
                y=1.3,
                buttons=list([
                    dict(label="all",
                         method="update",
                         args=[{"visible": [True, True, True, True, True, True, True, True]},
                               {"title": 'Team Confidence Distribution'}]),
                    dict(label="AFC",
                         method="update",
                         args=[{"visible": [True, True, True, True, False, False, False, False]},
                               {"title": 'AFC Confidence Distribution'}]),
                                # "annotations": []}]),
                    dict(label="AFC East",
                         method="update",
                         args=[{"visible": [True, False, False, False, False, False, False, False]},
                               {"title": 'AFC East Confidence Distribution'}]),
                                # "annotations": []}]),
                    dict(label="AFC North",
                         method="update",
                         args=[{"visible": [False, True, False, False, False, False, False, False]},
                               {"title": 'AFC North Confidence Distribution'}]),
                                # "annotations": high_annotations}]),
                    dict(label="AFC South",
                         method="update",
                         args=[{"visible": [False, False, True, False, False, False, False, False]},
                               {"title": 'AFC South Confidence Distribution'}]),
                                # "annotations": low_annotations}]),
                    dict(label="AFC West",
                         method="update",
                         args=[{"visible": [False, False, False, True, False, False, False, False]},
                               {"title": 'AFC West Confidence Distribution'}]),
                                # "annotations": high_annotations + low_annotations}]),
                    dict(label="NFC",
                         method="update",
                         args=[{"visible": [False, False, False, False, True, True, True, True]},
                               {"title": 'NFC Confidence Distribution'}]),
                                # "annotations": []}]),
                    dict(label="NFC East",
                         method="update",
                         args=[{"visible": [False, False, False, False, True, False, False, False]},
                               {"title": 'NFC East Confidence Distribution'}]),
                                # "annotations": []}]),
                    dict(label="NFC North",
                         method="update",
                         args=[{"visible": [False, False, False, False, False, True, False, False]},
                               {"title": 'NFC North Confidence Distribution'}]),
                                # "annotations": high_annotations}]),
                    dict(label="NFC South",
                         method="update",
                         args=[{"visible": [False, False, False, False, False, False, True, False]},
                               {"title": 'NFC South Confidence Distribution'}]),
                                # "annotations": low_annotations}]),
                    dict(label="NFC West",
                         method="update",
                         args=[{"visible": [False, False, False, False, False, False, False, True]},
                               {"title": 'NFC West Confidence Distribution'}]),
                ]),
            )            
        ])
    
    fig.update_layout(title_text='<b>Team Confidence Distribution</b>',boxmode='group',
        legend=dict(orientation="v"),
        yaxis=dict(title_text='Confidence',range=[0,16.2], tickvals=[i for i in range(0,17,2)]),
        xaxis=dict(title_text='Team',tickangle=45))
    fig.add_annotation(xref='paper',yref='paper',x=.6,y=1.28,text='Division:',font=dict(size=14), showarrow=False)
    # fig.update_yaxes(title_text='Confidence',range=[0,16], tickvals=[i for i in range(0,17,2)])
    # fig.update_xaxes(title_text='Team')
    # fig.show()
    return fig


def UserWeeklyCompare(users): #add selector for week ranges
    # color1={2:'rgb(254,1,1)',1:'rgb(255,179,0)',4:'rgb(0,170,255)',3:'rgb(144,0,255)',0:'rgb(0,145,255)'}
    # color2={2:'rgb(254,92,92)',1:'rgb(255,206,92)',4:'rgb(92,201,255)',3:'rgb(180,82,255)',0:'rgb(131,201,255)'} #68 transaprency
    # color2={0:'rgb(254,128,128)',1:'rgb(255,217,128)',2:'rgb(128,212,255)',3:'rgb(200,128,255)'} 75 trasnparency more trasnaprent color
    color2={0:'rgb(131,201,255)',1:'rgb(0,103,199)',2:'rgb(255,173,173)',3:'rgb(255,77,77)'} #173
    color1={0:'rgb(51,167,255)',1:'rgb(0,82,158)',2:'rgb(255,128,128)',3:'rgb(255,41,41)'} #darker 112

    weekly = pd.DataFrame({user.Name: user.Scores for user in users.values()})
    total = weekly.cumsum()
    weekly = weekly.rename_axis('Week')
    total = total.rename_axis('Week')
    # data = np.random.randint(50,150,size=(4,16))
    # weekly = pd.DataFrame(data.T, columns=['Justice','Brian','Gage','Matt'])
    # total = weekly.cumsum()
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    for i,name in enumerate(weekly.columns):
        fig.add_trace(
            go.Bar(x=weekly.index, y=weekly[name], name=f'{name} Weekly', marker={'color':color2[i]}, textposition='outside',
                   hovertemplate='<b>%{data.name}</b><br>Week: %{x}<br>Score: %{y}<extra></extra>',legendgroup=f'{i}'),
            secondary_y=False,
        )
        fig.add_trace(
            go.Scatter(x=total.index, y=total[name], name=f'{name} Total', mode='lines+markers+text', textposition='top center', marker=dict(color=color1[i],symbol='diamond',size=10,line=dict(width=1,color='black')),
                       hovertemplate='<b>%{data.name}</b><br>Week: %{x}<br>Total: %{y}<extra></extra>',legendgroup=f'{i}',showlegend=False),
            secondary_y=True,
        )
    fig.update_layout(title_text='<b>Weekly Score Comparison</b>', legend=dict(orientation="h",yanchor='bottom',y=1,xanchor='right',x=.9))
    ymax = math.ceil(total.max().max()/100)*100 #max takes max of each column and returns array, second max takes max of array
    fig.update_layout(
        yaxis=dict(title='Weekly Score', range=[0,201], gridcolor='grey'),
        yaxis2=dict(overlaying='y', side='right', title='Total Score', range=[0,ymax], tickvals=[i for i in range(0, ymax+1, int(ymax/4))], showgrid=False),
        xaxis=dict(title='Week', tickvals=[i for i in range(0,len(weekly)+1,1)],rangeslider=dict(visible=True,thickness=0.1)),#,yaxis=dict(range=[1800,1900])))
        # xaxis=dict(title='Week', tickvals=[i for i in range(0,len(weekly)+1,1)])
        xaxis2=dict(visible=False)
        )
    # fig.show()
    return fig


def UserTeamTotals(user):
    data = user.Teams.reset_index()
    # data['Conference'] = 0
    # for i in range(0, len(data)):
    #     val = math.floor(i/4) +1
    #     data.loc[i,'Conference'] = val
    data.sort_values(by=['Conference','Name'],ascending=[True,True],inplace=True)
    fig=go.Figure()
    for i,conf in enumerate(data['Conference'].unique()):
        dataPlot = data[data['Conference']==conf]
        fig.add_trace(
            go.Bar(x=dataPlot['Name'],y=dataPlot['Total'],name=str(conf),text=dataPlot['Total'],textposition='outside',hovertemplate='<b>%{x}</b><br>Total: %{y}<extra></extra>'))
    fig.update_layout(
        updatemenus=[
            dict(
                active=0,
                x=0.85,
                y=1.3,
                buttons=list([
                    dict(label="all",
                         method="update",
                         args=[{"visible": [True, True, True, True, True, True, True, True]},
                               {"title": 'Team Confidence Distribution'}]),
                    dict(label="AFC",
                         method="update",
                         args=[{"visible": [True, True, True, True, False, False, False, False]},
                               {"title": 'AFC Confidence Distribution'}]),
                                # "annotations": []}]),
                    dict(label="AFC East",
                         method="update",
                         args=[{"visible": [True, False, False, False, False, False, False, False]},
                               {"title": 'AFC East Confidence Distribution'}]),
                                # "annotations": []}]),
                    dict(label="AFC North",
                         method="update",
                         args=[{"visible": [False, True, False, False, False, False, False, False]},
                               {"title": 'AFC North Confidence Distribution'}]),
                                # "annotations": high_annotations}]),
                    dict(label="AFC South",
                         method="update",
                         args=[{"visible": [False, False, True, False, False, False, False, False]},
                               {"title": 'AFC South Confidence Distribution'}]),
                                # "annotations": low_annotations}]),
                    dict(label="AFC West",
                         method="update",
                         args=[{"visible": [False, False, False, True, False, False, False, False]},
                               {"title": 'AFC West Confidence Distribution'}]),
                                # "annotations": high_annotations + low_annotations}]),
                    dict(label="NFC",
                         method="update",
                         args=[{"visible": [False, False, False, False, True, True, True, True]},
                               {"title": 'NFC Confidence Distribution'}]),
                                # "annotations": []}]),
                    dict(label="NFC East",
                         method="update",
                         args=[{"visible": [False, False, False, False, True, False, False, False]},
                               {"title": 'NFC East Confidence Distribution'}]),
                                # "annotations": []}]),
                    dict(label="NFC North",
                         method="update",
                         args=[{"visible": [False, False, False, False, False, True, False, False]},
                               {"title": 'NFC North Confidence Distribution'}]),
                                # "annotations": high_annotations}]),
                    dict(label="NFC South",
                         method="update",
                         args=[{"visible": [False, False, False, False, False, False, True, False]},
                               {"title": 'NFC South Confidence Distribution'}]),
                                # "annotations": low_annotations}]),
                    dict(label="NFC West",
                         method="update",
                         args=[{"visible": [False, False, False, False, False, False, False, True]},
                               {"title": 'NFC West Confidence Distribution'}]),
                ]),
            )            
        ])
    ymax=math.ceil(user.Teams['Total'].max()/10)*10
    fig.update_layout(title_text='<b>Points Scored Per Team</b>', boxmode='group',
        yaxis=dict(title='Total',gridcolor='gray',range=[0,ymax+1]),#,tickvals=[i for i in range(0, ymax+1, int(ymax/5))]),
        xaxis=dict(title='Team',tickangle=45))
    fig.add_annotation(xref='paper',yref='paper',x=.6,y=1.28,text='Division:',font=dict(size=14), showarrow=False)
    return fig


def UserConfidencePercent(user):
    color1={0:'rgb(254,1,1)',1:'rgb(255,179,0)',2:'rgb(0,170,255)',3:'rgb(144,0,255)'}
    color2={0:'rgb(254,92,92)',1:'rgb(255,206,92)',2:'rgb(92,201,255)',3:'rgb(180,82,255)'}
    data = user.Confidences.reset_index()
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Bar(x=data['Confidence'], y=data['Correct'], name='% Accuracy', text=[f'{i:.0f}%' for i in data['Correct']*100],
               textposition='outside', hovertemplate='<b>%{data.name}</b><br>Confidence Level: %{x}<br>Accuracy: %{y}<extra></extra>'),#, marker={'color':color2[2]}),
        secondary_y=False,
        )
    fig.add_trace(
        go.Scatter(x=data['Confidence'], y=data['Total'], name='Total', mode='lines+markers+text', text=data['Total'], textposition='top center', textfont=dict(color='rgb(0,103,199)'), marker=dict(color='rgb(0,103,199)',symbol='diamond',size=10),#color1[1]
                   hovertemplate='<b>%{data.name}</b><br>Confidence Level: %{x}<br>Total: %{y}<extra></extra>'),
        secondary_y=True,
        )
    ymax = math.ceil(user.Confidences['Total'].max()/10)*10
    fig.update_layout(title_text='<b>Confidence Level Performance</b>',
        legend=dict(orientation="h",yanchor='bottom',y=1,xanchor='right',x=.9),
        yaxis=dict(title='Accuracy (%)',range=[0,1.01], tickformat='.0%', gridcolor='grey'),
        yaxis2=dict(title='Total Scored per Confidence Level', overlaying='y', side='right', range=[0,ymax], tickvals=[i for i in range(0, ymax+1, int(ymax/5))], showgrid=False),
        xaxis=dict(title='Confidence Level', tickvals=[i for i in range(0,17,1)]))
    return fig


def UserBox(user, teams=None):
    data = user.Teams
    # data['Conference'] = 0
    # for i in range(0, len(data)):
    #     val = math.floor(i/4) +1
    #     data.iloc[i,5] = val
    data = data.drop(columns=['Total','Average']).reset_index()
    data = data.melt(id_vars=['Name','Conference'])
    data.sort_values(by=['Conference','Name'],ascending=[True,True],inplace=True)
    fig = go.Figure()
    for i,conf in enumerate(data['Conference'].unique()):
        dataPlot = data[data['Conference']==conf]
        fig.add_trace(go.Box(x=dataPlot['Name'], y=dataPlot['value'], name=str(conf), boxpoints='all', boxmean=True)) #boxpoints='outliers'
    
    fig.update_layout(
        updatemenus=[
            dict(
                # type="buttons",
                # name='Division',
                # direction="right",
                active=0,
                x=0.85,
                # xanchor='left',
                y=1.3,
                # yanchor='top',
                buttons=list([
                    dict(label="all",
                         method="update",
                         args=[{"visible": [True, True, True, True, True, True, True, True]},
                               {"title": 'Team Confidence Distribution'}]),
                    dict(label="AFC",
                         method="update",
                         args=[{"visible": [True, True, True, True, False, False, False, False]},
                               {"title": 'AFC Confidence Distribution'}]),
                                # "annotations": []}]),
                    dict(label="AFC East",
                         method="update",
                         args=[{"visible": [True, False, False, False, False, False, False, False]},
                               {"title": 'AFC East Confidence Distribution'}]),
                                # "annotations": []}]),
                    dict(label="AFC North",
                         method="update",
                         args=[{"visible": [False, True, False, False, False, False, False, False]},
                               {"title": 'AFC North Confidence Distribution'}]),
                                # "annotations": high_annotations}]),
                    dict(label="AFC South",
                         method="update",
                         args=[{"visible": [False, False, True, False, False, False, False, False]},
                               {"title": 'AFC South Confidence Distribution'}]),
                                # "annotations": low_annotations}]),
                    dict(label="AFC West",
                         method="update",
                         args=[{"visible": [False, False, False, True, False, False, False, False]},
                               {"title": 'AFC West Confidence Distribution'}]),
                                # "annotations": high_annotations + low_annotations}]),
                    dict(label="NFC",
                         method="update",
                         args=[{"visible": [False, False, False, False, True, True, True, True]},
                               {"title": 'NFC Confidence Distribution'}]),
                                # "annotations": []}]),
                    dict(label="NFC East",
                         method="update",
                         args=[{"visible": [False, False, False, False, True, False, False, False]},
                               {"title": 'NFC East Confidence Distribution'}]),
                                # "annotations": []}]),
                    dict(label="NFC North",
                         method="update",
                         args=[{"visible": [False, False, False, False, False, True, False, False]},
                               {"title": 'NFC North Confidence Distribution'}]),
                                # "annotations": high_annotations}]),
                    dict(label="NFC South",
                         method="update",
                         args=[{"visible": [False, False, False, False, False, False, True, False]},
                               {"title": 'NFC South Confidence Distribution'}]),
                                # "annotations": low_annotations}]),
                    dict(label="NFC West",
                         method="update",
                         args=[{"visible": [False, False, False, False, False, False, False, True]},
                               {"title": 'NFC West Confidence Distribution'}]),
                ]),
            )            
        ])
    
    fig.update_layout(title_text='<b>Team Confidence Distribution</b>',boxmode='group',
        legend=dict(orientation="v"),
        yaxis=dict(title_text='Confidence',range=[0,16.2], tickvals=[i for i in range(0,17,2)]),
        xaxis=dict(title_text='Team',tickangle=45))
    fig.add_annotation(xref='paper',yref='paper',x=.6,y=1.28,text='Division:',font=dict(size=14), showarrow=False)
    # fig.update_yaxes(title_text='Confidence',range=[0,16], tickvals=[i for i in range(0,17,2)])
    # fig.update_xaxes(title_text='Team')
    # fig.show()
    return fig



st.set_page_config(
    page_title="Confidence-League Dashbaord",
    page_icon=':bar_chart:',
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
<style>
    .dataframe-container {
        text-align: center;
}
</style>
""",
    unsafe_allow_html=True
) #this does not work

st.markdown(
    """
    <style>
        section[data-testid="stSidebar"] {
            width: 450px !important; # Set the width to your desired value
        }
    </style>
    """,
    unsafe_allow_html=True,
)


st.write('<style>div.block-container{padding-top:1rem;}</style>', unsafe_allow_html=True)
st.write('<style>div.block-container{padding-bottom:3rem;}</style>', unsafe_allow_html=True)

# def AlertBox(wht_msg):
#     styles = {'material-icons':{'color': '#FF0000'},
#             'text-icon-link-close-container': {'box-shadow': '#3896de 0px 4px'},
#             'notification-text': {'':''},
#             'close-button':{'':''},
#             'link':{'':''}}

#     popup(icon='info', 
#         textDisplay=wht_msg, 
#         externalLink='', 
#         url='#', 
#         styles=styles, 
#         key="foo")

#can text align specific columns
# st.markdown(
# """
# <style>
#     div[data-testid="column"]:nth-of-type(1)
#     {
#         border:1px solid red;
#     } 

#     div[data-testid="column"]:nth-of-type(2)
#     {
#         border:1px solid blue;
#         text-align: end;
#     } 
# </style>
# """,unsafe_allow_html=True
# )


#----------------------------------------------------------------------------------------------------------------------


today=datetime.today().date()
week, seasonWeeks, users, names, matchups = establishInputs(today)


selected = option_menu(None,
                        ['Selections', 'History', 'Dashboard'], 
        icons=['file-earmark-arrow-up', 'book', 'bar-chart-line'], menu_icon="cast", default_index=0,
                        orientation = 'horizontal')
if selected=='Selections' or selected=='Reset':
    sidebarState='Selections'
elif selected=='History':
    sidebarState='History'
elif selected=='Dashboard':
    sidebarState='Dashboard'


with st.sidebar:
    if sidebarState=='Selections':    
        st.header('How To Score')
        st.write('''Select the winner of each matchup. Then rank each one by how confident you are they will win, 
                 the highest number being the most confident. If you are correct, you will earn points corresponding to the ranking you assigned. 
                 As you make picks, the table at the bottom of the page under 'Selections' will populate.''')
        st.markdown("""<hr style="border-width: 3px;" />""", unsafe_allow_html=True)
        st.header('Submitting Selections')
        st.write('''To submit your results, select your name from the dropdown list, enter your 3 digit code, then hit the 'Submit Answers' button at the bottom of the page. 
                 This prevents users from entering results under the wrong name. You can resubmit to change your selections as many times as you would like before the week locks on Thursday at 5:00 CT.''')
        name = st.selectbox('Name', options=names, key='name', index=None)
        code = st.text_input('User Code',max_chars=3,key='code')
        st.markdown("""<hr style="border-width: 3px;" />""", unsafe_allow_html=True)
        st.header('Clearing Selections')
        st.write('''If you would like to reset all of your selections, you can do so by clicking the button below.  \nNOTES:  \nThis cannot be undone.  \nThis will not effect any previous submissions.''')
        if st.sidebar.button('Reset Selections'):
            for key in st.session_state.keys():
                if key=='name' or key=='code':
                    pass
                else:
                    del st.session_state[key]
            selected = 'Reset'
    elif sidebarState=='History':
        st.header('Previous Submissions')
        st.write('''Use this page to view submissions from yourself for this week, or any user from previous weeks.  \nTo 
                 view other users previous selections, just select their name from the dropdown and the week you want to view.  \nTo 
                 view your current selections for this week, select your name, enter your code, and select the current week.''')
        histName = st.selectbox('Name', options=names, key='histName', index=None)
        code = st.text_input('User Code',max_chars=3,key='code')
        listWeeks=seasonWeeks
        if code and histName: #only allow user to see their own current week selections
            if int(code)==users[histName]:
                listWeeks.append(week)
        histWeek = st.selectbox('Week',options=listWeeks,key='week',index=None)
        histPopulate = st.button('Populate')
        st.markdown("""<hr style="border-width: 3px;" />""", unsafe_allow_html=True)
        st.header('Note:')
        st.write('''You can switch between this page and the selections page freely without losing progress. 
                  The dropdowns on the selections page might not correctly load the values or appear blank, but your inputs will be retained. 
                  You can confirm this by checking the table at the bottom of the page.
                  (unfortunately there is nothing I can do about this due to platform limitations)''')
        st.write('''If you viewed your selections for this week on this page and have since submitted new selections, you will
                 need to refresh the browser page in order for the new selections to show up here.''')
    elif sidebarState=='Dashboard':
        # st.markdown("<h1 style='text-align: center; font-size: 16px;'><b>Dashboard:</b></h1>", unsafe_allow_html=True)
        st.header('Leaderboard:')
        st.write('''The graph shows who is in the top 5. The data to the right shows the rank of the selected user as well 
                 as any users selected in the 'Comparisons' multiselect. The top row automatically shows first and last place.''')
        st.markdown("""<hr style="border-width: 3px;" />""", unsafe_allow_html=True)
        st.header('League Data:')
        st.write('''Data for all users in the league is displayed here. Total points scored for each team across users, and confidence distributions
                 of the average rank for each team by week.''')
        st.markdown("""<hr style="border-width: 3px;" />""", unsafe_allow_html=True)
        st.header('User Data:')
        st.write('''Make a selection in the 'User' box below to see thier data. Select users from the 'Comparisons' multiselect box to add 
                 thier data to the 'Weekly Score Comparison' graph. A maximum of 3 additional users can be added.''')
        name = st.selectbox('User:', options=names, key='name', index=None)
        compNames = st.multiselect('Comparisons:', options=names, key='compNames', max_selections=3)
        compUsers={}
        # if 'userList' not in st.session_state:
        #     with open('User List.pk1','rb') as f:
        #         st.session_state.userList = pickle.load(f)
        # compUsers = {name: st.session_state.userList[name]}
        # compUsers.update({user: st.session_state.userList[user] for user in compNames})



if selected == 'Selections':            
    st.markdown(f"<h1 style='text-align: center; font-size: 50px;'>Week {week} Selections</h1>", unsafe_allow_html=True)
    st.markdown("""<hr style="border-width: 4px;" />""", unsafe_allow_html=True)
    
    if 'questions' not in st.session_state:
        st.session_state.questions = matchups
        st.session_state.answers = {}
        st.session_state.winners = {}
        st.session_state.numbers = []
        for i in range(1,len(matchups)+1):
            st.session_state.numbers.append(i)
    
    for i, question in enumerate(st.session_state.questions):
        winner = st.selectbox(f'Game {i+1} - {question}', options=question.split('/'), key=(i+1)*2-1, index=None)
        if winner:
            st.session_state.winners[question] = winner
    
        
        if question not in st.session_state.answers or st.session_state.answers[question] == 0:
            default_value = 0
        else:
            default_value = st.session_state.answers[question]
    
        options = list(st.session_state.numbers)
        
        if default_value != 0 and default_value not in options:
            options.append(default_value)
            options=sorted(options)
    
        selected_number = st.selectbox('Confidence', options=options, key=(i+1)*2, index=options.index(default_value) if default_value != 0 else None)
    
        if selected_number != 0 and selected_number:
            if question in st.session_state.answers and st.session_state.answers[question] != selected_number:
                st.session_state.numbers.append(st.session_state.answers[question])
                st.session_state.answers[question] = selected_number
                st.session_state.numbers.remove(selected_number)
            elif question not in st.session_state.answers:
                st.session_state.answers[question] = selected_number
                st.session_state.numbers.remove(selected_number)
        
        st.markdown("""<hr style="border-width: 4px;" />""", unsafe_allow_html=True)
     
        
    st.markdown("<h1 style='text-align: center; color: white; font-size: 40px;'>Selections</h1>", unsafe_allow_html=True)
    data = pd.DataFrame(columns=['Winner','Confidence'], index=matchups)
    data = data.rename_axis('Matchup')
    for key,value in st.session_state.winners.items():
        data.loc[key,'Winner'] = value
    for key,value in st.session_state.answers.items():
        data.loc[key,'Confidence'] = value
    dispData = data.reset_index()
    dispData[['Winner','Confidence']] = dispData[['Winner','Confidence']].astype(str) #so displayed data si not greyed out
    disp1 = dispData.head(8)
    disp2 = dispData.tail(-8)
    # disp1=data.head(8) #manipulate for display pourposes
    # disp2=data.tail(-8)    
    col1,col2=st.columns([1,1])
    with col1:
        # hold = disp1.reset_index()
        # # styledf = hold.style.set_properties(**{
        # #     'text-align': 'center'
        # #     })
        # st.markdown(hold.style.hide(axis='index').to_html(), unsafe_allow_html=True)
        # st.write(disp1, use_container_width=True, unsafe_allow_html=True)
        st.dataframe(disp1, hide_index=True, use_container_width=True) #try to cetner data in columns
    with col2:
        st.dataframe(disp2, hide_index=True, use_container_width=True)
    
    col1,col2,col3=st.columns([2,1,2])
    if col2.button('Submit Answers',use_container_width=True):
        if not name or not code:
            modalMessage='Please input user name and code in the sidebar.'
        elif any(data.iloc[:,0].isnull()) or any(data.iloc[:,1].isnull()):
            modalMessage='Please make all selections before submitting.'
        else:
            if int(code)==users[name]:
                if CheckTime(datetime.now(pytz.timezone('US/Central'))):
                    blob = getBlob(name, week)
                    with blob.open('w') as f:
                        f.write(data.to_csv(index=True))
                    modalMessage='Submission Successful!'
                else:
                    modalMessage='Invalid Submission: submission window is Tuesday 12:01am - Thursday 5:00pm Central'
            else:
                modalMessage='User name and code do not match.'
        submitModal = Modal(key='submitModal', title='Submission Status')
        with submitModal.container():
            st.markdown(f'{modalMessage}')
    

elif selected=='Reset':
    st.write('''Your selections have been cleared.  \\nDue to a bug in the platform software that has not been patched yet, 
             this needs to be done in two steps. Please hit the 'Reload' button and you will be returned to the selections page.''')
    if st.button('Reload'):
        selected='Selections'
        st.rerun()

elif selected=='History':
    if histPopulate:
        if histWeek==week: #current week selections from gogole cloud storage
            try:
                blob = getBlob(histName, histWeek)
                with blob.open('r') as f:
                    st.session_state.histData = pd.read_csv(f)
            except:
                histModal = Modal(key='histModal', title='Fetch Error')
                with histModal.container():
                    st.markdown('You have not submitted your selections for the week yet.')
        else: #previous week selections from userList pickle
            if 'userList' not in st.session_state:
                with open('User List.pk1','rb') as f:
                    st.session_state.userList = pickle.load(f)
            viewUser = st.session_state.userList[histName]
            st.session_state.histData = viewUser.Data.get(histWeek)
        st.session_state.dispName = histName #so displayed data doesnt change when sidebar state updated
        st.session_state.dispWeek = histWeek
        
    if 'histData' in st.session_state:
        st.markdown(f"<h1 style='text-align: center; font-size: 50px;'>{st.session_state.dispName} Week {st.session_state.dispWeek} Selections</h1>", unsafe_allow_html=True)
        # st.session_state.histData.set_index('Matchup', inplace=True)
        histDisp = st.session_state.histData.reset_index()
        histDisp[['Winner','Confidence']] = histDisp[['Winner','Confidence']].astype(str)
        histDisp1 = histDisp.head(8)
        histDisp2 = histDisp.tail(-8)
        # histDisp1 = st.session_state.histData.head(8)
        # histDisp2 = st.session_state.histData.tail(-8)
        col1,col2=st.columns([1,1])
        with col1:
            st.dataframe(histDisp1, hide_index=True, use_container_width=True)
        with col2:
            st.dataframe(histDisp2, hide_index=True, use_container_width=True)
    else:
        st.write("Enter information in the sidebar to view selections")


elif selected=='Dashboard':
    if 'userList' not in st.session_state:
        with open('User List.pk1','rb') as f:
            st.session_state.userList = pickle.load(f)
    if 'teamTotals' not in st.session_state:
        with open('Team Totals.pk1','rb') as f:
            st.session_state.teamTotals = pickle.load(f)
    if name:
        compUsers = {name: st.session_state.userList[name]}
    compUsers.update({user: st.session_state.userList[user] for user in compNames})
    
    # hold = st.session_state.teamTotals
    # st.dataframe(st.session_state.teamTotals,hide_index=True)
    st.markdown("<h1 style='text-align: center; font-size: 35px;'>Leaderboard</h1>", unsafe_allow_html=True)
    row1=st.columns([4,.5,4])
    with row1[0]:
        fig = UserLeader(st.session_state.userList)
        st.plotly_chart(fig,use_container_width=True)
    with row1[2]:
        # fig = TeamLeader(st.session_state.teamTotals)
        # st.plotly_chart(fig,use_container_width=True)
        #if name then show top, 3 either end, and bottom, else show top5 bottom 5
        data = [(user.Name,user.Total) for user in st.session_state.userList.values()]
        scores = pd.DataFrame(data, columns=['Name','Total'])
        scores.sort_values(by=['Total'], ascending=False,inplace=True)
        scores.reset_index(drop=True,inplace=True)
        scores.rename_axis('Ranking',inplace=True)
        # st.dataframe(scores.head(2),hide_index=True,use_container_width=True)
        # st.dataframe(scores.tail(2),hide_index=True,use_container_width=True)
        st.markdown("<h1 style='text-align: center; font-size: 16px;'>Selected User Ranking</h1>", unsafe_allow_html=True)
        midRow = st.columns([1,1])
        with midRow[0]:
            st.markdown(f"<h1 style='text-align: center; font-size: 16px;'><b>Rank 1: {scores.iloc[0,0]} --> {scores.iloc[0,1]} pts</b></h1>", unsafe_allow_html=True)
        with midRow[1]:
            st.markdown(f"<h1 style='text-align: center; font-size: 16px;'><b>Rank {len(scores)}: {scores.iloc[-1,0]} --> {scores.iloc[-1,1]} pts</b></h1>", unsafe_allow_html=True)
        st.markdown("""<hr style="border-width: 2px;" />""", unsafe_allow_html=True)
        bottomRow = st.columns([1,1])
        with bottomRow[0]:
            if compUsers:
                dispScores = scores[scores['Name'].isin(compUsers)]
                for ind in dispScores.index:
                    st.write(f'Rank {ind+1}: {dispScores["Name"][ind]} --> {dispScores["Total"][ind]}')
        with bottomRow[1]:
            st.download_button('Download User Rankings',scores.to_csv().encode('utf-8'),'Rankings.csv')
        # for n in compUsers.keys():
        #     rank = scores.Name[scores.Name==n].index.to_list()[0]+1
        #     # st.dataframe(scores.loc[scores["Name"]==n,"Total"])
        #     st.write(f'Rank {rank}: {n} --> {scores.loc[scores["Name"]==n,"Total"].values[0]}')
        # st.write(str(scores.Name[scores.Name=='Justice'].index.to_list()[0]+1))
    
    st.markdown("<h1 style='text-align: center; font-size: 35px;'>League Wide Data</h1>", unsafe_allow_html=True)
    row2=st.columns([4,.5,4])
    with row2[0]:
        # fig=TeamTotals(st.session_state.teamTotals)
        st.plotly_chart(TeamTotals(st.session_state.teamTotals),use_container_width=True)
    with row2[2]:
        # fig = TeamBox(st.session_state.teamTotals)
        st.plotly_chart(TeamBox(st.session_state.teamTotals),use_container_width=True)
    st.markdown("<h1 style='text-align: center; font-size: 35px;'>User Data</h1>", unsafe_allow_html=True)
    row3=st.columns([4,.5,4])
    if name:
        with row3[0]:
            # fig = UserWeeklyCompare(st.session_state.userList)
            # if compNames:    
            #     users = {name: st.session_state.userList[name]}
            #     users.update({user: st.session_state.userList[user] for user in compNames})
            #     st.plotly_chart(UserWeeklyCompare(users),use_container_width=True)
            # else:
            #     st.plotly_chart(UserWeeklyCompare({name: st.session_state.userList[name]}),use_container_width=True)
            st.plotly_chart(UserWeeklyCompare(compUsers),use_container_width=True)
        with row3[2]:
            # fig = UserTeamTotals({1:st.session_state.userList['Justice']})
            # fig = UserTeamTotals(st.session_state.userList['Justice']) 
            st.plotly_chart(UserTeamTotals(st.session_state.userList[name]),use_container_width=True)
        row4=st.columns([4,1,4])
        with row4[0]:
            # fig = UserConfidencePercent(st.session_state.userList['Justice'])
            st.plotly_chart(UserConfidencePercent(st.session_state.userList[name]),use_container_width=True)
        with row4[2]:
            # fig = UserBox(st.session_state.userList['Justice'])
            st.plotly_chart(UserBox(st.session_state.userList[name]),use_container_width=True)
    else:
        st.markdown("<h1 style='text-align: center; font-size: 16px;'><b>Select user to view stats</b></h1>", unsafe_allow_html=True)
    # st.dataframe(st.session_state.teamTotals,hide_index=True)
    
        

        
        
        