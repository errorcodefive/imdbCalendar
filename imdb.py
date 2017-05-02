from bs4 import BeautifulSoup
import os
from icalendar import Calendar, Event
import time
import requests
import urllib2
import datetime
import smtplib

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
		output = "Rating: "+ self.rating +"\nGenre: "+ setToString(self.genre) +"\nDescription: "+ self.desc +"\nDirector: "+self.direct+"\nActors: "+setToString(self.actors)
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

opener  = urllib2.build_opener()
opener.addheaders = [('User-agent', 'Mozilla/5.0')]
movieClass = []
for i in range(0,9):
	
	url = "http://www.imdb.com/movies-coming-soon/"+str(today_year) + "-"+str(today_month).zfill(2)+"/?ref_=cs_dt_nx"
	today_month = int(today_month)+1
	if int(today_month) == 13:
		today_month = 1
		today_year = int(today_year)+1
		
	
	r = opener.open(url)
	f = open("raw_html.html", 'w')

	data = r.read()
	soup = BeautifulSoup(data, 'lxml')
	rawHTML=soup.prettify().encode('utf8')
	f.write(rawHTML)

	f.close


	movieDiv = soup.div.find_all(itemtype="http://schema.org/Movie")
	movieDiv.pop()
	for mov in movieDiv:
		tempMov = MovieInfo()
		tempMov.name = mov.find(name = "a", itemprop="url").get_text().strip()

		if mov.find(name = "span", itemprop="contentRating"):
			tempMov.rating=mov.find(name = "span", itemprop="contentRating").get_text().strip()

		if mov.find_all(name = "span", itemprop = "genre"):
			tempMov.genre = mov.find_all(name = "span", itemprop = "genre")

		if mov.find(name = "div", itemprop = "description"):
			tempMov.desc=mov.find(name = "div", itemprop = "description").get_text().strip()

		if mov.find(name = "span", itemprop="director"):
			tempMov.direct = mov.find(name = "span", itemprop="director").span.a.get_text().strip()

		if mov.find_all(name = "span", itemprop = "actors"):
			tempMov.actors = mov.find_all(name = "span", itemprop = "actors")

		if mov.find(name = "h4", itemprop="name"):
			if mov.find(name = "h4", itemprop="name").a['href']:
				temp=mov.find(name = "h4", itemprop="name").a['href']
				tempMov.IMDB = temp[7:16]
		if tempMov.name:
			movieClass.append(tempMov)
			
print "Movie Info Created"



cal = Calendar()
cal.add('prodid', 'IMDB Movie Releases')
cal.add('version', '1.0')
movie_count = 0
for m in movieClass:
	movie_count +=1
	print "Movie Count: " + str(movie_count)
	url = "http://www.imdb.com/title/"+m.IMDB
	print "Movie URL: " + url
	r = opener.open(url)
	mData = r.read()
	mSoup = BeautifulSoup(mData)
	print "Movie HTML Loaded"
	try:
		m.temp = mSoup.find(name = "meta", itemprop="datePublished")['content']
	except TypeError:
		print ("EROROROROROR")
		

	print m.temp
	if len(m.temp)>8:
		m.rel_year = m.temp[:4]
		m.rel_month=m.temp[5:7]
		m.rel_day=m.temp[8:]
		print"Adding to calendar"
		event = Event()
		event.add('summary', m.name)
		
		print m.name
		
		event.add('description',m.outToString()+"Link:"+url)
		event.add('dtstart',datetime.datetime(int(m.rel_year),int(m.rel_month),int(m.rel_day),21,0,0))
		event.add('dtend',datetime.datetime(int(m.rel_year),int(m.rel_month),int(m.rel_day),22,0,0))
		event.add('dtstamp',datetime.datetime.now())
		cal.add_component(event)
f2=open('IMDB.ics','wb')
f2.write(cal.to_ical())
f2.close()
print "done"


	
