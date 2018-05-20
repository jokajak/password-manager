FROM python:2 as builder

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY ./requirements.txt /usr/src/app/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY . /usr/src/app

RUN [ "/bin/bash", "/usr/src/app/scripts/build", "install --backends flask --frontends beta delta"]

FROM python:2

# set working directory
RUN mkdir -p /usr/share/app
WORKDIR /usr/share/app

COPY --from=builder /usr/src/app/target/flask /usr/share/app

# install requirements
RUN pip install --no-cache-dir -r /usr/share/app/requirements.txt

ENV FLASK_ENV="docker"

EXPOSE 5000
# run server
#CMD ["python", "/usr/share/app/run.py"]
CMD ["python", "/usr/share/app/manage.py", "runserver"]
