'''
Created on 9 Mar 2013

@author: Uriziel
'''
from BaseFilter import BaseFilter


class FirstGoogleResultFilter(BaseFilter):
    '''
    Boost first results from google a little bit
    '''

    def filterResults(self):
        self._results[0].matchBoost += 1
        if(len(self._results) >= 2):
            self._results[1].matchBoost += 0.5
