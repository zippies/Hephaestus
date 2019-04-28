FROM python:2.7.12
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
ENV OAUTHLIB_INSECURE_TRANSPORT=true

EXPOSE 8080

CMD ["gunicorn","-c","gunicorn.py","manager:app"]
