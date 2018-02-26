'''
This module houses the code to query the OWL API for match times.
'''

import sys
import urllib.request as ul
from datetime import datetime, timezone

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
def scrape_URL(url_string, file_write=False):
    '''
    https://docs.python.org/3/library/urllib.request.html#examples
    '''
    request = ul.Request(url_string)
    with ul.urlopen(request) as response:
        html_page = response.read()
        page_text = html_page.decode()

    if file_write:
        with open('OWLdata.json', 'w') as f:
            f.write(page_text)

    return page_text

def get_match_start_end(json_schedule):
    '''
    dig down in the json to find match times for each game
    return match times as tuples of start, end times in millisecond timestamp
    '''
    match_times = []
    stages = json_schedule.get('data').get('stages')
    for stage in stages:
        matches = stage.get('matches')
        for match in matches:
            match_times.append(
                (match.get('startDateTS'),
                match.get('endDateTS'),)
                )
    return match_times

def get_next_match_milli(match_times):
    # in millisecond precision
    current_time = get_current_time_in_milli()
    # get the next start time, millisecond precision
    # this could be done more efficiently with bisect, but run times
    # will be dominated by API calls anyway
    for match_time in match_times:
        if match_time[0] > current_time:
            return match_time
    # when we reach the last match time
    print("No future matches in database.")
    sys.exit(0)

def get_teams_playing_match(schedule, start_time):
    # check the dict for a matching start_time
    teams = ()
    stages = schedule.get('data').get('stages')
    for stage in stages:
        matches = stage.get('matches')
        for match in matches:
            if match.get('startDateTS') == start_time:
                competitor0 = match.get('competitors')[0].get('name')
                competitor1 = match.get('competitors')[1].get('name')
                teams = (competitor0, competitor1)
    return teams

################################
# Formatting
################################
def pretty_print_match(competitors, next_match):
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