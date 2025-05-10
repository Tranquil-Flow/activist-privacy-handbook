FROM python:alpine3.17

WORKDIR /app
COPY ./app.py ./api.py ./cli.py ./requirements.txt /app/
COPY ./contracts/DeadManSwitch.json /app/contracts/
RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT ["python", "api.py"]