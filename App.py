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
from datetime import date
import pickle
import matplotlib.pyplot as plt
import plotly.express as px
#cd Documents\GitHub\Confidence-League
#streamlit run App.py
class User:
    def __init__(self, name):
        self.Name = name
        self.Data = {}
        self.Scores = {}
        self.Total = 0
        with open('C:/Users/Matt/Documents/Python Scripts/Confidence Users/Teams.pk1','rb') as f:
              self.Teams=pickle.load(f)
        with open('C:/Users/Matt/Documents/Python Scripts/Confidence Users/Confidences.pk1','rb') as f:
              self.Confidences=pickle.load(f)
        
    def AddWeek(self, week, data):
        self.Data[week] = data
    
    def Score(self, week, winners):
        data = self.Data.get(week)
        comparison = np.where(data['Winner']==winners['Winner'], data['Confidence'],0)
        self.Scores[week] = int(np.sum(comparison))
        self.Total=0
        for score in self.Scores.values():
            self.Total += score

    def TeamScores(self, WinnerList):
        self.Teams.iloc[:] = 0
        self.Confidences.iloc[:] = 0
        for week,winners in WinnerList.items():
            data = self.Data.get(week)
            self.Teams[f'Wk{week}'] = 0
            for i in range(0,len(data)): #update the numebr of occurences of each confidence for % correct and weekly track team rankings
                Con = int(data.iloc[i,2])
                self.Confidences.loc[Con,'Occurrences'] += 1
                team = data.iloc[i,1] #team assigned confidence
                self.Teams.loc[team, f'Wk{week}'] = Con
            Comparison = np.where(data['Winner']==winners['Winner'], data['Confidence'], 0) #gets confidence of each matchup
            for i in range(0,len(winners)):
                team = winners.iloc[i,1] #team that won
                self.Teams.loc[team,['Total']] += Comparison[i]
                if int(Comparison[i]) in self.Confidences.index: self.Confidences.loc[int(Comparison[i]),'Total'] += Comparison[i]
        self.Confidences['Correct'] = round(self.Confidences['Total'] / (self.Confidences['Occurrences'] * self.Confidences.index),2)
        hold = self.Teams[self.Teams.columns[2:]]
        self.Teams['Average'] = round(hold.mean(axis=1), 2)

@st.cache_resource
def loadBucket():
    credentials = service_account.Credentials.from_service_account_info(st.secrets)
    storage_client = storage.Client(project=st.secrets['project_id'], credentials=credentials)
    bucket = storage_client.bucket('current-selections')
    return bucket
# st.session_state.weekSubmissions = list(bucket.list_blobs())

@st.cache_resource
def getBlob(name,week):
    bucket = loadBucket()
    return bucket.blob(f'{name} Wk{week}.csv')

@st.cache_data
def establishInputs(today):
    startDate = date(2024,5,1)
    # today=date.today()
    week=(today-startDate).days//7
    seasonWeeks=[]
    for i in range(1,week):
        seasonWeeks.append(i)
    # df = pd.read_csv(f'Matchups/Matchups Wk{week}.csv')
    df = pd.read_csv('Matchups Wk1.csv')
    # matchups = df[f'Wk{week}'].tolist()
    matchups = df['Wk1'].tolist()
    userdf = pd.read_csv('Users.csv')
    users={}
    names=[]
    for i in range(0,len(userdf)):
        users[userdf.iloc[i,0]]=userdf.iloc[i,1]
        names.append(userdf.iloc[i,0])
    return week, seasonWeeks, users, names, matchups

def user_leader(userList):
    scores = pd.DataFrame(columns=['Total'])
    for name, user in userList.items():
        scores.loc[name,'Total'] = user.Total
    scores = scores.sort_values(by=['Total'], ascending=True)
    plotScores = scores.head(5).rename_axis('User')
    xmin = plotScores['Total'].min()-20
    xmax = plotScores['Total'].max()+20
    fig =px.bar(plotScores,x='Total',y=plotScores.index,orientation='h',title='User Leaderboard')
    fig.update_layout(xaxis_range=[xmin,xmax])
    st.plotly_chart(fig,use_container_width=True)
    # return fig

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


today=date.today()
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
                 need to reload the page in order for the new selections to show up here.''')
    elif sidebarState=='Dashboard':
        st.header('Dashboard')
        st.write('view different stats about the league')
        st.selectbox('Name', options=names, key='name', index=None)


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
                blob = getBlob(name, week)
                with blob.open('w') as f:
                    f.write(data.to_csv(index=True))
                modalMessage='Submission Successful!'
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
    
    st.markdown("<h1 style='text-align: center; font-size: 40px;'>Leaderboards</h1>", unsafe_allow_html=True)
    row1=st.columns([2,1,2])
    with row1[0]:
        user_leader(st.session_state.userList)
    st.markdown("<h1 style='text-align: center; font-size: 40px;'>User Data</h1>", unsafe_allow_html=True)
    
    
    st.markdown("<h1 style='text-align: center; font-size: 40px;'>Team Data</h1>", unsafe_allow_html=True)
            

        
        
        