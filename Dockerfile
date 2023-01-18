FROM python:3.11.1
WORKDIR /app
ENV PORT 8080
ENV HOST 0.0.0.0
COPY ./requirements.txt /app
ADD ./imdb.py /app
RUN pip install -r requirements.txt
CMD ["python", "imdb.py"]