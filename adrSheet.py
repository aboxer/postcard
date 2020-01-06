import gspread
import logging
from oauth2client.service_account import ServiceAccountCredentials
import json
import sys
#from requests_toolbelt.adapters import appengine

#appengine.monkeypatch()

class adrSheet:
  def __init__(self,sheetName):
    self.scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive'] #enable the two apis selected
    self.creds = ServiceAccountCredentials.from_json_keyfile_name('gcCreds.json',self.scope) #file downloaded from google API console
    self.retries = 3
    self.sheetName = sheetName
    self.sheetMap = {'First Name:':'firstName','Last Name:':'lastName','Address:':'address','Address Line 2:':'suite','City:':'city','State/Province:':'state','Zip:':'zipcode','Phone Number:':'phone','E-mail:':'email','Comment:':'comment','State Senator':'stateSen','State Representative':'stateRep','Route':'route'}
    self.sheetCols = []
    self.lastRow = 0

  def addRow(self,formDat):
    for tries in range(self.retries):  #may be idle so long that spreadsheet closes
      try:
        gc = gspread.authorize(self.creds) #authorize access to the spreadsheet
        self.wks = gc.open(self.sheetName).sheet1 #open the spreadsheet by name
        self.sheet = self.wks.get_all_records() #get all the records into a list. each record is a dictionary with row 1 as keys.
        break
      except:
        logging.warning( 'ERR: reopen spreadsheet not found')
    else:
      logging.error( 'ERR: reopen spreadsheet retries fail')
      return False, 'Spreadsheet not found - check spelling'

    self.lastRow = len(self.sheet) + 1
    row1 = self.wks.row_values(1)
    #put the internal column names in the same order as the official spreadsheet column names
    for col in row1:
      try:
        self.sheetCols.append(self.sheetMap[col]) #found the official name in row1, append the internal name
      except:
        self.sheetCols.append(None) #blank column in row1 or no match for official name

    values = []
    for col in self.sheetCols: #go thru the internal names and add then to the row
      if col == None:
        values.append('') #blank or wrong name for this column
      else:
        values.append(formDat[col])

    for tries in range(self.retries): #write the row info out to spreadsheet
      try:
        self.wks.append_row(values)
        return [True,'ok']
      except:
        pass
    else:
      logging.error( 'ERR: spreadsheet update retires fail')
      return False, 'Spreadsheet Server down - try again later'


  def getAdr(self,rowNum): #not used
    if rowNum < 2 or rowNum > self.lastRow: #outside the bounds of the sheet
      return []
    else:
      row = self.sheet[rowNum - 2]
      return [row['Address:'],row['City:'],row['Zip:']]

  def doLookup(self,rowNum): #not used
    row = self.sheet[rowNum - 2]
    if row['State Senator'] == '' or row['State Representative'] == '': #needs a lookup
      if row['State/Province:'] != 'Massachusetts': #check if address is legal
       return False
      elif isinstance(row['Address:'],int): #integer only is a malformed address
        return False
      else: #can't do po boxes  or addresses wit h no numbers
        tmp = row['Address:'].replace(' ','')
        tmp1 = tmp.replace('.','').lower()
        if tmp1[:5] == 'pobox' or tmp1[:3] == 'box' : #can't do po boxes
          return False
      return True
    else:
      return False

