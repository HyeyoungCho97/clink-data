FROM python:3.7
COPY insertDataByDay.py insertDataByDay.py 
RUN pip3 install -r requirements.txt