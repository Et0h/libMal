'''
Created on 9 Mar 2013

@author: Uriziel
'''
import difflib
from BaseFilter import BaseFilter
from libMal._AnimeInfoExtractor import AnimeInfoExtractor


class MostSimilarNameFilter(BaseFilter):
    '''
    Find titles that are similar to extracted show name
    '''
    def filterResults(self):
        showName = AnimeInfoExtractor(self._filename).getName()
        for entry in self._results:
            if difflib.get_close_matches(showName, entry.titles, 3, 0.9) != []:
                entry.matchBoost += 2
            if difflib.get_close_matches(showName, entry.titles, 3, 0.8) != []:
                entry.matchBoost += 0.5
