#!/home/evanmayer/anaconda3/bin/python
'''
This module houses the code to open an instance of Firefox to the relevant
Twitch page, and begin watching the OWL match. It is assumed that Firefox
already has user login info stored, and no login is required to watch the stream
with the intended user logged in.
'''

import sys
import json
import OWLscheduleScraper as scraper


if __name__ == '__main__':
    if len(sys.argv) <= 1:
        print("Specify a URL and whether to print to file.\n"
              "Usage: ./OWLscheduleScraper.py <URL> <file_print=True, False>")
        sys.exit(1)

    # request from the OWL api page
    url_string = str(sys.argv[1])
    file_print = sys.argv[2]
    text = scraper.scrape_URL(url_string, file_write=True)
    # load to a json
    schedule = json.loads(text)
    # get data of interest
    match_times = scraper.get_match_start_end(schedule)
    next_match = scraper.get_next_match_UTC(match_times)
    competitors = scraper.get_teams_playing_match(schedule, next_match[0])
    # display
    scraper.pretty_print_match(competitors, next_match)