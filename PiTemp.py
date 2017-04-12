#!/usr/bin/env python
# Imports
from __future__ import print_function
import subprocess
import time
import sys
from apscheduler.schedulers.background import BackgroundScheduler

# Funtions
class PiTempLogic(object):
    def __init__(self):
        self.avgTotal = 0
        self.avgCount = 0
        self.statsTrack = False
        self.maxTemp = 0
        self.minTemp = 1000

    def readTemp(self):
        #get temp
        temp = self.getTemp()
        if temp is None:
            print("Temp error")
            return
        #clean line (incase longer string in previous print)
        print("\r                           ", end="")
        #print temp
        print("\r" + str(temp) + "*C", end="")
        #flush temp to screen
        sys.stdout.flush()
        #add stats if required
        if self.statsTrack:
            self.updateStats(temp)

    def getTemp(self):
        #read temp
        rawOutput = subprocess.check_output(['vcgencmd', 'measure_temp'])
        startIndex = rawOutput.find('=')
        stopIndex = rawOutput.find('\'')
        if startIndex == -1 or stopIndex == -1:
            return None
        try:
            return float(rawOutput[startIndex + 1 : stopIndex])
        except ValueError:
            return None

    def updateStats(self, currentTemp):
        if currentTemp < self.minTemp:
            self.minTemp = currentTemp
        if currentTemp > self.maxTemp:
            self.maxTemp = currentTemp
        self.avgTotal += currentTemp
        self.avgCount += 1
        #incase someone tries to overflow
        if self.avgCount > 1000:
            self.avgTotal = self.avgTotal / self.avgCount
            self.avgCount = 1

    def printHelp(self):
        #print version
        print("PiTemp 0.0.1")
        #print usage
        print("Usage:")
        print(" python PiTemp.py [options]")
        #print options
        print("Options:")
        print(" -h  This help text")
        print(" -i [s] Sets interval of refresh timer in seconds (s)")
        print(" -s Prints min, max and average temperatures at exit")
        sys.exit(0)
        
# Vars
timer = 1
l = PiTempLogic()

# Main Program
#handle options/arguments
# -h
try:
    argIndex = sys.argv.index("-h")
    # print manual
    l.printHelp()
except ValueError:
    pass
# -i
try:
    argIndex = sys.argv.index("-i")
    #check if float
    try:
        timer = float(sys.argv[argIndex + 1])
        if timer < 0.1:
            timer = 0.1
            print("Lowest interval value is 0.1s")
    except ValueError:
        print("Not a valid interval timer argument")
except ValueError:
    pass
# -s
try:
    argIndex = sys.argv.index("-s")
    l.statsTrack = True
except ValueError:
    pass

#print timer setting
print("Refresh interval is set to " + str(timer) + "s")
#print esc action
print("Press ctrl+c to exit")
#print a first temp
l.readTemp()
#read temp every interval of scheduler
s = BackgroundScheduler()
s.add_job(l.readTemp, 'interval', seconds=timer)
s.start()

#loop program till esc action
try:
    while True:
        time.sleep(100)
except (KeyboardInterrupt, SystemExit):
    # kill scheduler
    s.shutdown()
    #print line
    print("")
    sys.stdout.flush()
    #print stats if required
    if l.statsTrack:
        print("Max temp: " + str(l.maxTemp) + "*C\tMin temp: " + str(l.minTemp) + "*C\tAverage temp: " + str(round(l.avgTotal / l.avgCount, 2)) + "*C" )