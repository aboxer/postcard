import requests
import re
import lxml
from bs4 import BeautifulSoup
#from google.appengine.api import urlfetch
import logging

#compare two texts that may be different encodings
def eqText(a,b):
  if type(a) == type(b): #if they are the same encoding , do a simple comparison
    return (a == b)
  elif type(a) == unicode: #if one is unicode, convert to ascii, replacing undecodable points with ?
    aAscii = a.encode('ascii','replace')
    bAscii = b
  else:
    bAscii = b.encode('ascii','replace')
    aAscii = a

  if len(aAscii) != len(bAscii): #not equal if length differs
    return False
  for i in range(len(aAscii)): #one character at a time compare
    if aAscii[i] != '?' and bAscii[i] != '?': #skip comparing ?
      if aAscii[i] != bAscii[i]: #fail if ascii doesn't match
        return False
  return True
 
def nameSwitch(name):
  tmp = name.split()
  suffixes = ['Jr.','III'] #all the suffixes in MA senator & rep names
  for suffix in suffixes: #discard suffixes
    if tmp[-1] == suffix:
      last = tmp.pop()

  last = tmp.pop() 
  if last[-1] == ',': #last name may have a comma after suffix is removed
    last = last[:-1] 

  first = ''
  for wd in tmp:
    first += wd + ' '
  first = first[:-1]

  return last + ', ' + first

def space2Plus(field):
  wds = field.split()
  bar = ''
  for wd in wds:
    bar = bar + wd + '+'
  return bar[:-1]

def mkAdrVal(adr):
  field = adr.replace('#',' ')
  return space2Plus(field)

def mkZipVal(zipcode):
  #if isinstance(zipcode,basestring) == True: #its a string so it is probably a 9 digit zip code with a dash
  if isinstance(zipcode,str) == True: #its a string so it is probably a 9 digit zip code with a dash
    return zipcode[:5]
  else: #ints an integer so it is probably a valid 5 digit zipcode
    return str(zipcode).zfill(5)

def lkupLeg(adr):
  street = mkAdrVal(adr[0])
  town = space2Plus(adr[1])
  zipcode =  mkZipVal(adr[2])
  url = 'https://malegislature.gov/Search/FindMyLegislator?Address=' + street + '&City=' + town +'&ZipCode=' + zipcode

  try:
    #response = requests.get(url, timeout=60.0)
    response = requests.get(url, timeout=60.0, verify=False)
    return response.content
  except:
    logging.exception('Error fetching url')
  return None




def legScrape(content):
  #soup = BeautifulSoup(content,"lxml")
  soup = BeautifulSoup(content)
  profiles = soup.find_all(class_='legislatorProfile')
  legs = {}
  for profile in profiles:
    elem = profile.find(class_='role')
    role =  elem.string
    elem =  profile.find(class_='name')
    name =  elem.string
    #legs[role] = name
    legs[role] = nameSwitch(name)
  return legs

