#check that no zipcode has more than one town. NOTE: A city may have many zipcodes
import sys
import json
import os.path

rf = open('zip2city.json', 'r')
r = rf.read()  #read in all the bytes into one string
zip2town = json.loads(r)
rf.close()
 
for i in range(len(zip2town)-1):
  filename = '../zip2adr/adr_' + str(zip2town[i][0]).zfill(5)  + '.json'
  if not os.path.exists(filename):
    print filename

  for j in range(i+1,len(zip2town)):
      if zip2town[i][0] == zip2town[j][0]:
        print 'duplicate!!', zip2town[i],zip2town[j]

print 'zipcodes ', len(zip2town), 'files', i+2 #i starts at zero and ends one less than number of files 
