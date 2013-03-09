'''
Created on 9 Mar 2013

@author: Uriziel
'''
from BaseFilter import BaseFilter


class UserListStatusFilter(BaseFilter):
    '''
    Boost anime in watching.
    Huge boost for anime in watching if episode no. is being followed
    by the one currently watching.
    Huge boost if in plan to watch if episode == 1
    Smaller boost for different ep no.
    Small boost for anime in dropped if following episode
    Minimal minus boost for anime in completed
    '''
    SCORE_BOOST = 6

    def filterResults(self):
        for entry in self._results:
            entryOnList = self._userlist.get(entry.id)
            if entryOnList:
                dif = int(entry.episodeWatched) - int(entryOnList.episodesSeen)
                if entryOnList.watchedStatus == "watching":
                    if dif == 1:
                        entry.matchBoost += 6
                    elif dif <= 3:
                        entry.matchBoost += 4
                    else:
                        entry.matchBoost += 2.5
                elif entryOnList.watchedStatus == "plan to watch":
                    if int(entry.episodeWatched) == 1:
                        entry.matchBoost += 6
                    else:
                        entry.matchBoost += 1
                elif entryOnList.watchedStatus == "completed":
                    entry.matchBoost -= 0.1
                elif entryOnList.watchedStatus == "dropped":
                    if dif == 1:
                        entry.matchBoost += 1
