# OWLwatcher:
Who watches the Overwatchers? Me. I never remember to open streams when matches go live. This program will do it for me.

## Assumptions:

It is assumed that you have a Twitch account with credentials saved in Firefox on the machine running this utility, and that Firefox has all plugins updated so that the Twitch stream is functional upon Firefox startup.

## Usage:
Specify a URL to get match times from, a URL to open during the next match, and whether to print the API .json to file.

`$ chmod +x OWLwatcher.py`

`$ ./OWLwatcher.py <OWL API URL> <True, False>`

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

## Known issues:
- The OWL API is volatile and Blizzard makes no promises as to the stability of its structure or interfaces. As a result, this script may break without warning.
- The shebang at the top of `OWLwatcher.py`, `#!/home/evanmayer/anaconda3/bin/python`, points to the anaconda Python 3 install on my system. Make sure it points to your Python 3 install if you are running it as an executable script from the command line. You can usually find this with `which python`.
