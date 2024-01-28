FROM python:3.11.4

WORKDIR /moment

COPY . /moment

COPY aioredis.patch /tmp/

RUN pip install -r requirements.txt

RUN pip install gunicorn
RUN pip show aioredis
RUN patch /usr/local/lib/python3.11/site-packages/aioredis/exceptions.py < /tmp/aioredis.patch

EXPOSE 8000

CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "-w", "4", "-b", "0.0.0.0:8000", "main:app", "--preload"]
