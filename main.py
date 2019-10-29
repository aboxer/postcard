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
import logging
import json
import re
from fuzzywuzzy import fuzz
#import usaddress
#import pyap
from nameparser import HumanName
from streetaddress import StreetAddressParser



# [START imports]
from flask import Flask, render_template, request
import lkupLib
import adrSheet

# [END imports]

# [START create_app]
app = Flask(__name__)
# [END create_app]

formDat = None
wks = None
rf = open('streetDB.json', 'r')
r = rf.read()
zipStreets = json.loads(r)
rf.close()
 
# [START form]
#@app.route('/form')
@app.route('/')
def form():
    global wks
    wks = adrSheet.adrSheet('acluCard') #exits if spreadsheet not found
    #print wks.getAdr(2)
    return render_template('form.html')
# [END form]

@app.route('/gsOpen', methods=['POST'])
def spreadSheet():
    global wks
    global formDat
    jsdata = request.form['javascript_data']
    formDat = json.loads(jsdata)
    print formDat
    #wks = adrSheet.adrSheet('acluCard') #exits if spreadsheet not found
    wks = adrSheet.adrSheet(formDat) #exits if spreadsheet not found
    return jsdata


# [START submitted]
@app.route('/submitted', methods=['POST'])
def submitted_form():
    global formDat
    global wks
    jsdata = request.form['javascript_data']
    formDat = json.loads(jsdata)
    name = HumanName(formDat['firstName'])
    #print 'dbg3 first ', name.first,'mid ',name.middle,'last ',name.last;
    formDat['firstName'] = name.first + ' ' + name.middle
    formDat['lastName'] = name.last
    #print formDat;
    addr_parser = StreetAddressParser()
    tmp = addr_parser.parse(formDat['address'])
    formDat['address'] = ' '.join([tmp['house'],tmp['street_full']])
    formDat['suite'] = ' '.join([tmp['suite_type'],tmp['suite_num']])
    wks.addRow(formDat)
    #return render_template('form.html')
    return jsdata

@app.route('/postmethod', methods = ['POST'])
def get_post_javascript_data():
    global formDat
    jsdata = request.form['javascript_data']
    formDat = json.loads(jsdata)
    return jsdata

@app.route('/getpythondata')
def get_python_data():
    global formDat
    #try:
    #  tmp = usaddress.tag(formDat['address'])
    #  tmp1 = ' '.join(tmp['AddressNumber'],tmp['StreetNamePreDirectional'],tmp['StreetName'],tmp['StreetNamePostType'])
    #  print tmp1
    #except:
    #  tmp1 = ''
    #test_address = """
    #    Lorem ipsum
    #    225 E. John Carpenter Freeway,
    #    Suite 1500 Irving, Texas 75062
    #    Dorem sit amet
    #"""
    #test_address = """
    #  24 adams st
    #"""

    #addresses = pyap.parse([formDat['address']], country='US')
    #print 'dbg7 ',formDat['address'], test_address
    #addresses = pyap.parse(test_address, country='US')
    #print 'dbg6 ', addresses
    #for address in addresses:
    #  # shows found address
    #  print 'dbg4 ', address
    #  # shows address parts
    #  print 'dbg5 ', address.as_dict()

    addr_parser = StreetAddressParser()
    tmp = addr_parser.parse(formDat['address'])
    formDat['address'] = ' '.join([tmp['house'],tmp['street_full']])
    formDat['suite'] = ' '.join([tmp['suite_type'],tmp['suite_num']])
    print 'dbg4 adr', formDat['address'], 'suite ', formDat['suite']


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
  global zipStreets
  streets = zipStreets[zipcode]
  best = [(0,'a'),(0,'b'),(0,'c'),(0,'d'),(0,'e')]
  tmp = address.split(' ',2)
  if re.search(r'\d', tmp[0]): 
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

@app.errorhandler(500)
def server_error(e):
    # Log the error and stacktrace.
    logging.exception('An error occurred during a request.')
    return 'An internal error occurred.', 500
# [END app]

