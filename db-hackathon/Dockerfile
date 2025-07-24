FROM python:3.12

WORKDIR /app
COPY . /app

ENV HOME=/app
ENV VVM_HOME=/app/.vvm


RUN pip install setuptools
RUN pip3 install eth-brownie
RUN pip install -r requirements.txt

RUN brownie networks add Ethereum ganache host=http://172.30.251.113:8545 chainid=1337

RUN mkdir -p /app/.vvm /app/.solcx && chmod -R 777 /app

EXPOSE 8080
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8080"]