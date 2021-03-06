###############################################################################
# timer.py        Version 1.4     19-Nov-2014     Bill Manaris

###########################################################################
#
# This file is part of Jython Music.
#
# Copyright (C) 2014 Bill Manaris
#
#    Jython Music is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 2 of the License, or
#    (at your option) any later version.
#
#    Jython Music is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Jython Music.  If not, see <http://www.gnu.org/licenses/>.
#
###########################################################################

#
# Timer classes to schedule repeated tasks to be executed.
#
# REVISIONS:
#
#   1.4     19-Nov-2014 (bm) Fixed bug in cleaning up objects after JEM's stop button is pressed -
#                       if list of active objects already exists, we do not redefine it - thus, we 
#                       do not lose older objects, and can still clean them up.
#
#   1.3     06-Nov-2014 (bm)  Added functionality to stop timers via JEM's Stop button
#                       - see registerStopFunction().
#
#   1.2     25-Oct-2014 (bm)  Added EnvelopeTimer which calls a provided function
#                       giving it specified values at specified times.
#
#   1.1     12-Mar-2014 (bm)  Added OscillatorTimer which calls a provided function
#                       giving it an oscillating value at timed intervals.
#


from java.awt.event import *


# used to keep track which timers are active, so we can turn them off when
# JEM's Stop button is pressed - this way everything timed to happen into
# the future (notes, animation, etc.) stops

try:

   __ActiveTimers__         # if already defined (from an earlier run, do nothing, as it already contains material)
   
except:

   __ActiveTimers__  = []   # first run - let's define it to hold active objects


###############################################################################

# TimerListener
#
# Listener for Timer objects.  eventHandler is called when the timer interval expires.
# Extends Swing's ActionListener class.

class TimerListener(ActionListener):
   """
   Event handler for timer events
   """

   def __init__(self, eventFunction, parameters=[]):
      """
      Points this listener to eventFunction when the timer interval expires.
      """
      self.eventFunction = eventFunction
      self.parameters = parameters

   def actionPerformed(self, event = None):
      """
      Call the eventFunction.
      """
      # call the function with the specified parameters 
      # (see http://docs.python.org/2/tutorial/controlflow.html#unpacking-argument-lists)
      self.eventFunction(*self.parameters)  


###############################################################################
# Timer
#
# Class for creating a timer (for use to schedule tasks to be executed after 
# a given time interval, repeatedly or once).
#
# Methods:
#
# Timer( timeInterval, function, parameters, repeat)
#   Creates a new Timer to call 'function' with 'parameters', after 'timeInterval' (if 'repeat'
#   is True this will go on indefinitely (default); False means once.  
#   It uses either Swing's Timer.
#
# start()
#   Starts the timer.
#
# stop()
#   Stops the timer.
#
# isRunning()
#   Returns True if timer is running; False otherwise.
#
# stop()
#   Stops the timer.
#
# setRepeats( flag )
#   Sets the repeat attribute of the timer (True means repeat; False means once).
#####################################################################################

from javax.swing import Timer as JTimer

class Timer(JTimer):
   """Timer used to schedule tasks to be run at fixed time intervals."""
   
   def __init__(self, timeInterval, function, parameters=[], repeat=True):
      """Specify time interval (in milliseconds), which function to call when the time interval has passed
         and the parameters to pass this function, and whether to repeat (True) or do it only once."""
         
      self.timeListener = TimerListener(function, parameters)    # define the timer event listener and provide function and parameters to be called 
      
      JTimer.__init__(self, int(timeInterval), self.timeListener)
      self.setRepeats( repeat )      # should we do this once or forever? 
      
      # remember that this timer has been created and is active (so that it can be stopped/terminated by JEM, if desired)
      __ActiveTimers__.append(self)
      

   def setFunction(self, function, parameters=[]):
      """Sets the function to execute.  The optional parameter parameters is a list of parameters to pass to the function (when called)."""
      self.timeListener.eventFunction = eventFunction
      self.timeListener.parameters = parameters

   def getRepeat(self):
      """Returns True if timer is set to repeat, False otherwise."""
      return self.isRepeats()

   def setRepeat(self, flag):
      """Timer is set to repeat if flag is True, and not to repeat if flag is False."""
      self.setRepeats( flag )   # set the repeat flag
      self.start()              # and start it (in case it had stopped)


#####################################################################################

