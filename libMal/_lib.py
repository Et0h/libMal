import urllib
import urllib2
import json
import base64
from ._pygoogle import pygoogle
from pprint import pprint
from . import AnimeInfoExtractor
import re


class Manager(object):
    def __init__(self, username, password):
        self._username = username
        self._password = password
        self._animelist = None
        self._ep = 0

    def _getUpdateData(self, filename):
        f = AnimeInfoExtractor(filename)
        animeName = f.getName()
        epStart, epEnd = f.getEpisodeNumbers()
        return animeName, epStart, epEnd

    def performListUpdate(self, filename, dryRun=False):
        animeName, epStart, epEnd = self._getUpdateData(filename)
        # epStart and epEnd are for the spans, e.g. ep 1-4
        # We'll still have some use of them for filtering
        self._ep = epStart if not epEnd else epEnd
        malEntries = Finder().find(animeName)
        self._animelist = ListFetcher(self._username).fetch()
        filterer = ResultsFilterer(self._animelist, animeName)
        result = filterer.selectFrom(malEntries)
        if(result and not dryRun):
            u = Updater(self._username, self._password, self._animelist)
            u.update(result, self._ep)
        else:
            print("(Dry run) Mal Updater Result: ")
            print(result)
            print("Episode: {}".format(self._ep))


class ListFetcher(object):
    def __init__(self, username):
        self._username = username

    def __extractResults(self, data):
        results = {}
        for searchResults in data['anime']:
            result = Entry(searchResults)
            results[searchResults["id"]] = result
        return results

    def fetch(self):
        listUrl = "http://mal-api.com/animelist/{}".format(self._username)
        data = urllib2.urlopen(listUrl).read()
        data = json.loads(data)
        return self.__extractResults(data)


class ResultsFilterer(object):
    def __init__(self, animelist, showName):
        self._animelist = animelist
        self._showName = showName

    def _findBestMatch(self, malEntries):
        return malEntries[0]

    def selectFrom(self, malEntries):
        if (len(malEntries) > 1):
            malEntry = self._findBestMatch(malEntries)
        elif (len(malEntries) == 1):
            malEntry = malEntries.values()[0]
        elif (len(malEntries) == 0):
            malEntry = None
        return malEntry


class Updater(object):
    UPDATE_TEMPLATE = '''<?xml version="1.0" encoding="UTF-8"?>
<entry>
    <episode>{}</episode>
    <status>{}</status>
    <tags>{}</tags>
</entry>'''

    def __init__(self, username, password, animelist):
        self._password = password
        self._username = username
        self._animelist = animelist

    def update(self, malEntry, episode):
        if(malEntry.id in self._animelist):
            if(self._animelist[malEntry.id].episodesSeen >= episode):
                return
            url = "http://myanimelist.net/api/animelist/update/{}.xml"
        else:
            url = "http://myanimelist.net/api/animelist/add/{}.xml"
        self._executeApiCall(url, malEntry, episode)

    def _executeApiCall(self, url, malEntry, episode):
        if(malEntry.episodeCount == episode):
            status = "completed"
        else:
            status = "watching"
        request = urllib2.Request(url.format(malEntry.id))
        login = '{}:{}'.format(self._username, self._password)
        auth = base64.encodestring(login).replace('\n', '')
        request.add_header("Authorization", "Basic [}".format(auth))
        postData = {
                    "data": self.UPDATE_TEMPLATE.format(
                                                        episode,
                                                        status,
                                                        "syncplay")
                    }
        request.add_data(urllib.urlencode(postData))
        pprint(url.format(malEntry.id))
        pprint(urllib2.urlopen(request).read())


class Finder(object):

    def find(self, name):
        malLookup = "site:http://myanimelist.net/anime/ -inurl:.php {}"
        data = pygoogle(malLookup.format(name)).get_urls()
        return self.__extractResults(data)

    def __extractResults(self, data):
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
            results.append(result)
        return results


class Entry(object):
    def __init__(self, searchResults):
        self.id = searchResults.get("id")

        self.titles = []
        self.titles.append(searchResults.get("title"))
        otherTitles = searchResults.get("other_titles", {})
        self.titles.append(otherTitles.get("english", []))
        self.titles.append(otherTitles.get("japanese", []))
        self.titles.extend(otherTitles.get("synonyms", []))

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

    def __repr__(self, *args, **kwargs):
        return "{}|{}|(boost={})".format(
                                         self.id,
                                         self.titles[0],
                                         self.matchBoost
                                         )


class BaseFilter(object):
    def __init__(self, filename, userlist, searchResults, options={}):
        self._userlist = userlist
        self._results = searchResults

    def getScoreChange(self):
        return 0

    def filterResults(self):
        return self.results
