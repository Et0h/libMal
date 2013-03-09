'''
Created on 9 Mar 2013

@author: Uriziel
'''
from BaseFilter import BaseFilter


class FirstGoogleResultFilter(BaseFilter):
    '''
    Boost first result from google a little bit
    '''
    SCORE_BOOST = 1

    def filterResults(self):
        self._results[0].matchBoost += self.SCORE_BOOST
        if(len(self._results) >= 2):
            self._results[1].matchBoost += self.SCORE_BOOST / 2.0
#        print "Google Boost +1: {}".format(self._results[0].mainTitle)
#        print "Google Boost +0.5: {}".format(self._results[1].mainTitle)
