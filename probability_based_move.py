from random import *
from AIMA.logic import *
from AIMA.utils import *
from AIMA.probability import *
from tkinter import messagebox

import logic_based_move
import copy

# =============================================================================
#   Function: PitWumpus_probability_distribution
#   Parameters:
#    - width: Width of the board
#    - height: Height of the board
#   
#   Returns: Join Distribution Probability table
#
#   Description: Creates the Join Distribution Probability table that contains 
#   all possible events
# =============================================================================

def PitWumpus_probability_distribution(self, width, height):
    PW_variables = [] 
    
    for column in range(1, width + 1):
        for row in range(1, height + 1):
            PW_variables = PW_variables + ['(%d,%d)' % (column, row)]

    #--------- Add your code here -------------------------------------------------------------------
    # getting room's size
    room_size = width*height
    
    # create the Joint Probability Distribution for all the rooms, setting each one to True or False
    joint_p = JointProbDist(PW_variables, {each: {True, False} for each in PW_variables})
    
    # Getting all possible combinations with the JPD that was just created
    events =  all_events_jpd(PW_variables, joint_p, {})   
    
    # Defining probability values for True and False
    p_true = 0.2                                                     
    p_false = 1 - p_true                                 
    
    # Loop through all the events and get the probability for every single one of them
    for event in events:
        
        true_count = sum(map((True).__eq__, event.values()))
        joint_p[event] = (p_true**true_count) * (p_false ** (room_size - true_count))
    
    # Return the JPD to the main program
    return joint_p
    
#---------------------------------------------------------------------------------------------------
 
####################################################################################################

# =============================================================================
#   Function: next_room_prob
#   Parameters:
#    - x: X coordinate of the agent's current possition
#    - y: Y coordinate of the agent's current possition
#   
#   Returns: A tuple containing the next room to move.
#
#   Description: This function loops through the surrounding rooms based on the 
#   agent's current possition. The function returns the surrounding room with 
#   less probability than the max probability threshold
# ============================================================================= 

def next_room_prob(self, x, y):
    #This list contains the hidden rooms
    hidden = []
    
    #Initializing the minimum probability assuming that is 1
    min_prob = 1
    
    #Getting the JPD table
    JDP = self.PitWumpus_probability_distribution(self.cave.WIDTH, self.cave.HEIGHT)
    
    #getting all the visited rooms
    visited = self.visited_rooms
    
    #getting all the room possitions of the known breeze/stench. True if there's a breeze, False if it doesn't
    knownBS = self.observation_breeze_stench(visited)
    
    #getting all the room possitions of the known Pit/Wumpus. True if there's a Pit/Wumpus, False if it doesn't
    knownPW = self.observation_pits(visited)
    
    #getting all the surrounding rooms according to the current possition
    surrounding_rooms = self.cave.getsurrounding(x,y)
    
    #getting the next room to move using logic based agent
    logic_based_room = self.next_room(x,y)
    
    #Initializing the new room to move
    new_room = (0,0)
    
    #Initializing the room that has min probability of having a Pit/Wumpus
    min_room = (0,0)
    
    #Appending all PW_Variables from PitWumpus_probability_distribution assuming that all the rooms are hidden
    for p in JDP.variables:
        hidden.append(p)
    
    #Removing all the visited rooms from hidden list
    for v in visited:
        #Converting to string since the rest of dictionaries (knownPW, knownBS) keys are strings
        v_room = '(' + str(v[0])+',' + str(v[1])+ ')' 
        for h in hidden:
            if h == v_room:
                hidden.remove(h)
                break

    #If next_room method from logic_based_move.py returns (0,0), use probability based move
    if logic_based_room == (0,0):
     #Loops through all the surrounding rooms that are not visited yet to get the probability of each surrounding room
     #The room with the less minimum probability and less than the maximum probability threshold (self.max_pit_probability)
     #is chosen to be the next room that the agent has to go to avoid any Pits or the Wumpus
        for s in surrounding_rooms:
            surrounding_room_probability = 0
            if s not in visited:
                #Since temp_hidden and temp_knownPw keys are strings, s_string converts the tuple in string
                s_string = '(' + str(s[0])+',' + str(s[1])+ ')'
                PValue = {}
                #Making deep copies of knownPW and hidden to not to alterate the original values
                temp_knownPw = copy.deepcopy(knownPW)
                temp_hidden = copy.deepcopy(hidden)
                
                #Assigning probability values for both True and False events
                for truth in [True, False]:
                    if s_string in temp_hidden:
                        temp_hidden.remove(s_string)
                    temp_knownPw[s_string] = truth
                    probevents = all_events_jpd(temp_hidden, JDP, temp_knownPw)
                    for e in probevents:
                        if self.consistent(knownBS, e) == 1:
                            #sum of each True and False probobilities
                            surrounding_room_probability = surrounding_room_probability + JDP[e] 
                    PValue[truth] = surrounding_room_probability
                    
                #normalization
                surrounding_room_probability = PValue[True]/(PValue[True]+PValue[False])
            
                if surrounding_room_probability < min_prob:
                     min_prob = surrounding_room_probability
                     min_room = s

        if min_prob < self.max_pit_probability:
            new_room = min_room
    else:
        new_room = logic_based_room
    
    return new_room
#---------------------------------------------------------------------------------------------------
 
####################################################################################################
