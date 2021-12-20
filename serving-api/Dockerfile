#docker pull tiangolo/uvicorn-gunicorn-fastapi:latest
#docker pull tiangolo/uvicorn-gunicorn-fastapi:python3.9-slim
FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7

COPY . /app

WORKDIR /app/

#ENV PYTHONUNBUFFERED 1
RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

EXPOSE 8000


#RUN apt-get update && \
#    apt-get install -y --no-install-recommends netcat && \
#    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
#
#COPY poetry.lock pyproject.toml ./
#RUN pip install poetry==1.1 && \
#    poetry config virtualenvs.in-project true && \
#    poetry install --no-dev
#
#CMD poetry run alembic upgrade head && \
#    poetry run uvicorn --host=0.0.0.0 app.main:app
