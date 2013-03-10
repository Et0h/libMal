libMal
======

Library to manage MyAnimeList

Work in progress, don't expect it to do anything just yet

Example usage:

      from libMal import Manager
      import sys
      if __name__ == '__main__':
          username = sys.argv[1]
          password = sys.argv[2]
          filename = " ".join(sys.argv[3:])
          manager = Manager(username, password)
          results = manager.findEntriesOnMal(filename)
          #for r in results:
          #    print r
          if(len(results) > 0):
              manager.updateEntryOnMal(results[0])
