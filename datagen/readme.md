#Tools for generating databases used by the postcard data form

##Zipcode to Town database

database is used in form.html and as the source for creating the streetname database

maZips.txt was copied and pasted from a zipcode website
mazips.py turns maZips.txt into maZip.json
maZip.json is copied and pasted into form.html

##Legislators Room Numbers

databases used by lkuplib.py to create the routing number for each legislator

maRep.txt and maSen.txt wer copied and pasted from malegislature.gov
legRooms.py turns them into maRepRoom.json and maSenRoom.json
These json files are copied and pasted into lkuplib.py

## Tools for creating database of street names per zipcode using data from www.melissa.com
These are run in subdirectory ziptools. They are python2 tools. I've tried them in python3 and found that they yielded a streetDB.json in a different order that is probably the same content as the python2 version but I don't want to spend the time right now to prove that. So just use python2.

streetDB.json is used by mkGuess in main.py to find the closest match to a misspelled street

zip2city.json - all the current MA zipcodes and their city name
It was hand edited from maZip.json using the info in goneZipcodes.txt

melissa.py - fetches a zipcode to street file from melissa for each zipcode in zip2city.json
It uses the following url format to access my account
https://www.melissa.com/v2/lookups/addresssearch/?number=&street=&city=&state=&zip=01014&fmt=json&id=P7uEpV_llnpcT8UodfqDQf**nSAcwXpxhQ0PC2lXxuDAZ-**

Note - No need to run this again unless we think there have been zipcode changes since the last run because all the melissa data is in zip2adr.zip. melissa.py takes a long time to run and melissa.com charges for fetching the data.

First expand zip2adr.zip into the zip2adr directory containing all the steet info collected from melisa

zipchk.py - does the following checks.
  - checks that all the zipcodes in zip2city.json have been fetched from www.melissa.com
  - checks that each zipcode is in zip2city.json only once

zipStreet.py - combines every zipcode to street file into one json database for guessing street names
