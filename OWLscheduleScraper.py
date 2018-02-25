#!/home/evanmayer/anaconda3/bin/python

import sys
import urllib.request as ul
import json
from datetime import datetime, timezone

def scrape_URL(url_string):
    '''
    Courtesy https://www.summet.com/dmsi/html/readingTheWeb.html
    '''
    request = ul.Request(url_string)
    response = ul.urlopen(request)
    page = response.read()
    text = page.decode()

    with open('OWLdata.json', 'w') as f:
        f.write(text)

    return text

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

def get_next_match_UTC(match_times):
    # in millisecond precision
    current_time = datetime.now(timezone.utc).timestamp() * 1e3
    # get the next start time, millisecond precision
    next_match = 0
    for match_time in match_times:
        if match_time[0] > current_time:
            next_match = match_time
            break
    return next_match

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

def pretty_print_match(competitors, next_match):
    # convert OWL api milli timestamps to UNIX-format
    start = next_match[0] / 1e3
    finish = next_match[1] / 1e3
    print("=================================================")
    print("| Next up:")
    print('|', competitors[0], 'vs.', competitors[1])
    print("| From", datetime.utcfromtimestamp(start),
          "to", datetime.utcfromtimestamp(finish))
    print("=================================================")

if __name__ == '__main__':
    if len(sys.argv) <= 1:
        print("Specify a URL and whether to print to file.\n"
              "Usage: ./OWLscheduleScraper.py <URL> <file_print=True, False>")
        sys.exit(1)

    # request from the OWL api page
    url_string = str(sys.argv[1])
    file_print = sys.argv[2]
    text = scrape_URL(url_string)
    # load to a json
    schedule = json.loads(text)
    # get data of interest
    match_times = get_match_start_end(schedule)
    next_match = get_next_match_UTC(match_times)
    competitors = get_teams_playing_match(schedule, next_match[0])
    # display
    if file_print:
        pretty_print_match(competitors, next_match)