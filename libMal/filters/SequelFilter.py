'''
Created on 9 Mar 2013

@author: Uriziel
'''
from BaseFilter import BaseFilter
from libMal._AnimeInfoExtractor import AnimeInfoExtractor
import re


class SequelFilter(BaseFilter):
    '''
    Try to figure out which season is this
    '''

    SCORE_BOOST = 3

    def boostIfSequel(self, sequelIndicators, entry, showName):
        if entry.prequels != None:
            entry.matchBoost += 1
#            print "Sequel boost +1: {}".format(entry.mainTitle)
            for si in sequelIndicators:
                si = "(" + si + ")"
                m1 = re.search(si, showName)
                for title in entry.titles:
                    m2 = re.search(si, title)
                    if m1 and m2 and m1.group(1) == m2.group(1):
                        entry.matchBoost += 2
#                        print "Sequel boost +2: {}".format(title)
                        break

    def filterResults(self):
        showName = AnimeInfoExtractor(self._filename).getName()
        sequelIndicators = [" II(?!I)", " III", "!!", "\d"]
        if self.isSequel(showName, sequelIndicators):
            for entry in self._results:
                self.boostIfSequel(sequelIndicators, entry, showName)

    def isSequel(self, showName, sequelIndicators):
        for si in sequelIndicators:
            if re.search(si, showName):
                return True
        return False
