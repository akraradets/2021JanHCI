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

#==============================================
# experiment parameters
#==============================================
total_image      = 500
num_trial        = 20
num_block        = int(total_image/num_trial)

stim_time        = 0.5
stim_blink_time  = 0.3
fixation_time    = 5  # inter trial interval, i.e., how long the fixation will stay in second


experiment_time  = (total_image * stim_time ) + ( (total_image-1)*stim_blink_time) + (num_block-1)*fixation_time
print(f"Total experiment time = {'{:.2f}'.format(experiment_time/60)} Minute" )
      
    
#==============================================
# Configuration
#==============================================
image_folder='numerical_stimuli'


#name, type, channel_count, sampling rate, channel format, source_id
#info = StreamInfo('CytonMarkers', 'Markers', 1, 0.0, 'int32', 'CytonMarkerID')#make an outlet
info = pylsl.StreamInfo('CytonMarkers', 'Markers', 1, 0.0, 'string', 'CytonMarkerID')#make an outlet
outlet = pylsl.StreamOutlet(info)
# %whos


def genNumbers(num):
    trial_sequence = []
    for loop in range(int(num/10)):
        sequence = np.arange(10)
        trial_sequence.extend(sequence)
    random.shuffle(trial_sequence)
    return trial_sequence


# find the 2 consecutive
def findConsecutive(data):
    for loop_i in range(len(data)):
        if loop_i <= (len(data)-2) :
            if data[loop_i] == data[loop_i+1] :
                fixConsecutive(data, loop_i+1)

# find the positon that can swap
def fixConsecutive(data, position):
    if position <= ( len(data) -2 ) :
        counter = len(data) - position
        for ii in range(counter) :
            if data[position] != data[position+ii] :
                # swap
                swapPositions(data,position, position+ii )
                return
            
# swap 2 value
def swapPositions(list, pos1, pos2): 
    list[pos1], list[pos2] = list[pos2], list[pos1] 
#     print(f"swap index {pos1} <-> {pos2}")
    return 


# check 2 consecutive value
def checkConsecutive(data):
    num_consecutive = 0
    for loop_i in range(len(data)):
        if loop_i <= (len(data)-2) :
            if data[loop_i] == data[loop_i+1] :
#                 print(f"Consecutive found : {loop_i}<->{loop_i+1} , value {data[loop_i]} " )
                num_consecutive = num_consecutive+1
    return num_consecutive


# generate 0-9 for 1000 value
trials = genNumbers(total_image)
# print(trials)

if checkConsecutive(trials) :
    print(f"First consecutive check : There is some consecutive number in the list")
    # find and fix consecutive number
    findConsecutive(trials)

if checkConsecutive(trials) :
    print(f"Second check : There is still two same consecutive number in the list")
    findConsecutive(trials)
else :
    print(f"Second consecutive check : PASS")

if checkConsecutive(trials) :
    print(f"Third check : There is still two same consecutive number in the list")
    findConsecutive(trials)
else :
    print(f"Third consecutive check : PASS")

blocks_imgs = np.reshape(trials, (-1,num_trial))
# blocks_imgs
    

def drawTextOnScreen(massage) :
    message = visual.TextStim( mywin, text=massage, languageStyle='LTR')
    message.contrast =  0.3
    message.height= 0.07
    message.draw() # draw on screen
    mywin.flip()   # refresh to show what we have draw

def drawTrial( fileName, stimTime ) :
    imgPath=image_folder+"/"+str(fileName)+".png"
    drawTextOnScreen('') 
    core.wait(stim_blink_time)
    img = visual.ImageStim( mywin,  image=imgPath )
    img.size *= 1.5
    img.draw()
    mywin.flip()
    eegMarking(fileName, "img_stim" )
    core.wait(stimTime)
    
def drawFixation(fileName, fixationTime):
    fixation = visual.ShapeStim(mywin,
                                vertices=((0, -0.5), (0, 0.5), (0,0), (-0.5,0), (0.5, 0)),
                                lineWidth=5,
                                closeShape=False,
                                lineColor="white"
            )
    fixation.draw()
    if not(isTrianing) :
        text = f"Block {block+1} / {len(blocks_imgs)}"
        message = visual.TextStim( mywin, text=text, languageStyle='LTR' )
        message.contrast =  0.3
        message.pos = (0, -0.6)
        message.draw() # draw on screen
        
    mywin.flip()   # refresh to show what we have draw
    eegMarking(fileName, "fixation" )
    core.wait(fixationTime-0.5)
    drawTextOnScreen('')
    core.wait(0.5)
     
def eegMarking(img, stampType):   # use trial variable from main
    if not isTrianing :
        if stampType == "img_stim" :
            markerString = str(block+1) + "," + str(trial) + ","  + str(img)
        elif stampType == "fixation" :
            markerString = str((block+1)*-1) + "," +str("Fixation") + "," + str("Fixation")
    else:
        markerString = 'Training'
    markerString= str(markerString)                              
    print("Marker string {}".format(markerString))
    outlet.push_sample([markerString])


mywin = visual.Window([1366, 768], color="black", units='norm')     # set the screen and full screen mode
# mywin = visual.Window([1920, 1080], color="black", units='norm')    # set the screen and full screen mode

##############
####  Training session
while True:
    isTrianing = True
    drawTextOnScreen('Training session, Press space bar to start')
    keys = event.getKeys()
    if 'space' in keys:      # If space has been pushed
        start = time.time()
        drawTextOnScreen('') 
        trial = 1
        for img in blocks_imgs[4]:
            drawTrial(img, stim_time)   # drawTrail(fileName, stimTime, thinkingTime, fixationTime)

            if trial == 3 :
                break
            trial += 1

        drawFixation(img, fixation_time)
        drawTextOnScreen('End of training session')
        core.wait(5)
        isTrianing = False
        break

        
################
####### Experiment session
        
while True:
    drawTextOnScreen('Experiment session : Press space bar to start')
    keys = event.getKeys()
    if 'space' in keys:      # If space has been pushed
        start = time.time()
        drawTextOnScreen('') 
        
        for block in range(len(blocks_imgs)) :
            trial = 1
            for img in blocks_imgs[block]:
                clear_output(wait=True)
                drawTrial(img, stim_time)   # drawTrail(fileName, stimTime, thinkingTime, fixationTime)
                trial += 1
            if block != num_block:  # do not draw fixation on last block
                drawFixation(img, fixation_time)
        drawTextOnScreen('End of experiment, Thank you')
        
        stop  = time.time()
        print(f"Total experiment time = {(stop-start)/60} ")
        core.wait(10)
        break
    
mywin.close()
