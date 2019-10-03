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
    #print formDat;
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
    adr = [formDat['address'],formDat['town'],formDat['zipcode']]
    for tries in range(5):
      response = lkupLib.lkupLeg(adr) #returns none if retries fail
      if response != None: #got something from website, scrape it and return
        senRep = lkupLib.legScrape(response)
        if len(senRep) > 1: #lookup worked, calculate route code
          senRep['route'] = lkupLib.mkRoute(senRep)
        return json.dumps(senRep)
    return None


@app.errorhandler(500)
def server_error(e):
    # Log the error and stacktrace.
    logging.exception('An error occurred during a request.')
    return 'An internal error occurred.', 500
# [END app]