class EnvelopeTimer:
   """It calls a provided function giving it specified values at specified times.
      The values to use and the times to call the function come from an envelope.
      The envelope consists of values [v1, v2, ..., vn], and times, [t1, t2, ..., tn] ], 
      where vn is a value and tn is the time to call the provided function with the vn value.

      It may be used to fluctuate volume, panning, or frequency of sounds, among many other things.
      
      EnvelopeTimer(function, values, times, repeat)
      
      For example, given an AudioSample a, 
      
      EnvelopeTimer(function=a.setVolume, values=[0, 50, 127], times=[0, 10, 105], repeat=True)
                    
      will update the volume of sound a at the given settings and times.
      
      This function is passed one argument, namely the current value of the envelope.
      If the function expects, say, two arguments (e.g., circle.setPosition(x, y) ),
      then the envelope values should specify values accordingly, e.g., [(10, 20), ...].
   """
   
   def __init__(self, function, values, times, repeat=False):
      """Specify a 'function' to call with 'values' and at 'times', with 'repeat' specifying if to cycle.
          
         This function is passed on argument, namely the current value of the envelope.
         If the function expects more arguments, specify them in the envelope values as tuples.
      """
         
      self.function = function    
      self.envelopeValues = values
      self.envelopeTimes  = times
      self.repeat = repeat

      # check envelope format (are lists parallel?)
      if len( self.envelopeValues ) != len( self.envelopeTimes ):
         raise ValueError("The envelope needs parallel values and times -- sublists " \
                          + str(self.envelopeValues) + " and " + str(self.envelopeTimes) \
                          + " do not have the same length.")
      
      # remember how many envelope points are there
      self.numEnvelopePoints = len( self.envelopeTimes )   

      # check envelope format (are times increasing?)
      for i in range( self.numEnvelopePoints-1 ):
         # check if two consecutive times are increasing
         if self.envelopeTimes[i] >= self.envelopeTimes[i+1]:
            raise ValueError("The envelope needs increasing times -- sublist " + str(self.envelopeTimes) \
                             + " should consist of increasing absolute times (in milliseconds).")

      # find the minimum tick needed (how often to check elapsed time) - for efficiency
      self.tick = reduce(self.__gcd__, self.envelopeTimes)     # how often to check elapsed time

      self.elapsedTime = 0         # accumulates total elapsed time
      self.envelopeIndex = 0       # remembers which envelope entry comes next
      
      # check how to pass arguments to function
      self.envelopeValuesAreTuples = type(self.envelopeValues[0]) == type([]) or type(self.envelopeValues[0]) == type(())  # list or tuple?
      
      # remember if we are paused
      self.hasPaused = False
       
      # define timer
      self.timer = Timer(self.tick, self.__advance__, [], True)    # keep repeating (remember, __advance()__ handles envelope repeat)

      # remember that this timer has been created and is active (so that it can be stopped/terminated by JEM, if desired)
      __ActiveTimers__.append(self)
      
         
   def __advance__(self):
      """It calls the callback function with the current envelope value, if enough time has elapsed."""
      
      self.elapsedTime += self.tick

      # do we have more envelope points?
      if self.envelopeIndex < self.numEnvelopePoints:

         # is it time to call function?
         if self.elapsedTime >= self.envelopeTimes[ self.envelopeIndex ]:
      
            # yes, so check how many arguments to pass
            if self.envelopeValuesAreTuples:                 
               # envelope values are typles (or lists), unpack them when calling function
               self.function( *self.envelopeValues[ self.envelopeIndex ] )            
            else:
               # envelope values are atomic, so call function with a single argument
               self.function( self.envelopeValues[ self.envelopeIndex ] )            
         
            # we have served this envelope point, so let's go to next one (if any)
            self.envelopeIndex += 1
         
      elif self.repeat:   # we have finished all envelope points, so check if to repeat
      
         # yes, so reset
         self.elapsedTime = 0
         self.envelopeIndex = 0
         
      else:   # we have finished all envelope points, and not repeat is needed
      
         # shut down
         self.stop()


   def start(self):
      """(Re)start EnvelopeTimer to begin calling function."""
      self.elapsedTime = 0     # reset
      self.envelopeIndex = 0
      self.timer.start()
   
   def stop(self):
      """Stop envelopeTimer."""
      self.elapsedTime = 0     # reset
      self.envelopeIndex = 0
      self.timer.stop()
   
   def pause(self):
      """Pause EnvelopeTimer, so it may be resume (if desired)."""
      self.hasPaused = True
      self.timer.stop()
   
   def resume(self):
      """Resume envelopeTimer from where it was paused."""
      self.timer.start()
      self.hasPaused = False
      
   def isRunning(self):
      """Returns True if timer is running (has been started), False otherwise."""
      return self.timer.isRunning()

   def isPaused(self):
      """Returns True if timer is paused, False otherwise."""
      return self.hasPaused
   
   # Helper function - calculates the greatest common divisor between two numbers
   # (used to find the maximum time tick to advance, given all specified envelope times - for efficiency)
   def __gcd__(self, a, b):
      while b != 0:
         (a, b) = (b, a%b)
      return a


