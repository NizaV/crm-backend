FROM python:3.7-alpine
WORKDIR /python-docker
COPY requirements.txt ./
RUN pip install psycopg2-binary
RUN pip install --upgrade setuptools
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]