repRooms = [["Arciero", "James", "277"], ["Ashe", "Brian", "236"], ["Ayers", "Bruce", "167"], ["Balser", "Ruth", "167"], ["Barber", "Christine", "254"], ["Barrett", "John", "237"], ["Jay", "F.", "542"], ["Benson", "Jennifer", "236"], ["Berthiaume", "Donald", "540"], ["Biele", "David", "26"], ["Blais", "Natalie", "134"], ["Boldyga", "Nicholas", "167"], ["Brodeur", "Paul", "472"], ["Cabral", "Antonio", "466"], ["Cahill", "Daniel", "446"], ["Campbell", "Linda", "238"], ["Capano", "Peter", "443"], ["Carey", "Daniel", "33"], ["Cassidy", "Gerard", "136"], ["Chan", "Tackey", "42"], ["Ciccolo", "Michelle", "473F"], ["Connolly", "Mike", "33"], ["Coppinger", "Edward", "26"], ["Crocker", "William", "39"], ["Cronin", "Claire", "136"], ["Cullinane", "Daniel", "236"], ["Cusack", "Mark", "34"], ["Cutler", "Josh", "167"], ["D'Emilia", "Angelo", "548"], ["Day", "Michael", "136"], ["Decker", "Marjorie", "33"], ["DeCoste", "David", "443"], ["DeLeo", "Robert", "356"], ["Devers", "Marcos", "527A"], ["Domb", "Mindy", "134"], ["Donahue", "Daniel", "39"], ["Donato", "Paul", "481"], ["Dooley", "Shawn", "167"], ["Driscoll", "William", "446"], ["DuBois", "Michelle", "473F"], ["Durant", "Peter", "33"], ["Dykema", "Carolyn", "127"], ["Ehrlich", "Lori", "174"], ["Elugardo", "Nika", "448"], ["Farley-Bouvier", "Tricia", "156"], ["Ferguson", "Kimberly", "473B"], ["Fernandes", "Dylan", "472"], ["Ferrante", "Ann-Margaret", "42"], ["Finn", "Michael", "274"], ["Fiola", "Carole", "236"], ["Frost", "Paul", "542"], ["Galvin", "William", "166"], ["Garballey", "Sean", "540"], ["Garlick", "Denise", "238"], ["Garry", "Colleen", "238"], ["Gentile", "Carmine", "167"], ["Gifford", "Susan", "124"], ["Golden", "Thomas", "473B"], ["Gonzalez", "Carlos", "26"], ["Gordon", "Kenneth", "146"], ["Gouveia", "Tami", "146B"], ["Gregoire", "Danielle", "23"], ["Haddad", "Patricia", "370"], ["Haggerty", "Richard", "540"], ["Harrington", "Sheila", "237"], ["Hawkins", "James", "472"], ["Hay", "Stephan", "254"], ["Hecht", "Jonathan", "22"], ["Hendricks", "Christopher", "237"], ["Higgins", "Natalie", "527A"], ["Hill", "Bradford", "128"], ["Hogan", "Kate", "163"], ["Holmes", "Russell", "254"], ["Honan", "Kevin", "38"], ["Howitt", "Steven", "237"], ["Hunt", "Daniel", "166"], ["Hunt", "Randy", "136"], ["Jones", "Bradley", "124"], ["Kafka", "Louis", "185"], ["Kane", "Hannah", "167"], ["Kearney", "Patrick", "39"], ["Keefe", "Mary", "466"], ["Kelcourse", "James", "130"], ["Khan", "Kay", "146"], ["LaNatra", "Kathleen", "236"], ["Lawn", "John", "445"], ["LeBoeuf", "David", "146A"], ["Lewis", "Jack", "43"], ["Linsky", "David", "146"], ["Livingstone", "Jay", "472"], ["Lombardo", "Marc", "443"], ["Madaro", "Adrian", "134"], ["Mahoney", "John", "130"], ["Malia", "Elizabeth", "238"], ["Mariano", "Ronald", "343"], ["Mark", "Paul", "160"], ["Markey", "Christopher", "527A"], ["McGonagle", "Joseph", "279"], ["McKenna", "Joseph", "33"], ["McMurtry", "Paul", "171"], ["Meschino", "Joan", "34"], ["Michlewitz", "Aaron", "243"], ["Minicucci", "Christina", "448"], ["Miranda", "Liz", "236"], ["Mirra", "Lenny", "548"], ["Mom", "Rady", "544"], ["Moran", "Frank", "448"], ["Moran", "Michael", "39"], ["Muradian", "David", "156"], ["Muratore", "Mathew", "39"], ["Murphy", "James", "254"], ["Murray", "Brian", "136"], ["Nangle", "David", "479"], ["Naughton", "Harold", "167"], ["Nguyen", "Tram", "33"], ["O'Connell", "Shaunna", "237"], ["O'Day", "James", "540"], ["Orrall", "Norman", "540"], ["Parisella", "Jerald", "156"], ["Peake", "Sarah", "7"], ["Peisch", "Alice", "473G"], ["Petrolati", "Thomas", "146"], ["Pignatelli", "Smitty", "473F"], ["Poirier", "Elizabeth", "124"], ["Provost", "Denise", "473B"], ["Puppolo", "Angelo", "122"], ["Robertson", "David", "473F"], ["Robinson", "Maria", "22"], ["Rogers", "David", "544"], ["Rogers", "John", "162"], ["Roy", "Jeffrey", "43"], ["Ryan", "Daniel", "36"], ["Sabadosa", "Lindsay", "443"], ["Santiago", "Jon", "130"], ["Scaccia", "Angelo", "167"], ["Schmid", "Paul", "466"], ["Silvia", "Alan", "167"], ["Smola", "Todd", "124"], ["Soter", "Michael", "443"], ["Speliotis", "Theodore", "20"], ["Stanley", "Thomas", "167"], ["Straus", "William", "134"], ["Sullivan", "Alyson", "39"], ["Tosado", "Jose", "33"], ["Tucker", "Paul", "473G"], ["Tyler", "Chynah", "155"], ["Ultrino", "Steven", "446"], ["Vargas", "Andres", "136"], ["Vega", "Aaron", "146"], ["Velis", "John", "174"], ["Vieira", "David", "167"], ["Vincent", "RoseLee", "473F"], ["Vitolo", "Tommy", "443"], ["Wagner", "Joseph", "234"], ["Walsh", "Thomas", "276"], ["Whelan", "Timothy", "542"], ["Whipps", "Susannah", "540"], ["Williams", "Bud", "160"], ["Wong", "Donald", "541"], ["Zlotnik", "Jonathan", "26"]]

