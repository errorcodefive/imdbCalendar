FROM python:3.1.1
WORKDIR /app
COPY ./requirements.txt /app
ADD ./imdb.py /app
RUN pip install -r requirements.txt
CMD ["python", "imdb.py"]