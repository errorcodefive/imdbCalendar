from bs4 import BeautifulSoup

from icalendar import Calendar, Event
import time
import requests

import datetime
import smtplib

import boto3
import sys
import os
import lxml
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
		output = "Name: " + self.name + "\nRating: "+ self.rating +"\nGenre: "+ setToString(self.genre) +"\nDescription: "+ self.desc +"\nDirector: "+self.direct+"\nActors: "+setToString(self.actors)
		return output
	
def setToString(set):
	output = ""
	for i in set:
		if i:
			output = output + i.get_text().strip() +" | "
	return output.strip()
	

today_date = time.strftime("%d")
today_month=time.strftime("%m")
today_year = time.strftime("%Y")

movieClass = []
for i in range(0,10):
	url = "http://www.imdb.com/movies-coming-soon/"+str(today_year) + "-"+str(today_month).zfill(2)+"/?ref_=cs_dt_nx"
	print(url)
	today_month = int(today_month)+1
	if int(today_month) == 13:
		today_month = 1
		today_year = int(today_year)+1

	r = requests.get(url)
	
	data = r.text
	soup = BeautifulSoup(data, "lxml")
	rawHTML=soup.prettify()
	
	movieDiv = soup.div.find_all('div', class_='list_item', itemtype="http://schema.org/Movie")
	#print(len(movieDiv))
	try:
		movieDiv.pop()
	except IndexError:
		print("IndexError, movieDiv is empty")
	for mov in movieDiv:
		tempMov = MovieInfo()
		#print(mov.find(name="h4"))
		tempMov.name = mov.find(name = "h4").a.get_text().strip() #working Sep 2018
		#print("Movie Name: "+ tempMov.name)
		if mov.find(name = "span", class_="certRating"):
			tempMov.rating=mov.find(name = "span", class_="certRating").get_text().strip() #working Sep 2018
			#print("Movie Rating: "+ tempMov.rating)

		if mov.find(name="p", class_="cert-runtime-genre").find_all(name = "span", itemprop = ""):
			tempMov.genre = mov.find(name="p", class_="cert-runtime-genre").find_all(name = "span", itemprop = "") #Working Sep 2018
			#print("Movie Genre: " + setToString(tempMov.genre[1:]))

		if mov.find(name = "div", class_ = "outline"):
			tempMov.desc=mov.find(name = "div", class_ = "outline").get_text().strip() #working Sep 2018
			#print("Movie Desc: " + tempMov.desc)
		if mov.find_all(name = "div", class_="txt-block")[0].span is not None:
			tempMov.direct = mov.find_all(name = "div", class_="txt-block")[0].span.a.get_text().strip() #working Sep 2018
			#print("Movie Direct: " + tempMov.direct)
		if mov.find_all(name = "div", class_="txt-block")[1].find_all(name="a"):

			tempMov.actors = mov.find_all(name = "div", class_="txt-block")[1].find_all(name="a") #working Sep 2018
			#print("Movie Actors: " + setToString(tempMov.actors))

		if mov.find(name = "h4"):
			if mov.find(name = "h4").a['href']:
				temp=mov.find(name = "h4").a['href']
				tempMov.IMDB = temp[7:16]
				#print("Movie ID: " + tempMov.IMDB)
		if tempMov.name:
			movieClass.append(tempMov)
			
cal = Calendar()
cal.add('prodid', 'IMDB Movie Releases')
cal.add('version', '2.0')
movie_count = 0
for m in movieClass:
	movie_count +=1
	getError = False
	url = "http://www.imdb.com/title/"+m.IMDB
	print(url)
	try:
		r = requests.get(url, timeout=300)
		mData = r.text
		mSoup = BeautifulSoup(mData, 'lxml')
		try:
			#print(mSoup.find(name="script", type="application/ld+json").get_text())
			#get json script
			parsed_json = json.loads(mSoup.find(name="script", type="application/ld+json").get_text())
			#grab the date published
			#print(parsed_json)
			#print (mSoup.find(name = "a", title="See more release dates").get_text())
			#print(parsed_json['datePublished'])
			m.temp = parsed_json['datePublished']
		except (TypeError, KeyError):
			getError = True
			
		if getError == False:
			print ("M.temp: " + m.temp)
			if len(m.temp)>8:
				m.rel_year = m.temp[:4]
				m.rel_month=m.temp[5:7]
				m.rel_day=m.temp[8:]
				print ("Adding to calendar")
				event = Event()
				event.add('summary', m.name)
				
				print (m.name)
				print ("\n")
				
				event.add('description',m.outToString()+"Link:"+url)
				event.add('dtstart',datetime.datetime(int(m.rel_year),int(m.rel_month),int(m.rel_day),21,0,0))
				event.add('dtend',datetime.datetime(int(m.rel_year),int(m.rel_month),int(m.rel_day),22,0,0))
				event.add('dtstamp',datetime.datetime.now())
				event['uid']=uuid.uuid4()
				cal.add_component(event)
	except:
		print("URLError")
print ("done")
try:
	ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY']
except KeyError:
	ACCESS_KEY_ID = str(sys.argv[1])
try:
	ACCESS_SECRET_KEY = os.environ['AWS_SECRET_KEY']
except KeyError:
	ACCESS_SECRET_KEY = sys.argv[2]

#print("access key: " + ACCESS_KEY_ID)
#print("access secret: " + ACCESS_SECRET_KEY)
s3 = boto3.resource('s3', aws_access_key_id = ACCESS_KEY_ID, aws_secret_access_key=ACCESS_SECRET_KEY)
data = cal.to_ical()
s3.Bucket('kc-calendars').put_object(Key="movie_calendar.ics", Body = data, ContentType='text/calendar', ACL = 'public-read')
#print (data)