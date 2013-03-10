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
    def filterResults(self):
        for entry in self._results:
            entryOnList = self._userlist.get(entry.id)
            if entryOnList:
                epWatched = int(entry.episodeBeingWatched)
                epOnList = int(entryOnList.episodesSeen)
                diff = epWatched - epOnList
                if entryOnList.watchedStatus == "watching":
                    self._boostEntryInWatching(entry, diff)
                elif entryOnList.watchedStatus == "plan to watch":
                    self._boostEntryInPlanToWatch(entry)
                elif entryOnList.watchedStatus == "completed":
                    self._boostEntryInCompleted(entry)
                elif entryOnList.watchedStatus in ["on-hold", "dropped"]:
                    self._boostEntryInDropped(entry, diff)

    def _boostEntryInWatching(self, entry, diff):
        if diff == 1:
            entry.matchBoost += 6
        elif diff <= 3:
            entry.matchBoost += 4
        else:
            entry.matchBoost += 2.5

    def _boostEntryInPlanToWatch(self, entry):
        if int(entry.episodeBeingWatched) == 1:
            entry.matchBoost += 6
        else:
            entry.matchBoost += 2

    def _boostEntryInCompleted(self, entry):
        entry.matchBoost -= 0.1

    def _boostEntryInDropped(self, entry, diff):
        if diff == 1:
            entry.matchBoost += 2
