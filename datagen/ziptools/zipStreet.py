#combine json files for each zipcode into one database
import sys
import json

rf = open('zip2city.json', 'r')
r = rf.read()  #read in all the bytes into one string
zip2town = json.loads(r)
rf.close()
 
streetDB = {}
for i in range(len(zip2town)):
  zipcode = str(zip2town[i][0]).zfill(5)
  filename = '../zip2adr/adr_' + zipcode  + '.json'
  
  rf = open(filename, 'r')
  r = rf.read()  #read in all the bytes into one string
  streets = json.loads(r)
  try:
    streets[0]['StreetName']
    tmp = []
    for street in streets:
      tmp.append(street['StreetName'])
    rf.close()
    streetDB[zipcode] = tmp
  except:
    print zip2town[i]

wf = open('streetDB.json','w')
json.dump(streetDB, wf)
wf.close()

