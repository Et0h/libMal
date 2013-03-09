'''
Created on 9 Mar 2013

@author: Uriziel
'''
import difflib
from BaseFilter import BaseFilter
from libMal._AnimeInfoExtractor import AnimeInfoExtractor


class MostSimilarNameFilter(BaseFilter):
    '''
    Boost first result from google a little bit
    '''
    SCORE_BOOST = 2

    def filterResults(self):
        showName = AnimeInfoExtractor(self._filename).getName()
        for entry in self._results:
            if difflib.get_close_matches(showName, entry.titles, 3, 0.9) != []:
                entry.matchBoost += 2
#                print "SimilarName boost +2: {}".format(entry.mainTitle)
