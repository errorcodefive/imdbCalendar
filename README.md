# imdbCalendar

Generates a calendar with upcoming movie dates.

I scrape IMDB's coming soon for the next 9 months and uploads the .ics file to AWS S3.

Pass AWS_ACCESS_KEY and AWS_SECRET_KEY as environment variables or parameters

Requires:
  bs4
  requests
  urllib2
  smtplib
  icalendar
  boto3
  lxml
  PyMovieDb
