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

import urllib as ul


################################
# Date/time format handlers
################################
def get_current_time_in_milli():
    return datetime.now(timezone.utc).timestamp() * 1e3


def get_time_in_UTC(timestamp):
    # case: timestamp is in normal UNIX compatible precision
    try:
        return datetime.utcfromtimestamp(timestamp)
    # case: timestamp is in OWL API ms precision. handle the error from datetime
    except:
        return datetime.utcfromtimestamp(timestamp / 1e3)


################################
# API URL scraping
################################
def url_to_json(url_string, file_write=False):
    '''
    https://docs.python.org/3/library/urllib.request.html#examples
    '''
    req = ul.request.Request(url_string)
    with ul.urlopen(req) as response:
        html_page = response.read()
        page_text = html_page.decode()

    if file_write:
        with open('OWLdata.json', 'w') as f:
            f.write(page_text)

    schedule = json.loads(page_text)

    return schedule


################################
# Formatting
################################
def pretty_print_match(competitors):
    # convert OWL api milli timestamps to UNIX-format for display
    start = next_match[0] / 1e3
    finish = next_match[1] / 1e3
    print("=========================================================")
    print("Next up:")
    print(competitors[0], 'vs.', competitors[1])
    print("From", get_time_in_UTC(start), "UTC",
          "to", get_time_in_UTC(finish), "UTC")
    print("=========================================================")

    return


################################
# Implementation
################################
def try_to_watch_next_match(api_url, file_write=False):
    ## get match info
    # request raw text from the OWL api page, load to a json
    schedule = url_to_json(api_url, file_write=False)
    
    # Get the pending or the current ongoing match
    current_match = schedule['data'].get('liveMatch')
    competitors = ( current_match['competitors']['0'].get('name'),
                    current_match['competitors']['1'].get('name') )

    # wait for the next match to go live
    liveStatus = current_match.get('liveStatus')
    print(liveStatus)

    while ('LIVE' != liveStatus):
        print("=========================================================")
        print("OWLwatcher:")
        print("UTC is currently", 
              get_time_in_UTC(get_current_time_in_milli()))
        print("Sleeping until next match...")
        pretty_print_match(competitors)
        time.sleep(5. * 60.)
    # Loop concludes when match goes live
    watch_url = current_match['hyperlinks']['4'].get('value')
    start_browser_while_live(current_match, competitors, watch_url)

    # when current match ends, find the next match ad infinitum
    try_to_watch_next_match(api_url, file_write=file_write)

    return


def start_browser_while_live(current_match, competitors, watch_url):
    '''
    start browser if match is supposed to be live. Close when match ends.
    Inputs: 
        next_match: json storing current match data
        competitors: tuple of competitors participating in match. For next up
            logging.
        watch_url: the url for browser open
    Returns:
        N/A
    '''
    # if we live, open firefox
    # With thanks to https://stackoverflow.com/a/4791612
    print("=========================================================")
    print("OWLwatcher:")
    print("Match live! Opening\n", watch_url)
    pretty_print_match(competitors, current_match)

    cmd = 'firefox ' + watch_url + ' &>/dev/null'
    p1 = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                          preexec_fn=os.setsid, shell=True)

    # check current time every 10s until match ends, then close firefox.
    while get_current_time_in_milli() < current_match.get('endDateTS'):
        print("=========================================================")
        print("OWLwatcher:")
        print("Match ongoing:")
        pretty_print_match(competitors)
        time.sleep(60)

    print("=========================================================")
    print("OWLwatcher:")
    print("Match ended. Terminating Firefox.")
    print("=========================================================")

    os.killpg(os.getpgid(p1.pid), signal.SIGTERM)

    return


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Specify a URL to get match times from, a URL to open during the"
              "next match, and whether to print the API .json to file.\n" 
              "Usage: ./OWLwatcher.py <API_URL> <True, False>")
        sys.exit(1)

    # handle inputs
    api_url = str(sys.argv[1])
    file_write = sys.argv[2]
    
    import cProfile

    cProfile.run('try_to_watch_next_match(api_url, file_write=file_write)', 'time')
