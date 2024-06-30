FROM python:3.11.3

WORKDIR /bot

COPY ./Pipfile .

COPY ./.env .

RUN pip install pipenv

RUN pipenv install

COPY ./main.py ./

COPY ./parsers.py .

COPY ./rcon_listener.py .

COPY ./rcon.py .

COPY ./login_observer.py .

COPY ./data.py .

COPY ./logger.py .

COPY ./chat_observer.py .

COPY ./database.py .

COPY ./playtime_client.py .

COPY ./session_topic.py .

COPY ./compute.py .

CMD ["pipenv", "run", "python", "main.py"]
