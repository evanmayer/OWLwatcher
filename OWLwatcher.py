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

def match_is_live(current_match):
    current_time = scraper.get_current_time_in_milli()
    if current_match == None:
        return False
    if current_time > current_match[0]:
        return True
    else:
        return False


def start_firefox_while_live(current_match, competitors, api_url):
    '''
    start firefox if match is supposed to be live. Close when match ends.
    Inputs: 
        next_match: tuple of match start, match end timestamps in ms precision
        competitors: tuple of competitors participating in match. For next up
            logging.
        api_url: the url for browser open
    Returns:
        N/A
    '''
    # if we are past the match start time, open firefox
    # With thanks to https://stackoverflow.com/a/4791612
    print("=========================================================")
    print("OWLwatcher:")
    print("Match live! Opening\n", api_url, '\nin Firefox.')
    scraper.pretty_print_match(competitors, current_match)


    cmd = 'firefox ' + api_url
    p1 = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                          preexec_fn=os.setsid, shell=True)

    # check current time every 10s until match ends, then close firefox.
    while scraper.get_current_time_in_milli() < current_match[1]:
        print("OWLwatcher:")
        print("Match ongoing.")
        time.sleep(10)

    print("=========================================================")
    print("OWLwatcher:")
    print("Match ended. Terminating Firefox.")
    print("=========================================================")

    os.killpg(os.getpgid(p1.pid), signal.SIGTERM)

    return

def try_to_watch_next_match(api_url, twitch_url, file_write):
    ## get match info
    # request from the OWL api page
    text = scraper.scrape_URL(api_url, file_write=False)
    # load to a json
    schedule = json.loads(text)

    # get data of interest; match times in OWL API millisecond precision
    match_times = scraper.get_match_start_end(schedule)
    current_match = scraper.get_current_match_milli(match_times)
    next_match = scraper.get_next_match_milli(match_times)
    competitors = scraper.get_teams_playing_match(schedule, current_match[0])

    # wait for the next match to go live
    while not match_is_live(current_match):
        current_match = scraper.get_current_match_milli(match_times)
        print("=========================================================")
        print("OWLwatcher:")
        print("UTC is currently", 
              scraper.get_time_in_UTC(scraper.get_current_time_in_milli()))
        print("Sleeping until next match...")
        scraper.pretty_print_match(competitors, next_match)
        time.sleep(10)
    # Loop concludes when match goes live
    start_firefox_while_live(current_match, competitors, twitch_url)

    # when current match ends, find the next match ad infinitum
    try_to_watch_next_match(api_url, twitch_url, file_write)

    return

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print("Specify a URL to get match times from, a URL to open during the"
              "next match, and whether to print the API .json to file.\n" 
              "Usage: ./OWLscheduleScraper.py <API_URL> <Twitch_URL> <True, False>")
        sys.exit(1)

    # handle inputs
    api_url = str(sys.argv[1])
    twitch_url = sys.argv[2]
    file_write = sys.argv[3]

    try_to_watch_next_match(api_url, twitch_url, file_write)