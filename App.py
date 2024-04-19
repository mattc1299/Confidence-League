# -*- coding: utf-8 -*-
"""
Created on Thu Apr 18 15:36:38 2024

@author: Matt
"""

import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import numpy as np
from datetime import date
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

startDate = date(2024,4,1)
today=date.today()
week=(today-startDate).days//7

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
                        ['Survey', 'Dashboard'], 
        icons=['house', 'award'], menu_icon="cast", default_index=0,
                        orientation = 'horizontal')
if selected=='Survey' or selected=='Reset':
    sidebarState='Survey'
elif selected=='Dashboard':
    sidebarState='Dashboard'


with st.sidebar:
    if sidebarState=='Survey':    
        st.header('INSTRUCTIONS')
        st.write('Select the winner of each matchup. Then rank each one by how confident you are they will win, 16 being the most confident and 1 being the least.')
        name = st.selectbox('Name', options=names, key='name', index=None)
        code = st.text_input('User Code',max_chars=3,key='Code')
        if st.sidebar.button('Reset Confidences'):
            for key in st.session_state.keys():
                if key=='name':
                    pass
                else:
                    del st.session_state[key]
            selected = 'Reset'
        
    elif sidebarState=='Dashboard':
        st.header('DASHBOARD')
        st.write('view different stats about the league')
        st.selectbox('Name', options=names, key='name', index=None)


if selected == 'Survey':            
    st.markdown(f"<h1 style='text-align: center; font-size: 50px;'>Week {week} Selections</h1>", unsafe_allow_html=True)
    
    if 'questions' not in st.session_state:
        st.session_state.questions = matchups
        st.session_state.answers = {}
        st.session_state.winners = {}
        st.session_state.numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10,11,12,13,14,15,16]
    
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
    displayData = pd.DataFrame(columns=['Winner','Confidence'], index=matchups)
    displayData = displayData.rename_axis('Matchup')
    for key,value in st.session_state.winners.items():
        displayData.loc[key,'Winner'] = value
    for key,value in st.session_state.answers.items():
        displayData.loc[key,'Confidence'] = value
    disp1=displayData.head(8)
    disp2=displayData.tail(-8)
    col1,col2=st.columns([1,1])
    with col1:
        st.dataframe(disp1, use_container_width=True)
    with col2:
        st.dataframe(disp2,use_container_width=True)
    
    col1,col2,col3=st.columns([2,1,2])
    if col2.button('Submit Answers',use_container_width=True):
        if not name or not code:
            st.write('Please input user name and code in the sidebar')
        else:
            if int(code)==users[name]:
                st.write('loading')
            else:
                st.write('User name and code do not match.')
    

    
elif selected=='Reset':
    st.write('this has to be done in two steps')
    if st.button('Reload'):
        selected='Survey'
        st.rerun()
