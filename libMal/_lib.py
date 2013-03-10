import urllib
import urllib2
import json
import base64
from ._pygoogle import pygoogle
from . import AnimeInfoExtractor
import re
from libMal.filters.FirstGoogleResultFilter import FirstGoogleResultFilter
from libMal.filters.SequelFilter import SequelFilter
from libMal.filters.MostSimilarNameFilter import MostSimilarNameFilter
from libMal.filters.UserListStatusFilter import UserListStatusFilter


class Manager(object):
    '''
    Support for updating anime list on MAL
    '''
    def __init__(self, username, password):
        self._username = username
        self._password = password
        self._animelist = None

    def findEntriesOnMal(self, filename, options={}):
        '''
        Look for shows that are probably associated with filename
        Ordered by best match
        @return: list of libMal.Entry
        @param filename: Name of file played
        @param options: Dict of options, usually you're fine with defaults.
            Options consisting of:
            "extractor": instance compatible with libMal.AnimeInfoExtractor
            "finder": instance compatible with libMal.Finder
            "list_fetcher": instance compatible with libMal.ListFetcher
            "filterer": instance compatible with libMal.ResultsFilterer
        '''
        animeName, ep = self._extractDataFromFilename(filename, options)
        finder = options.get("finder", Finder())
        malEntries = finder.find(animeName, ep)
        listFetcher = options.get("list_fetcher", ListFetcher(self._username))
        self._animelist = listFetcher.fetch()
        filterer = options.get("filterer", ResultsFilterer(self._animelist,
                                                          animeName, filename))
        results = filterer.scoreEntries(malEntries)
        return results

    def updateEntryOnMal(self, entry, options={}):
        '''
        Update user's list with given entry
        Best to use with libMal.Manager.findEntriesOnMal
        @param entry: Properly initialised libMal.Entry
        @param options: Dict of options, usually you're fine with defaults.
            Options consisting of:
            "updater": instance compatible with libMal.Updater
        '''
        if(entry):
            args = (self._username, self._password, self._animelist)
            updater = options.get("updater", Updater(*args))
            updater.update(entry)

    def performAutomaticListUpdate(self, filename):
        '''
        Perform update on best search result using default options
        @param filename: Name of file to update
        '''
        results = self.findEntriesOnMal(filename)
        if(len(results) > 0):
            result = results[0]
            self.updateEntryOnMal(result)

    def __sanitizeEpisodeNumberForUpdating(self, epStart, epEnd):
        ep = epStart if epEnd == '' else epEnd
        ep = ep if ep != '' else '1'
        return ep

    def _extractDataFromFilename(self, filename, options):
        extractor = options.get("extractor", AnimeInfoExtractor(filename))
        animeName = extractor.getName()
        # epStart and epEnd are for the spans, e.g. ep 1-4
        epStart, epEnd = extractor.getEpisodeNumbers()
        ep = self.__sanitizeEpisodeNumberForUpdating(epStart, epEnd)
        return animeName, ep


class ListFetcher(object):
    '''
    Downloads and parses AnimeList of user.
    Users unofficial mal api (http://mal-api.com)
    '''
    def __init__(self, username):
        self._username = username

    def __extractResults(self, data):
        results = {}
        for searchResults in data['anime']:
            result = Entry(searchResults)
            results[searchResults["id"]] = result
        return results

    def fetch(self):
        '''
        @return: Id indexed dict of user list
        '''
        listUrl = "http://mal-api.com/animelist/{}".format(self._username)
        data = urllib2.urlopen(listUrl).read()
        data = json.loads(data)
        return self.__extractResults(data)


class ResultsFilterer(object):
    '''
    Using internal filters find the best search result
    '''
    def __init__(self, animelist, showName, filename):
        self._animelist = animelist
        self._showName = showName
        self._filename = filename

    '''
    @param malEntries: Search results
    '''
    def scoreEntries(self, malEntries):
        args = (self._filename, self._animelist, malEntries)
        FirstGoogleResultFilter(*args).filterResults()
        SequelFilter(*args).filterResults()
        MostSimilarNameFilter(*args).filterResults()
        UserListStatusFilter(*args).filterResults()
        return sorted(malEntries, key=lambda e: e.matchBoost, reverse=True)


