# -*- coding: utf-8 -*-
"""
Created on Thu Apr 18 15:36:38 2024

@author: Matt
"""

import streamlit as st
from streamlit_option_menu import option_menu
# from streamlit_custom_notification_box import custom_notification_box as popup
from streamlit_modal import Modal
import pandas as pd
import numpy as np
from datetime import date
import pickle
#cd Documents\GitHub\Confidence-League
#streamlit run App.py
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


#----------------------------------------------------------------------------------------------------------------------

startDate = date(2024,4,1)
today=date.today()
week=(today-startDate).days//7
seasonWeeks=[]
for i in range(1,week):
    seasonWeeks.append(i)


df = pd.read_csv('Matchups Wk1.csv')
userdf = pd.read_csv('Users.csv')
users={}
for i in range(0,len(userdf)):
    users[userdf.iloc[i,0]]=userdf.iloc[i,1]
names = []
for key in users.keys():
    names.append(key)
matchups = df['Wk1'].tolist()


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
        currentWeekView=False
        if code and histName:
            if int(code)==users[histName]:
                listWeeks.append(week)
                # currentWeekView=True
        viewWeek = st.selectbox('Week',options=listWeeks,key='week',index=None)
        histPopulate = st.button('Populate')
        st.markdown("""<hr style="border-width: 3px;" />""", unsafe_allow_html=True)
        st.header('Note:')
        st.write('''You can switch between this page and the selections page freely if you are editing your selections for the week. 
                  The dropdowns on the selections page might not correctly load the values or appear blank, but your inputs will be retained. 
                  You can confirm this by checking the table at the bottom of the page.''')
    elif sidebarState=='Dashboard':
        st.header('DASHBOARD')
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
        # st.session_state.numbers = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16] #need to change to match number of matchups
    
    for i, question in enumerate(st.session_state.questions):
        winner = st.selectbox(f'Game {i+1} - {question}', options=question.split('/'), key=(i+1)*2-1, index=None)
        if winner:
            st.session_state.winners[question] = winner
    
        
        if question not in st.session_state.answers or st.session_state.answers[question] == 0:
            default_value = 0
        else:
            default_value = st.session_state.answers[question]
    
        options = [0] + list(st.session_state.numbers)
        
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
    disp1=data.head(8)
    disp2=data.tail(-8)
    col1,col2=st.columns([1,1])
    with col1:
        st.dataframe(disp1, use_container_width=True)
    with col2:
        st.dataframe(disp2,use_container_width=True)
    
    submitModal = Modal(key='submitModal', title='Submission Error')
    col1,col2,col3=st.columns([2,1,2])
    if col2.button('Submit Answers',use_container_width=True):
        if not name or not code:
            modalMessage='Please input user name and code in the sidebar.'
        elif any(data.iloc[:,0].isnull()) or any(data.iloc[:,1].isnull()):
            modalMessage='Please make all selections before submitting.'
        else:
            if int(code)==users[name]:
                #save score
                # submitPath = f'C:/Documents/GitHub/Confidence-League/Week Submissions/{name} Wk{week}.pk1'
                submitPath = f'Week Submitions\\{name} Wk{week}.pk1'
                with open(submitPath,'wb') as f:
                    pickle.dump(data,f)
                modalMessage='Submission Successful!'
            else:
                modalMessage='User name and code do not match.'
        with submitModal.container():
            st.markdown(f'{modalMessage}')
    

elif selected=='Reset':
    st.write('''Your selections have been cleared.  \\nDue to a bug in the platform software that has not been patched yet, 
             this needs to be done in two steps. Please hit the 'Reload' button and you will be returned to the selections page.''')
    if st.button('Reload'):
        selected='Selections'
        st.rerun()

elif selected=='History':
    st.write(viewWeek)
    # if currentWeekView:
    if viewWeek==week:
        #pull from pickled users
        fileName = histName + f' Wk{viewWeek}.pk1'
        if histPopulate:
            try:
                with open(fileName,'rb') as f:
                      histData=pickle.load(f)
            except:
                histModal = Modal(key='histModal', title='Fetch Error')
                with histModal.container():
                    st.markdown('You have not submitted your selections for the week yet.')
    else:
        #pull info out of userlist data
        st.write(histName)
        
        
        