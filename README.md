libMal
======

### Library to manage MyAnimeList

Updates list very well at this moment.  
Work in progress about filtering results (works ok for series).

**Looking for developers.** Currently I'm alone with two projects apart from work, could use some help.

## Planned improvements
* Improved filtering, especially for OVA and Specials.
* More options for updates, scoring, tagging, setting up dates
* More verbose output and error handling.


## Example usage:

    if __name__ == '__main__':
        import sys
        from libMal import Manager
        username = sys.argv[1]
        password = sys.argv[2]
        filename = " ".join(sys.argv[3:])
        manager = Manager(username, password)
        results = manager.findEntriesOnMal(filename)
        #for r in results:
        #    print r
        if(len(results) > 0):
            manager.updateEntryOnMal(results[0])
