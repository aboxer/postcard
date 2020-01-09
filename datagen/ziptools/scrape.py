#scrape melissa.com to create a json street file for each zipcode
import requests
import re
from bs4 import BeautifulSoup
import sys
import json
import os.path
import time
import random



def nameSwitch(name):
  tmp = name.split()
  suffixes = ['Jr.','III'] #all the suffixes in MA senator & rep names
  for suffix in suffixes: #discard suffixes
    if tmp[-1] == suffix:
      last = tmp.pop()

  last = tmp.pop() 
  if last[-1] == ',': #last name may have a comma after suffix is removed
    last = last[:-1] 

  first = ''
  for wd in tmp:
    first += wd + ' '
  first = first[:-1]

  return last + ', ' + first

def space2Plus(field):
  wds = field.split()
  bar = ''
  for wd in wds:
    bar = bar + wd + '+'
  return bar[:-1]

def mkAdrVal(adr):
  field = adr.replace('#',' ')
  return space2Plus(field)

def mkZipVal(zipcode):
  if isinstance(zipcode,basestring) == True: #its a string so it is probably a 9 digit zip code with a dash
    return zipcode[:5]
  else: #ints an integer so it is probably a valid 5 digit zipcode
    return str(zipcode).zfill(5)

def lkupZip(zipcode):
  #street = mkAdrVal(adr[0])
  #town = space2Plus(adr[1])
  #zipcode =  mkZipVal(adr[2])
  #url = 'https://malegislature.gov/Search/FindMyLegislator?Address=' + street + '&City=' + town +'&ZipCode=' + zipcode
  url = 'https://www.melissa.com/v2/lookups/addresssearch/?number=&street=&city=&state=&zip=' + zipcode + '&fmt=json&id='
  try:
    response = requests.get(url, timeout=60.0)
    return response.content
  except:
    print 'Err: - melissa request failed ', url
    return None



#returns None if content fails to parse, returns legs with less than 2 entries if sen or rep not found
def adrScrape(content):
  try:
    #soup = BeautifulSoup(content,"lxml")
    soup = BeautifulSoup(content)
  except:
    return None
  tables = soup.find_all('tbody')
  adrs = []
  items = tables[0].find_all('a')
  for item in items:
    adrs.append(item.string)

  nums = []
  items = tables[1].find_all('a')
  for item in items:
    nums.append(item.string)

  return adrs,nums

rf = open('adrNum_01027.html', 'r')
r = rf.read()  #read in all the bytes into one string
rf.close()
adrs,nums = adrScrape(r)
#print adrs,nums

wf = open('adr_01027.json','w')
json.dump(adrs, wf)
wf.close()

wf = open('num_01027.json','w')
json.dump(nums, wf)
wf.close()

exit()

 
for i in range(len(zip2town)):
  zipcode = str(zip2town[i][0]).zfill(5)
  filename = 'adr_' + zipcode  + '.json'
  if not os.path.exists(filename):
    time.sleep(random.randint(30,50)) #add random delay to fool DOS attack detector
    print zipcode
    streets = lkupZip(zipcode)

    #output data
    wf =  open('adr_' + zipcode + '.json', 'w')
    wf.write(streets) 
    wf.close()

print 'done'

