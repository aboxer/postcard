import re
import json
print('mazips')

inf = open('maZips.txt','r')
zipList = []
for line in inf.readlines():
  if 'View Map' not in line:
    tmp = line.split()[:-1] #remove districts which is always one word
    zipList.append((int(tmp[0]),' '.join(tmp[1:]))) #save zipcode and city/town

with open('maZip.json', 'w') as outfile:
    json.dump(zipList, outfile)

#print(json.dumps(zipList, indent=2))
