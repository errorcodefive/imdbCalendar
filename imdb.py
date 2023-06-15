from urllib.request import Request, urlopen
from bs4 import BeautifulSoup

from icalendar import Calendar, Event
from PyMovieDb import IMDB

import time
import datetime
import boto3
import sys
import os
import uuid
import json

class MovieInfo:
	name=""
	rel_day=0
	rel_month=0
	rel_year=0
	rating=""
	genre=[]
	desc=""
	direct=""
	actors=[]
	temp=""
	IMDB=""
	def outToString(self):
		output = "Name: " + str(self.name) + "\nRating: "+ str(self.rating) +"\nGenre: "+ setToString(self.genre) +"\nDescription: "+ str(self.desc) +"\nDirector: "+str(self.direct)+"\nActors: "+setToString(self.actors)
		return output
	
def setToString(set):
	output = ""
	for i in set:
		if i:
			output = output + str(i).strip() +" | "
	return output.strip()
	

today_date = time.strftime("%d")
today_month=time.strftime("%m")
today_year = time.strftime("%Y")

movieClass = []

#v2_url="https://www.imdb.com/calendar?region=CA&ref_=rlm"
v2_url="https://www.imdb.com/calendar/?ref_=rlm&region=&type=MOVIE"
hdr={'User-Agent': 'Mozilla/5.0'}
#r=requests.get(v2_url)
r=Request(v2_url,headers=hdr)
page=urlopen(r)

print("URL: "+v2_url)
#data=page.text
soup = BeautifulSoup(page, 'lxml')
rawHTML=soup.prettify()
f=open("rawHTML.txt","a", encoding='utf-8')
f.write(rawHTML)
f.close()
movieDiv=soup.find("main")
#movieDiv=soup.find("")
movie_list=movieDiv.find_all("a")
#print("divs: " + str(movie_list))
try:
	movie_list.pop()
except IndexError:
	print("IndexError, movie_list is empty")

for mov in movie_list:
	tempMov=MovieInfo()
	tempMov.name=mov.string
	temp=mov['href'].split("/")[2]
	tempMov.IMDB=temp

	#print(tempMov.IMDB)
	if(tempMov.IMDB[1]=="t"):
		movieClass.append(tempMov)

imdb=IMDB()
cal = Calendar()
cal.add('prodid', 'IMDB Movie Releases')
cal.add('version', '2.0')
movie_count = 0
list_movies=[]
for m in movieClass:
	temp_m=m
	temp_m.actors=[]
	movie_count +=1
	getError = False
	url = "http://www.imdb.com/title/"+m.IMDB
	#print(url)
	try:
		temp_json=json.loads(imdb.get_by_id(m.IMDB))
		#Was page found:
		if('status' in temp_json ):
			getError=True
		#print(temp_json)
		for x in list_movies:
			if temp_m.IMDB==x:
				getError=True
				print("duplicate movie found: " + str(temp_m.IMDB))

		if getError == False:
			temp_m.temp=temp_json['datePublished']
			print(temp_m.temp)
			temp_m.rating=temp_json['contentRating']
			temp_m.genre=temp_json['genre']
			temp_m.desc=temp_json['description']
			temp_m.direct=temp_json['director'][0]['name']
			for acts in temp_json['actor']:
				temp_m.actors.append(acts['name'])
			#print ("M.temp: " + str(m.temp))
			if len(m.temp)>8:
				temp_m.rel_year = m.temp[:4]
				temp_m.rel_month=m.temp[5:7]
				temp_m.rel_day=m.temp[8:]
				print ("Adding to calendar")
				event = Event()
				event.add('summary', temp_m.name)
				list_movies.append(m.IMDB)
				print (temp_m.name)
				#print ("\n")
				
				event.add('description',m.outToString()+"Link:"+url)
				event.add('dtstart',datetime.date(int(temp_m.rel_year),int(temp_m.rel_month),int(temp_m.rel_day)))
				#event.add('dtend',datetime.datetime(int(temp_m.rel_year),int(temp_m.rel_month),int(temp_m.rel_day))+datetime.timedelta(hours=1))
				event.add('dtstamp',datetime.datetime.now())
				event['uid']=uuid.uuid4()
				cal.add_component(event)
				print(temp_m.outToString())
	except TypeError as e:
		print("Type Error")
	except Exception as e:
		print(e)
print ("done")
try:
	ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY']
except Exception as e:
	ACCESS_KEY_ID = str(sys.argv[1])
try:
	ACCESS_SECRET_KEY = os.environ['AWS_SECRET_KEY']
except KeyError:
	ACCESS_SECRET_KEY = sys.argv[2]

#print("access key: " + ACCESS_KEY_ID)
#print("access secret: " + ACCESS_SECRET_KEY)
try:
	s3 = boto3.resource('s3', aws_access_key_id = ACCESS_KEY_ID, aws_secret_access_key=ACCESS_SECRET_KEY)
	data = cal.to_ical()
	s3.Bucket('kc-calendars').put_object(Key="movie_calendar.ics", Body = data, ContentType='text/calendar', ACL = 'public-read')
except Exception as e:
	print(e)
print("Completed transfer")

sys.exit(0)
