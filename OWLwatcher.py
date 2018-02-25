#!/home/evanmayer/anaconda3/bin/python
'''
This module houses the code to open an instance of Firefox to the relevant
Twitch page, and begin watching the OWL match. It is assumed that Firefox
already has user login info stored, and no login is required to watch the stream
with the intended user logged in.
'''
import sys

import os
import signal
import subprocess
import time

import json
import OWLscheduleScraper as scraper

def match_is_live(next_match):
    '''
    check next_match against current timestamp * 1e3
    '''
    current_time = scraper.get_current_time_in_milli()
    if current_time > next_match[0]:
        return True
    else:
        return False


def start_firefox_while_live(next_match, competitors, url_string):
    '''
    start firefox if match is supposed to be live. Close when match ends.
    Inputs: 
        next_match: tuple of match start, match end timestamps in ms precision
        competitors: tuple of competitors participating in match. For next up
            logging.
        url_string: the url for browser open
    Returns:
        N/A
    '''
    # if we are past the match start time, open firefox
    # With thanks to https://stackoverflow.com/a/4791612
    if match_is_live(next_match):
        print("=========================================================")
        print("OWLwatcher:")
        print("Match live! Opening", url_string, 'in Firefox.')
        print("=========================================================")

        cmd = 'firefox ' + url_string
        p1 = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                              preexec_fn=os.setsid, shell=True)

        # check current time every 30s until match ends, then close firefox.
        while scraper.get_current_time_in_milli() < next_match[1]:
            print("OWLwatcher:")
            print("Match ongoing.")
            time.sleep(30)

        print("=========================================================")
        print("OWLwatcher:")
        print("Match ended. Terminating Firefox.")
        print("=========================================================")

        os.killpg(os.getpgid(p1.pid), signal.SIGTERM)

        return
    else:
        print("=========================================================")
        print("OWLwatcher:")
        print("No match live.")
        scraper.pretty_print_match(competitors, next_match)

        return

def try_to_watch_next_match(url_string, twitch_url, file_write):
    ## get match info
    # request from the OWL api page
    text = scraper.scrape_URL(url_string, file_write=False)
    # load to a json
    schedule = json.loads(text)
    # get data of interest; match times in OWL API millisecond precision
    match_times = scraper.get_match_start_end(schedule)
    next_match = scraper.get_next_match_milli(match_times)
    competitors = scraper.get_teams_playing_match(schedule, next_match[0])

    # only for spoofing an active match: this one is 60s long.
    # next_match = (scraper.get_current_time_in_milli() - 1, 
    #               scraper.get_current_time_in_milli() + (60 * 1e3))

    # wait for the next match to go live
    while not match_is_live(next_match):
        print("=========================================================")
        print("OWLwatcher:")
        print("Sleeping until next match...")
        print("=========================================================")
        time.sleep(60)
    # when live, start firefox
    start_firefox_while_live(next_match, competitors, twitch_url)

    return

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print("Specify a URL to get match times from, a URL to open during the"
              "next match, and whether to print the API .json to file.\n" 
              "Usage: ./OWLscheduleScraper.py <API_URL> <Twitch_URL> <True, False>")
        sys.exit(1)

    # handle inputs
    url_string = str(sys.argv[1])
    twitch_url = sys.argv[2]
    file_write = sys.argv[3]

    try_to_watch_next_match(url_string, twitch_url, file_write)