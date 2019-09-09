import requests
import re
import lxml
from bs4 import BeautifulSoup
from google.appengine.api import urlfetch
import logging

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
    #print 'dbg0',zipcode, zipcode[:5]
    return zipcode[:5]
  else: #ints an integer so it is probably a valid 5 digit zipcode
    return str(zipcode).zfill(5)

def lkupLeg(adr):
  street = mkAdrVal(adr[0])
  town = space2Plus(adr[1])
  zipcode =  mkZipVal(adr[2])
  url = 'https://malegislature.gov/Search/FindMyLegislator?Address=' + street + '&City=' + town +'&ZipCode=' + zipcode
  #print 'dbg1',url

#  try:
#    response = requests.get(url, timeout=60.0)
#    return response.content
#  except:
#    print 'Err: - malegislature.gov request failed ', url
#    exit()

  try:
    result = urlfetch.fetch(url)
    if result.status_code == 200:
      #self.response.write(result.content)
      return result.content
    else:
      #self.response.status_code = result.status_code
      return result.status_code
  except urlfetch.Error:
    logging.exception('Caught exception fetching url')




def legScrape(content):
  #soup = BeautifulSoup(content,"lxml")
  soup = BeautifulSoup(content)
  profiles = soup.find_all(class_='legislatorProfile')
  legs = {}
  for profile in profiles:
    elem = profile.find(class_='role')
    role =  elem.string
    elem =  profile.find(class_='name')
    name =  elem.string
    #legs[role] = name
    legs[role] = nameSwitch(name)
  return legs

def mkRoute(senRep):
  tmp2 = ''
  tmp = senRep['Senator'].split()
  for word in tmp:
    tmp2 = tmp2 + word[0]
  tmp2 = tmp2 + '_'
  tmp = senRep['Representative'].split()
  for word in tmp:
    tmp2 = tmp2 + word[0]
  return tmp2