class Updater(object):
    '''
    For updating user's anime list
    '''
    UPDATE_TEMPLATE = str('<?xml version="1.0" encoding="UTF-8"?>\n'
                          '<entry>\n'
                          '    <episode>{}</episode>\n'
                          '    <status>{}</status>\n'
                          '    <tags>{}</tags>\n'
                          '</entry>\n')

    def __init__(self, username, password, animelist):
        self._password = password
        self._username = username
        self._animelist = animelist

    '''
    Do update list
    '''
    def update(self, malEntry):
        if(malEntry.id in self._animelist):
            epsOnList = self._animelist[malEntry.id].episodesSeen
            if(epsOnList >= malEntry.episodeBeingWatched):
                return
            url = "http://myanimelist.net/api/animelist/update/{}.xml"
        else:
            url = "http://myanimelist.net/api/animelist/add/{}.xml"
        self._executeApiCall(url, malEntry)

    def _executeApiCall(self, url, malEntry):
        if(malEntry.episodeCount == malEntry.episodeBeingWatched):
            status = "completed"
        else:
            status = "watching"
        request = urllib2.Request(url.format(malEntry.id))
        login = '{}:{}'.format(self._username, self._password)
        auth = base64.encodestring(login).replace('\n', '')
        request.add_header("Authorization", "Basic {}".format(auth))
        postData = {
                    "data": self.UPDATE_TEMPLATE.format(
                                                  malEntry.episodeBeingWatched,
                                                  status,
                                                  "syncplay")
                    }
        request.add_data(urllib.urlencode(postData))
        urllib2.urlopen(request).read()


class Finder(object):
    '''
    Lookup MAL entries given the show name
    Uses google search engine
    '''

    def find(self, name, ep):
        malLookup = "site:http://myanimelist.net/anime/ -inurl:.php {}"
        data = pygoogle(malLookup.format(name)).get_urls()
        return self.__extractResults(data, ep)

    def __extractResults(self, data, ep):
        results = []
        ids = []
        for link in data:
            m = re.search("myanimelist.net/anime/(\d+)", link)
            notRefferenced = "reviews" not in link and "userrecs" not in link
            if(None != m and notRefferenced and m.group(1) not in ids):
                ids.append(m.group(1))
        # We need unique ids. And they're better off sorted actually
        # So instead of set() we'll go for second loop
        for id_ in ids:
            listUrl = "http://mal-api.com/anime/{}".format(id_)
            data = urllib2.urlopen(listUrl).read()
            data = json.loads(data)
            result = Entry(data)
            result.setEpisodeWatched(ep)
            results.append(result)
        return results


class Entry(object):
    def __init__(self, searchResults):
        self.id = searchResults.get("id")

        self.mainTitle = searchResults.get("title")
        self.titles = []
        self.titles.append(searchResults.get("title"))
        otherTitles = searchResults.get("other_titles", {})
        self.titles.extend(otherTitles.get("english", ""))
        self.titles.extend(otherTitles.get("japanese", ""))
        self.titles.extend(otherTitles.get("synonyms", ""))

        self.malRank = searchResults.get("rank")
        self.malPopularity = searchResults.get("popularity_rank")
        self.image = searchResults.get("image_url")
        self.type = searchResults.get("type")
        self.episodeCount = searchResults.get("episodes")
        self.episodeCount = searchResults.get("episodes")
        self.airingStatus = searchResults.get("status")
        self.malScore = searchResults.get("members_score")
        self.airStartDate = searchResults.get("start_date")
        self.airEndDate = searchResults.get("end_date")
        self.classification = searchResults.get("classification")
        self.membersScore = searchResults.get("members_score")
        self.membersCount = searchResults.get("members_count")
        self.favouritedCount = searchResults.get("favorited_count")
        self.synopsis = searchResults.get("synopsis")
        self.genres = searchResults.get("genres")
        self.tags = searchResults.get("tags")
        self.mangaAdaptations = searchResults.get("manga_adaptations")
        self.prequels = searchResults.get("prequels")
        self.sequels = searchResults.get("sequels")
        self.sideStories = searchResults.get("side_stories")
        self.parentStory = searchResults.get("parent_story")
        self.characterAnime = searchResults.get("character_anime")
        self.spinOffs = searchResults.get("spin_offs")
        self.alternativeVersions = searchResults.get("alternative_versions")
        self.summaries = searchResults.get("summaries")

        self.episodesSeen = searchResults.get("watched_episodes")
        self.userScore = searchResults.get("score")
        self.watchedStatus = searchResults.get("watched_status")

        self.matchBoost = 0
        self.episodeBeingWatched = 0

    def setEpisodeWatched(self, ep):
        '''
        Episode that's currently being watched by user,
        this number can be changed by filters and will be sent on MAL on update
        '''
        self.episodeBeingWatched = ep

    def __repr__(self, *args, **kwargs):
        return repr({
                      'Id': self.id,
                      'Title': self.mainTitle,
                      'Episode being watched': self.episodeBeingWatched,
                      'Url': "http://myanimelist.net/anime/{}".format(self.id),
                      'Boost': self.matchBoost
                      })