senRooms = [["Barrett", "Michael", "109-D"], ["Boncore", "Joseph", "112"], ["Brady", "Michael", "416-A"], ["Brownsberger", "William", "319"], ["Chandler", "Harriette", "333"], ["Chang-Diaz", "Sonia", "111"], ["Collins", "Nick", "312-D"], ["Comerford", "Joanne", "70C"], ["Creem", "Cynthia", "312-A"], ["Crighton", "Brendan", "520"], ["Cyr", "Julian", "309"], ["deMacedo", "Viriato", "313-C"], ["DiDomenico", "Sal", "208"], ["DiZoglio", "Diana", "416-B"], ["Eldridge", "James", "511-C"], ["Fattman", "Ryan", "213-A"], ["Feeney", "Paul", "215"], ["Finegold", "Barry", "507"], ["Friedman", "Cindy", "413-D"], ["Gobi", "Anne", "513"], ["Hinds", "Adam", "109-E"], ["Humason", "Donald", "313-A"], ["Jehlen", "Patricia", "424"], ["Keenan", "John", "413-F"], ["Kennedy", "Edward", "405"], ["Lesser", "Eric", "413-C"], ["Lewis", "Jason", "511-B"], ["Lovely", "Joan", "413-A"], ["Montigny", "Mark", "312-C"], ["Moore", "Michael", "109-B"], ["O'Connor", "Patrick", "419"], ["Pacheco", "Marc", "312-B"], ["Rausch", "Rebecca", "218"], ["Rodrigues", "Michael", "212"], ["Rush", "Michael", "109-C"], ["Spilka", "Karen", "332"], ["Tarr", "Bruce", "308"], ["Timilty", "Walter", "213-B"], ["Tran", "Dean", "504"], ["Welch", "James", "413-B"]]

def mkRoute(senRep):
  global repRooms
  global senRooms
  tmp = senRep['Senator'].split()
  for senRoom in senRooms:
    if eqText(tmp[0][:-1],senRoom[0]) and eqText(tmp[1],senRoom[1]): #chop the comma off the end of last name
      tmp2 = senRoom[2]
      break
  tmp2 = tmp2 + '/'
  tmp = senRep['Representative'].split()
  for repRoom in repRooms:
    if eqText(tmp[0][:-1],repRoom[0]) and eqText(tmp[1],repRoom[1]): #chop the comma off the end of last name
      tmp2 = tmp2 + repRoom[2]
      break
  return tmp2
