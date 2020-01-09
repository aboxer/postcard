# -*- coding: utf-8 -*-
import re
import json
import csv
print('legRooms')

def mkLegs(lines):
  roomList = []
  for line in lines:
    leg = line.split()
    legLen = len(leg)
    if legLen > 4:
      legRoom = [leg[1],leg[0],leg[-4]]
      roomList.append(legRoom)
  return roomList

def dupChk(rooms):
  for i in range(len(rooms)-1):
    for j in range(i+1,len(rooms)):
      #if rooms[i][0] == rooms[j][0]:
      #if rooms[i][2] == rooms[j][2] and rooms[i][0][0] == rooms[j][0][0] and rooms[i][1][0] == rooms[j][1][0]:
      #if rooms[i][2] == rooms[j][2] and rooms[i][0][0:2] == rooms[j][0][0:2]:
      if rooms[i][2] == rooms[j][2] and rooms[i][0][0:2] == rooms[j][0:2][0] and rooms[i][1][0] == rooms[j][1][0]:
        print('duplicate legroom',  rooms[i], rooms[j])

inf = open('maRep.txt','r')
rooms = mkLegs(inf.readlines())
print(len(rooms))
dupChk(rooms)
with open('maRepRoom.json', 'w') as outfile:
  json.dump(rooms, outfile)

#with open('maSenRoom.csv', 'w', newline='') as csvfile:
with open('maRepRoom.csv', 'w') as csvfile:
  spamwriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
  for room in rooms:
    spamwriter.writerow(room) 


inf = open('maSen.txt','r')
rooms = mkLegs(inf.readlines())
print(len(rooms))
dupChk(rooms)
with open('maSenRoom.json', 'w') as outfile:
  json.dump(rooms, outfile)

#with open('maSenRoom.csv', 'w', newline='') as csvfile:
with open('maSenRoom.csv', 'w') as csvfile:
  spamwriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
  for room in rooms:
    spamwriter.writerow(room) 


