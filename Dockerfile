FROM python:2.7
LABEL maintainer="Isidro Moran"

COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
RUN python init_db.py
EXPOSE 3111

# command to run on container start
CMD [ "python", "app.py" ]
