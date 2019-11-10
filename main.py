# -*- coding: utf-8 -*-

# Copyright 2016 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# [START app]
import sys
import logging
import json
import re
from fuzzywuzzy import fuzz
#import usaddress
#import pyap
from nameparser import HumanName
from streetaddress import StreetAddressParser

from google.appengine.ext import ndb
from google.appengine.api import memcache


# [START imports]
from flask import Flask, render_template, request
import lkupLib
import adrSheet
#print 'paths'
#print '\n'.join(sys.path)

# [END imports]

# [START create_app]
app = Flask(__name__)
# [END create_app]

# [START form]
#@app.route('/form')
@app.route('/')
def form():

    #global wks
    #wks = adrSheet.adrSheet('acluCard') #exits if spreadsheet not found
    #print wks.getAdr(2)
    memcache.add(key="spreadSheet",value="acluCard",time=7200)
    return render_template('form.html')
# [END form]

@app.route('/gsOpen', methods=['POST']) #NOTE - not used but will be when client can specify spreadsheet
def spreadSheet():
    #global wks
    #global formDat
    jsdata = request.form['javascript_data']
    formDat = json.loads(jsdata)
    print 'dbg11', formDat
    memcache.set(key="spreadSheet", value=formDat['sheet'], time=36000)
    spreadSheet = memcache.get("spreadSheet")
    print 'dbg12', spreadSheet
    #wks = adrSheet.adrSheet('acluCard') #exits if spreadsheet not found
    wks = adrSheet.adrSheet(spreadSheet) #exits if spreadsheet not found
    return jsdata


# Runs when the submit button puts the client data into the spreadsheet
@app.route('/submitted', methods=['POST'])
def submitted_form():
    #global formDat
    #global wks
    jsdata = request.form['javascript_data']
    formDat = json.loads(jsdata)
    name = HumanName(formDat['firstName'])
    #print 'dbg3 first ', name.first,'mid ',name.middle,'last ',name.last;
    formDat['firstName'] = name.first + ' ' + name.middle
    formDat['lastName'] = name.last
    #print formDat;
    addr_parser = StreetAddressParser()
    tmp = addr_parser.parse(formDat['address'])
    #if tmp['house'] and tmp['street_full']:
    #  formDat['address'] = ' '.join([tmp['house'],tmp['street_full']])

    if tmp['house'] and tmp['street_full']:
      formDat['address'] = ' '.join([tmp['house'],tmp['street_full']])
    elif tmp['street_full']:
      formDat['address'] = tmp['street_full']
    else:
      formDat['address'] = ''

    formDat['suite'] = ''
    for tmp2 in ['suite_type','suite_num','other']:
      try:
        formDat['suite'] += tmp[tmp2] + ' '
      except:
        pass

    #print 'dbg4 adr', formDat['address'], 'suite ', formDat['suite']
    #print 'dbg5 tmp', tmp


    spreadSheet = memcache.get("spreadSheet")
    wks = adrSheet.adrSheet(spreadSheet) #exits if spreadsheet not found
    wks.addRow(formDat)
    #return render_template('form.html')
    return jsdata

@app.route('/postmethod', methods = ['POST'])
def get_post_javascript_data():
    #global formDat
    jsdata = request.form['javascript_data']
    #formDat = json.loads(jsdata)
    tmp = json.loads(jsdata)
    memcache.add(key="formDat",value=tmp,time=7200)
    return jsdata

@app.route('/getpythondata')
def get_python_data():
    #global formDat
    formDat = memcache.get("formDat")
    print 'dbg0',formDat
    memcache.delete("formDat")

    addr_parser = StreetAddressParser()
    tmp = addr_parser.parse(formDat['address'])

    if tmp['house'] and tmp['street_full']:
      formDat['address'] = ' '.join([tmp['house'],tmp['street_full']])
    elif tmp['street_full']:
      formDat['address'] = tmp['street_full']
    else:
      formDat['address'] = ''


    adr = [formDat['address'],formDat['town'],formDat['zipcode']]
    for tries in range(5):
      response = lkupLib.lkupLeg(adr) #returns none if retries fail
      if response != None: #got something from website, scrape it and return
        senRep = lkupLib.legScrape(response)
        if len(senRep) > 1: #lookup worked, calculate route code
          senRep['route'] = lkupLib.mkRoute(senRep)
        else: #lookup failed. return list of guesses
          senRep['guesses'] = mkGuess(formDat['zipcode'],formDat['address'])
        return json.dumps(senRep)
    return None

def getMin(best):
  minIdx = 0
  minScore = best[minIdx][0]
  for i in range(1,len(best)):
    j = best[i][0]
    if j < minScore:
      minScore = j
      minIdx = i
  return minIdx

def score(elem):
  return elem[0]

def mkGuess(zipcode,address):
  rf = open('streetDB.json', 'r') #TODO - if performance sucks we may be able to do this in parallel with legislator lookup
  r = rf.read()
  zipStreets = json.loads(r)
  rf.close()

  best = [(0,' '),(0,' '),(0,' '),(0,' '),(0,' ')]
  try:
    streets = zipStreets[zipcode]
  except:
    return [best[0][1],best[1][1],best[2][1],best[3][1],best[4][1]]
  tmp = address.split(' ',2)
  #if re.search(r'\d', tmp[0]): 
  if re.search(r'\d', tmp[0]) and len(tmp) > 1: 
    adr = tmp[1]
  else:
    adr = ' '.join(tmp)

  for street in streets:
    Ratio = fuzz.ratio(adr.lower(),street.lower())
    #print Ratio, street
    minIdx = getMin(best)
    if Ratio > best[minIdx][0]:
      best[minIdx] = (Ratio,street)

  best.sort(key=score,reverse=True)
  #return ['guessa','guessb','guessc','guessd','guesse']
  return [best[0][1],best[1][1],best[2][1],best[3][1],best[4][1]]

@app.route('/shutDown', methods=['POST'])
def shutDown():
  memcache.delete("spreadSheet")
  memcache.delete("formDat")
  jsdata = request.form['javascript_data']
  return jsdata 
# [END form]


@app.errorhandler(500)
def server_error(e):
    # Log the error and stacktrace.
    memcache.delete("formDat")
    memcache.delete("spreadSheet")
    logging.exception('ERR request %s',e)
    return 'An internal error occurred.', 500
# [END app]

