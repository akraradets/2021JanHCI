import random
import pylsl
import numpy as np
import pandas as pd
import time
import itertools
import math
import psychopy 
from psychopy import visual, core, event
from datetime import datetime
from IPython.display import clear_output
from playsound import playsound
from utils import balanced_latin_squares, get_filenames_in_path
import sys


if(len(sys.argv) == 1):
    raise ValueError(f"Must give order_index number in rage of 0 - 9")

order_index = int(sys.argv[1])

if(order_index not in range(10)):
    raise ValueError(f"Must give order_index number in rage of 0 - 9")

folder = 'sounds/'
screen_size = [1920, 1080]
# screen_size = [1366, 768]


categories = ['1','2','3','4','5']
conditions = []
stimuli = dict()
for cat in categories:
    l = get_filenames_in_path(f"{folder}{cat}")
    random.shuffle(l)
    stimuli[f"{cat}_1"] = l[:5]
    stimuli[f"{cat}_2"] = l[5:]
    conditions.append(f"{cat}_1")
    conditions.append(f"{cat}_2")

seq = balanced_latin_squares(10)[order_index]
# print(stimuli)
# raise ValueError()

#==============================================
# experiment parameters
#==============================================
total_image      = 50
num_trial        = 5
num_block        = int(total_image/num_trial)

stim_time        = 6 #second
stim_blink_time  = 0 #second
fixation_time    = 15  # inter trial interval, i.e., how long the fixation will stay in second

experiment_time  = (total_image * stim_time ) + ( (total_image-1)*stim_blink_time) + (num_block-1)*fixation_time
print(f"Total experiment time = {'{:.2f}'.format(experiment_time/60)} Minute" )
      
    
#==============================================
# Configuration
#==============================================
# image_folder='numerical_stimuli'


#name, type, channel_count, sampling rate, channel format, source_id
#info = StreamInfo('CytonMarkers', 'Markers', 1, 0.0, 'int32', 'CytonMarkerID')#make an outlet
info = pylsl.StreamInfo('CytonMarkers', 'Markers', 1, 0.0, 'string', 'CytonMarkerID')#make an outlet
outlet = pylsl.StreamOutlet(info)
# %whos

def drawTextOnScreen(massage) :
    message = visual.TextStim( mywin, text=massage, languageStyle='LTR')
    message.contrast =  0.3
    message.height= 0.07
    message.draw() # draw on screen
    mywin.flip()   # refresh to show what we have draw

def drawTrial( imgPath, mark, stimTime ) :
    drawTextOnScreen('') 
    core.wait(stim_blink_time)
    img = visual.ImageStim( mywin,  image=imgPath )
    img.size *= 1.5
    img.draw()
    mywin.flip()
    eegMarking(mark)
    core.wait(stimTime)
    
def playTrial(path, mark):
    eegMarking(mark)
    playsound(path)

def drawFixation(fixationTime):
    draw_blank_screen()
    eegMarking('-1')
    core.wait(fixationTime-0.5)
    drawTextOnScreen('')
    core.wait(0.5)

def draw_blank_screen():
    fixation = visual.ShapeStim(mywin,
                                vertices=((0, -0.5), (0, 0.5), (0,0), (-0.5,0), (0.5, 0)),
                                lineWidth=5,
                                closeShape=False,
                                lineColor="white"
            )
    fixation.draw()
    # if not(isTrianing) :
    # text = f"Block {block+1} / {len(blocks_imgs)}"
    # message = visual.TextStim( mywin, text=text, languageStyle='LTR' )
    # message.contrast =  0.3
    # message.pos = (0, -0.6)
    # message.draw() # draw on screen
        
    mywin.flip()   # refresh to show what we have draw
     
def eegMarking(markerString):   # use trial variable from main
    # if not isTrianing :
    # if stampType == "img_stim" :
    #     markerString = str(block+1) + "," + str(trial) + ","  + str(img)
    # elif stampType == "fixation" :
    #     markerString = str((block+1)*-1) + "," +str("Fixation") + "," + str("Fixation")
    # else:
    #     markerString = 'Training'
    # markerString= str(markerString)                              
    print("Marker string {}".format(markerString))
    outlet.push_sample([markerString])


mywin = visual.Window(screen_size, color="black", units='norm')     # set the screen and full screen mode
# mywin = visual.Window([1920, 1080], color="black", units='norm')    # set the screen and full screen mode

##############
####  Training session
# while True:
#     isTrianing = True
#     drawTextOnScreen('Training session, Press space bar to start')
#     keys = event.getKeys()
#     if 'space' in keys:      # If space has been pushed
#         start = time.time()
#         drawTextOnScreen('') 
#         trial = 1
#         for img in blocks_imgs[4]:
#             drawTrial(img, stim_time)   # drawTrail(fileName, stimTime, thinkingTime, fixationTime)

#             if trial == 3 :
#                 break
#             trial += 1

#         drawFixation(img, fixation_time)
#         drawTextOnScreen('End of training session')
#         core.wait(5)
#         isTrianing = False
#         break

        
################
####### Experiment session
        
while True:
    drawTextOnScreen('Experiment session : Press space bar to start')
    keys = event.getKeys()
    if 'space' in keys:      # If space has been pushed
        start = time.time()
        drawTextOnScreen('') 
        # draw_blank_screen()
        for round,block in enumerate(seq):
            drawTextOnScreen('')
            trial = 1
            # print(block)
            cat = conditions[block-1].split('_')[0]
            for imgName in stimuli[conditions[block-1]]:
                clear_output(wait=True)
                playTrial(f"{folder}/{cat}/{imgName}", f"{conditions[block-1]}_{trial}")   # drawTrail(fileName, stimTime, thinkingTime, fixationTime)
                trial += 1
            if round+1 < len(seq):  # do not draw fixation on last block
                drawFixation(fixation_time)
        drawTextOnScreen('End of experiment, Thank you')
        
        stop  = time.time()
        print(f"Total experiment time = {(stop-start)/60} ")
        core.wait(10)
        break
    
mywin.close()
