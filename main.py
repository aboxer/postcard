#!/usr/bin/python3
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

import sys
import logging
import json
import re
from fuzzywuzzy import fuzz
from nameparser import HumanName
#from streetaddress import StreetAddressParser
#from mystreetaddress import StreetAddressParser

from flask import Flask, render_template, request, jsonify
from flask_api import status
#import lkupLib
#import adrSheet

#import statsLib as stats
#import m_nlpAI as model
import c_nlpAI as ctl
#import v_nlpAI as view
import m_nlpAI as model

#m = model.model('rfa150.json',150) #infile json

#v = view.view()
#m = model.model(sys.argv[1],aiSz) #infile json
m = model.model('rfa150.json',100) #infile json
#c = ctl.ctl(v,m)
c = ctl.ctl(0,m)
c.run(c)
#if outfile != None: #save the results 
#  m.fileSv(outfi

app = Flask(__name__)

@app.route('/')
def form():
    return render_template('form.html')

# Runs when the submit button puts the client data into the spreadsheet
@app.route('/submitted', methods=['POST'])
def submitted_form():
    jsdata = request.form['javascript_data']
    formDat = json.loads(jsdata)
    name = HumanName(formDat['firstName'])
    #print 'dbg3 first ', name.first,'mid ',name.middle,'last ',name.last;
    formDat['firstName'] = name.first + ' ' + name.middle
    formDat['lastName'] = name.last
    #addr_parser = StreetAddressParser()
    #tmp = addr_parser.parse(formDat['address'])
    tmp = None

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

    #send the data to spreadsheet
    spreadSheet = formDat['sheet']
    #wks = adrSheet.adrSheet(spreadSheet) #exits if spreadsheet not found
    #print 'dbg12'
    wks = None
    formDat.pop('sheet', None)
    status,msg = wks.addRow(formDat)
    if status == False:
      #print 'dbg14',status,msg
      return json.dumps(msg),404
    return jsdata

#lookup the address in malegislature.gov
@app.route('/getpythondata')
def get_python_data():
    global c
    #addr_parser = StreetAddressParser()
    #tmp = addr_parser.parse(request.args.get('address'))
    tmp = request.args.get('address')
    #print 'dbg1',tmp

    #if tmp['house'] and tmp['street_full']: #create a full address for legislature lookup
    #  fullAdr = ' '.join([tmp['house'],tmp['street_full']])
    #elif tmp['street_full']:
    #  fullAdr = tmp['street_full']
    #else:
    #  fullAdr = ''

    #aiConf = '{:6.2f}'.format(stats.samConf(int(trainGoal),float(errMargin)/100.0,0.5,self.m.mailCt)*100)
    #aiConf = '{:6.2f}'.format(stats.samConf(int(tmp),0.05,0.5,5000))
    aiConf = c.trainConf(int(tmp),5)

  
    #adr = [fullAdr,request.args.get('city'),request.args.get('zipcode')]
    #print 'dbg2',adr
    senRep = {}
    senRep['route'] = 'hello'
    senRep['route2'] = 'world'
    senRep['Senator'] = 'me'
    senRep['Representative'] = aiConf
    return json.dumps(senRep)
    #for tries in range(5):
    #  response = lkupLib.lkupLeg(adr) #returns none if retries fail
    #  if response != None: #got something from website, scrape it and return
    #    senRep = lkupLib.legScrape(response)
    #    if len(senRep) > 1: #lookup worked, calculate route code
    #      senRep['route'],senRep['route2'] = lkupLib.mkRoute(senRep)
    #    else: #lookup failed. return list of guesses
    #      #print 'dbg3',request.args.get('zipcode'),tmp['street_full']
    #      senRep['guesses'] = mkGuess(request.args.get('zipcode'),tmp['street_full'])
    #    return json.dumps(senRep)
    #return 'MA Legislature Website Down - Hit Clear and try again later', status.HTTP_404_NOT_FOUND

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
  if re.search(r'\d', tmp[0]) and len(tmp) > 1: 
    adr = tmp[1]
  else:
    adr = ' '.join(tmp)

  for street in streets:
    Ratio = fuzz.ratio(adr.lower(),street.lower())
    minIdx = getMin(best)
    if Ratio > best[minIdx][0]:
      best[minIdx] = (Ratio,street)

  best.sort(key=score,reverse=True)
  return [best[0][1],best[1][1],best[2][1],best[3][1],best[4][1]]

@app.route('/shutDown', methods=['POST'])
def shutDown():
  jsdata = request.form['javascript_data']
  return jsdata 


@app.errorhandler(500)
def server_error(e):
    #print 'dbg13',e
    #logging.exception('ERR request %s',e)
    return 'An internal error occurred.', 500

@app.route('/postmethod', methods = ['POST']) #not used
def get_post_javascript_data():
    jsdata = request.form['javascript_data']
    tmp = json.loads(jsdata)
    return jsdata

@app.route('/gsOpen', methods=['POST']) #NOTE - not used but will be when client can specify spreadsheet
def spreadSheet():
    jsdata = request.form['javascript_data']
    formDat = json.loads(jsdata)
    wks = adrSheet.adrSheet(spreadSheet) #exits if spreadsheet not found
    return jsdata
