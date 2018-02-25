#!/home/evanmayer/anaconda3/bin/python
'''
This module houses the code to open an instance of Firefox to the relevant
Twitch page, and begin watching the OWL match. It is assumed that Firefox
already has user login info stored, and no login is required to watch the stream
with the intended user logged in.
'''

import sys
import subprocess
import json
import OWLscheduleScraper as scraper

def start_firefox_if_live(next_match, url_string):
    '''
    check next_match against current timestamp * 1e3, and start Firefox if
    match is supposed to be live.
    Inputs: 
        next_match: tuple of match start, match end timestamps in ms precision
        url_string: the url for Firefox open
    Returns:
        N/A
    '''
    current_time = scraper.get_current_time_in_milli()
    if next_match[0] < current_time:
        print("Match live!")
    else:
        print("Next match goes live at", next_match[0], '!')
    return

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
    # get data of interest; times in OWL API millisecond precision
    match_times = scraper.get_match_start_end(schedule)
    next_match = scraper.get_next_match_UTC(match_times)

    start_firefox_if_live(next_match, url_string)

    # display
    competitors = scraper.get_teams_playing_match(schedule, next_match[0])
    scraper.pretty_print_match(competitors, next_match)