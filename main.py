import sys

from settings import SETTINGS
from HackerNewsFetcher import Fetcher


if __name__ == '__main__':
    reverse_filter = len(sys.argv) > 1 and (sys.argv[1] == '--reverse' or sys.argv[1] == '-r')
    fetcher = Fetcher(settings=SETTINGS, reverse_filter=reverse_filter)
    fetcher.run()
