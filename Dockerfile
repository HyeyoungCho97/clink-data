# 이미지의 기반이 될 베이스 이미지
FROM python:3.7

#작업 디렉토리 설정
WORKDIR /app

#현재 디렉토리의 파일들을 복사
COPY . /app

#필요한 패키지 설치
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

#cmd 실행
CMD python insertDataByDay.py
