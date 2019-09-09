import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
import sys
from requests_toolbelt.adapters import appengine

appengine.monkeypatch()

class adrSheet:
  def __init__(self,sheetName):
    scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive'] #enable the two apis selected
    creds = ServiceAccountCredentials.from_json_keyfile_name('gcCreds.json',scope) #file downloaded from google API console

    gc = gspread.authorize(creds) #authorize access to the spreadsheet
    try:
      self.wks = gc.open(sheetName).sheet1 #open the spreadsheet by name
    except:
      print "Unexpected error:", sys.exc_info()[0]
      print "message:", sys.exc_info()[0].message
      print 'ERR: spreadsheet not found'
      exit()
    self.sheet = self.wks.get_all_records() #get all the records into a list. each record is a dictionary with row 1 as keys.
    self.lastRow = len(self.sheet) + 1

  def getAdr(self,rowNum):
    if rowNum < 2 or rowNum > self.lastRow: #outside the bounds of the sheet
      return []
    else:
      row = self.sheet[rowNum - 2]
      return [row['Address:'],row['City:'],row['Zip:']]

  def doLookup(self,rowNum):
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

  def chgLegis(self,rowNum,legis):
    #if rowNum < 2 or rowNum > self.lastRow: #outside the bounds of the sheet
    #  return False
    #else:
    try:
      update = [self.wks.cell(rowNum,11)] #NOTE: - this worked in previous sheet
      update.append(self.wks.cell(rowNum,12))
      #update = [self.wks.cell(rowNum,9)]  #column I = Rep
      #update.append(self.wks.cell(rowNum,10))  #column J = Sen
      update[0].value = legis['Representative']
      update[1].value = legis['Senator']
      #print 'dbg2', update[0].value,update[1].value
      self.wks.update_cells(update)
      return True
    except:
      return False

  def addRow(self,formDat):
    try:
      print 'dbg0',formDat
      values = []
      #for x in ['fullName','address','city','state','zipcode','phone','email']:
      for x in ['fullName','address','city','state','zipcode','phone','email']:
        print 'dbg1',x,formDat[x]
        values.append(formDat[x])
      #tmp = ['aaron boxer','24 adams st.','arlington','ma','02474','978-821-9102','aboxer51@yahoo.com']
      #values = ['joan goodman','24 Adams St.','Arlington','MA','02474','978-821-9102','aboxer51@yahoo.com']
      self.wks.append_row(values)
      print 'dbg2',values
      return True
    except:
      return False


  def addRow2(self,rowNum):
    try:
      values = ['Aaron Boxer','24 Adams St.','Arlington','MA','02474','978-821-9102','aboxer51@yahoo.com']
      self.wks.append_row(values)
      print 'dbg3'
      return True
    except:
      return False