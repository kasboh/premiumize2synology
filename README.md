# premiumize2synology
This script downloads finished transfers from specific premiumize.me folder (e.g. transfers from Automatic RSS Feed downloader) 
to the synology NAS server. Finished transfers are deleted from premiumize.me
Script can be run as a scheduled task on synology
e.g. /usr/local/bin/python3 /volume1/temporary/scripts/premiumize.py


install python 3 from packet manager in synology
to install required packages:
  curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
  /usr/local/bin/python3 get-pip.py
  export PATH=$PATH:/volume1/@appstore/py3k/usr/local/bin
  pip install requests