#####################################################################################
from music import mapValue
from math import cos, pi

class OscillatorTimer:
   """It calls a provided function giving it an oscillating value at timed intervals.
      It may be used to fluctuate volume, panning, or frequency of sounds, among other things.
   """
   
   def __init__(self, delay, minValue, maxValue, step, function):
      """Specify a time interval ('delay', in milliseconds), the min and max values within which to oscillate,
         the 'step' increment by which to advance the oscillating value at every time interval, and finally
         the function to call when the time interval has passed.  
         This function is passed on argument, namely the current value of the oscillator.
      """
         
      self.minValue = minValue     # the lowest point of the oscillating value
      self.maxValue = maxValue     # the highest point of the oscillating value
         
      self.function = function     # the function to call passing it the oscillating value
        
      # initialize oscillation
      self.oscillatorPhase  = 0.0  # ranges from -0 to 2*pi
      self.oscillatingValue = mapValue( cos(self.oscillatorPhase), -1.0, 1.0, self.minValue, self.maxValue)
         
      # convert the step increment to an angle/phase increment (in radians)  
      # NOTE: 'step' is allowed to range be between 0 and self.maxValue-self.minValue - as anything smaller
      #       or larger does not make much sense.
      self.stepPhase = mapValue(step, 0.0, self.maxValue-self.minValue, 0.0, 2*pi)
         
      # define timer
      self.timer = Timer(delay, self.__oscillate__, [], True)
         
      # remember that this timer has been created and is active (so that it can be stopped/terminated by JEM, if desired)
      __ActiveTimers__.append(self)
      

   def __oscillate__(self):
      """It calls callback function with current oscillator value, and calculates next oscillator value."""
      
      # ***
      #print "phase =", self.oscillatorPhase, ", value =", self.oscillatingValue
      
      self.function( self.oscillatingValue )
      
      # advance angle and wrap around
      self.oscillatorPhase  = (self.oscillatorPhase + self.stepPhase) % (2*pi)
      
      # caclulate new oscillation value 
      self.oscillatingValue = mapValue( cos(self.oscillatorPhase), -1.0, 1.0, self.minValue, self.maxValue)

   def start(self):
      """Start oscillator and begin calling function."""
      self.timer.start()
   
   def stop(self):
      """Stop oscillator."""
      self.timer.stop()
   
   def setDelay(self, delay):
      """Set time interval to wait before advancing oscillating value."""
      self.timer.setDelay(delay)
   
   def getDelay(self):
      """Get current time interval to wait before advancing oscillating value."""
      return self.timer.getDelay()
               

######################################################################################
# If running inside JEM, register function that stops everything, when the Stop button
# is pressed inside JEM.
######################################################################################

# function to stop and clean-up all active timers
def __stopActiveTimers__():

   global __ActiveTimers__

   # first, stop them
   for timer in __ActiveTimers__:
      timer.stop()

   # then, delete them
   for timer in __ActiveTimers__:
      del timer

   # also empty list, so things can be garbage collected
   __ActiveTimers__ = []   # remove access to deleted items   

# now, register function with JEM (if possible)
try:

    # if we are inside JEM, registerStopFunction() will be available
    registerStopFunction(__stopActiveTimers__)   # tell JEM which function to call when the Stop button is pressed

except:  # otherwise (if we get an error), we are NOT inside JEM 

    pass    # so, do nothing.



#################### Unit Testing ##############################

if __name__ == '__main__':

   ###### create an timer object ######
   seconds = 0    # hold seconds passed
   def echoTime():
      
      global seconds
      
      print seconds
      seconds = seconds + 1  # update time
      
   # define timer to count and output elapsed time (in seconds)
   t = Timer(1000, echoTime, [], True)
   t.start()
   