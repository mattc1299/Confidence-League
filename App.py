# -*- coding: utf-8 -*-
"""
Created on Thu Apr 18 15:36:38 2024

@author: Matt
"""

import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import numpy as np
#cd Documents\GitHub\Confidence-League
#streamlit run App.py


df = pd.read_csv('Matchups Wk1.csv')
userdf = pd.read_csv('Users.csv')
users={}
for i in range(0,len(userdf)):
    users[userdf.iloc[i,0]]=userdf.ilov[i,1]
names = []
for key in users.keys():
    names.append(key)
Matchups = df['Wk1'].tolist()


selected = option_menu(None,
                        ['Survey', 'Data'], 
        icons=['house', 'award'], menu_icon="cast", default_index=0,
                        orientation = 'horizontal')
st.title('Confidence League Weekly Selections')
with st.sidebar:
    st.header('INSTRUCTIONS')
    st.write('Select the winner of each matchup. Then rank each one by how confident you are they will win, 16 being the most confident and 1 being the least.')
    st.selectbox('Name', options=names, key='name', index=None)
if st.sidebar.button('Reset Confidences'):
    # st.session_state.questions = Matchups #["Question 1", "Question 2", "Question 3", "Question 4", "Question 5"]
    # st.session_state.answers = {}
    # st.session_state.winners = {}
    # st.session_state.numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10,11,12,13,14,15,16]
    # for i, question in enumerate(st.session_state.questions):
    #     st.write(f'Game {i+1} - {question}')
    #     winner = st.selectbox('', options=[''], key=(i+1)*2-1, index=None)
    # placeholder=st.empty()
    # placeholder.empty()
    
    for key in st.session_state.keys():
        if key=='name':
            pass
        else:
            del st.session_state[key]
    selected = 'Reset'


if selected == 'Survey':            
    
    if 'questions' not in st.session_state:
        st.session_state.questions = Matchups
        st.session_state.answers = {}
        st.session_state.winners = {}
        st.session_state.numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10,11,12,13,14,15,16]
    
    for i, question in enumerate(st.session_state.questions):
        #question=str(question)
        # winner_placeholder = st.empty()
        # if len(st.session_state.winners)<1:
        #     with st.empty():
        #         winner = st.selectbox(f'Game {i+1} - {question}', options=question.split('/'), key=(i+1)*2-1, index=None)
        # else:
        #     winner = st.selectbox(f'Game {i+1} - {question}', options=question.split('/'), key=(i+1)*2-1, index=None)
    
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
            # st.rerun()
    st.write(st.session_state.answers)
    st.write(st.session_state.winners)


    
elif selected=='Reset':
    # selected='Survey'
    # st.write('Reloading...')
    st.write('this has to be done in two steps')
    if st.button('Reload'):
        selected='Survey'
        st.rerun()
        
        
        
    
    # col1, col2 = st.columns([1,1])
    # with col1:
    #     if st.button('Yes', key='Yes'):
    #         selected='Survey'
    #         st.rerun()
    # with col2:
    #     if st.button('No', key='No'):
    #         selected='Survey'
            
