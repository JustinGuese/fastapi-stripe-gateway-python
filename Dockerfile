FROM python:3.11-slim
RUN mkdir /app
WORKDIR /app
COPY ./src/requirements.txt /app
RUN pip install -r requirements.txt
COPY ./src/app.py /app/
CMD ["uvicorn", "app:app", "--host", "0.0.0.0"]