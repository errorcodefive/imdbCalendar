FROM python:3.6.6-jessie
WORKDIR /app
COPY ./requirements.txt /app
ADD ./imdb.py /app
RUN pip install -r requirements.txt
CMD ["python", "imdb.py"]