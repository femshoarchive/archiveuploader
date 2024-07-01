FROM python:3-alpine

ENV GIT_URL=https://github.com/femshoarchive/femshoarchive.github.io \
    GIT_PATH=/tmp

WORKDIR /usr/src/app

RUN apk --no-cache add gcc git

COPY main.py ./
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

CMD [ "python", "./main.py" ]