libMal
======

Library to manage MyAnimeList

Work in progress, don't expect it to do anything just yet

Example usage:

      if __name__ == '__main__':
          from libMal import Manager
          import sys
          username = sys.argv[1]
          password = sys.argv[2]
          filename = " ".join(sys.argv[3:])
          Manager(username, password).performListUpdate(filename, dryRun=True)
