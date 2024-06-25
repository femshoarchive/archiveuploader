FROM python:3-alpine

ENV GIT_URL=https://github.com/femshoarchive/femshoarchive.github.io \
    GIT_PATH=repo

WORKDIR /usr/src/app

COPY main.py ./
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

CMD [ "python", "./main.py" ]