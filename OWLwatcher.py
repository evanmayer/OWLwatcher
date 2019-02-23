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
import datetime
import urllib.request as urlreq

################################
# Date/time format handlers
################################
def get_current_time_in_milli():
    return datetime.datetime.now(datetime.timezone.utc).timestamp() * 1e3


def get_time_in_UTC(timestamp):
    # case: timestamp is in normal UNIX compatible precision
    try:
        return datetime.datetime.utcfromtimestamp(timestamp)
    # case: timestamp is in OWL API ms precision. handle the error from datetime
    except:
        return datetime.datetime.utcfromtimestamp(timestamp / 1e3)


################################
# API URL scraping
################################
def get_match_data(url_string, file_write=False):
    '''
    https://docs.python.org/3/library/urllib.request.html#examples
    '''
    # Request raw text from the API page, load to a json
    req = urlreq.Request(url_string)
    with urlreq.urlopen(req) as response:
        html_page = response.read()
        page_text = html_page.decode()

    if file_write:
        with open('OWLdata.json', 'w') as f:
            f.write(page_text)

    schedule = json.loads(page_text)

    # Get the pending or the current ongoing match
    current_match = schedule['data'].get('liveMatch')

    return current_match


################################
# Formatting
################################
def pretty_print_match(current_match, competitors):
    # convert OWL api milli timestamps to UNIX-format for display
    start = current_match.get('startDateTS') / 1e3
    finish = current_match.get('endDateTS') / 1e3
    print("=========================================================")
    print("On deck:")
    print(competitors[0], 'vs.', competitors[1])
    print("From", get_time_in_UTC(start), "UTC",
          "to", get_time_in_UTC(finish), "UTC")
    print("=========================================================")

    return


################################
# Idle behavior cycles
################################

def wait_for_match_data(api_url, file_write=False):
    # A loop to wait until  the live-match api field is populated
    while not (get_match_data(api_url, file_write=file_write)):
        print("=========================================================")
        print("OWLwatcher:")
        print("UTC is currently", 
            get_time_in_UTC(get_current_time_in_milli()))
        print("Sleeping until next match is available...")
        time.sleep(60.)
    return 


def wait_for_match_live(api_url, file_write=False):
    # A loop to wait until the live-match api field reports a live match
    current_match = get_match_data(api_url, file_write=file_write)
    liveStatus = current_match.get('liveStatus')
    while ('LIVE' != liveStatus):
        print("=========================================================")
        print("OWLwatcher:")
        print("UTC is currently", 
            get_time_in_UTC(get_current_time_in_milli()))
        print("Sleeping until next match is goes live!")
        time.sleep(60.)
        current_match = get_match_data(api_url, file_write=file_write)
        liveStatus = current_match.get('liveStatus')
    return


def wait_for_match_end(current_match, competitors):
    # check current time every 60s until match ends, then close browser.
    while get_current_time_in_milli() < current_match.get('endDateTS'):
        print("=========================================================")
        print("OWLwatcher:")
        print("Match ongoing:")
        pretty_print_match(current_match, competitors)
        print("UTC is currently", 
              get_time_in_UTC(get_current_time_in_milli()))
        time.sleep(60)
    return


################################
# Implementation
################################
def try_to_watch_next_match(api_url, file_write=False):
    # Wait until API reports a match is scheduled to go live
    wait_for_match_data(api_url, file_write=file_write)
    # Wait until API reports match has gone live
    wait_for_match_live(api_url, file_write=file_write)
    # Get the match json
    current_match = get_match_data(api_url, file_write=file_write)
    # Find out who's playing
    competitors = ( current_match['competitors'][0].get('name'),
                    current_match['competitors'][1].get('name') )
    # Get an English Twitch link
    watch_url = current_match['hyperlinks'][2].get('value')

    # Open a method for watching the match
    watch_match(current_match, competitors, watch_url)

    # when current match ends, wait for the next match to start
    try_to_watch_next_match(api_url, file_write=file_write)

    return


def watch_match(current_match, competitors, watch_url):
    '''
    start browser if match is supposed to be live. Close when match ends.
    Inputs: 
        next_match: json storing current match data
        competitors: tuple of competitors participating in match. 
        watch_url: the url for browser open
    Returns:
        N/A
    '''
    # if we live, open firefox
    # With thanks to https://stackoverflow.com/a/4791612
    print("=========================================================")
    print("OWLwatcher:")
    print("Match live! Opening\n", watch_url)
    pretty_print_match(current_match, competitors)

    cmd = 'firefox ' + watch_url + ' &>/dev/null'
    p1 = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                          preexec_fn=os.setsid, shell=True)

    wait_for_match_end(current_match, competitors)

    print("=========================================================")
    print("OWLwatcher:")
    print("Match ended. Terminating Firefox.")
    print("=========================================================")

    os.killpg(os.getpgid(p1.pid), signal.SIGTERM)

    return


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Specify a URL to get match times from, a URL to open during the"
              " next match, and whether to print the API .json to file.\n"
              "Try: https://api.overwatchleague.com/live-match. \n" 
              "Usage: ./OWLwatcher.py <API_URL> <True, False>")
        sys.exit(1)

    # handle inputs
    api_url = str(sys.argv[1])
    file_write = sys.argv[2]
    
    try_to_watch_next_match(api_url, file_write=file_write)