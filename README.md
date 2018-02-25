# OWLwatcher:
Who watches the Overwatchers?

## Assumptions:

It is assumed that you have a Twitch account with credentials saved in Firefox on the machine running this utility, and that Firefox has all plugins updated so that the Twitch stream is functional upon Firefox startup.

## Usage:
Specify a URL to get match times from, a URL to open during the next match, and whether to print the API .json to file.

`$ chmod +x OWLwatcher.py`

`$ ./OWLwatcher.py <OWL API URL> <Twitch URL> <True, False>`

## Known dependencies:
- Linux-based OS
  - I use Ubuntu 16.04 on a VM, but any POSIX-compliant OS should be fine.
- Python 3
  - sys
  - os
  - signal
  - subprocess
  - time
  - json
  - urllib
  - datetime
- Firefox
  - Flash (for viewing Twitch streams in Firefox)
