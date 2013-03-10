'''
Created on 9 Mar 2013

@author: Uriziel
'''


class BaseFilter(object):
    '''
    Base class for filters
    '''
    def __init__(self, filename, userlist, searchResults, options={}):
        self._filename = filename
        self._userlist = userlist
        self._results = searchResults
        self._options = options

    def filterResults(self):
        pass
