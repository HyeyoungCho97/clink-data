from datetime import datetime
import time
import requests
import json
import pymysql
import schedule
import mysql_auth

#gpt 통신을 위한 key
file = open('openAI_key.txt', 'r')
key = file.read()

#데이터1 인물의 페르소나
persona = {
    "이름": "김 지영",
    "나이": 25,
    "거주지": "서울",
    "직업": "마케팅 전문가",
    "관심사": ["여행", "음악", "패션", "건강"],
    "성격": "외향적이고 사교적인 성격을 가지고 있으며, 새로운 사람들과의 만남을 즐깁니다. 호기심이 많고 창의적인 생각을 가지고 있으며, 도전적인 상황에 잘 적응합니다.",
    "라이프스타일": "다양한 음악 장르를 즐기며 주말에는 친구들과 함께 공연이나 클럽에 가기도 합니다. 여행을 좋아하여 자유로운 분위기의 여행지를 선호하며, 새로운 문화와 경험을 즐깁니다. 패션에 관심이 많아 트렌디한 스타일을 즐기고 스스로의 개성을 표현하는 것을 좋아합니다. 또한 건강에 관심이 많아 운동이나 요가를 즐기며 균형 잡힌 식단을 유지합니다.",
    "소셜 미디어 사용": ["인스타그램", "페이스북"],
    "목표": ["마케팅 분야에서 성장하고 전문성을 키우는 것", "세계 각지의 다양한 문화와 사람들을 경험하며 넓은 시각을 갖추는 것"]
}

#데이터2 결제내역 형식
payment_data = {
    "date": "2023-01-01",
    "transactions": [
        {
            "timestamp": "2023-01-01 09:30:15",
            "description": "스타벅스",
            "amount": 4500,
            "category": "음식점"
        },
        {
            "timestamp": "2023-01-01 12:15:30",
            "description": "홍대개미",
            "amount": 10900,
            "category": "음식점"
        },
        {
            "timestamp": "2023-01-01 15:45:20",
            "description": "ABC마켓",
            "amount": 35000,
            "category": "생활"
        }
    ]
}
#데이터3 category 범위
category_list = {"식료품": "001", 
                 "음식점": "002",
                 "생활": "003", 
                 "문화": "004", 
                 "숙박":"005", 
                 "교통":"006", 
                 "전자상거래": "007", 
                 "현금서비스": "008", 
                 "기타":"009"}

# db에 저장
def putInDB(payment):
    # DB 연결
    info = mysql_auth.info
    db = pymysql.connect(   
                        host=info["host"],
                        user=info["user"],
                        passwd=info["passwd"],
                        port=info["port"],
                        db=info["db"],
                        charset=info["charset"]
                        )
    cursor = db.cursor()

    ##데이터 삽입
    sql = "INSERT INTO Account_History (transaction_datetime, account_no, bank_code, user_no, transaction_amount, transaction_info_content, transaction_code,register_datetime,register_id, history_delete_yn) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    cursor.execute(sql, (datetime.strptime(payment["timestamp"], '%Y-%m-%d %H:%M:%S'), "372-01-214931", "026", "00000", payment["amount"], payment["description"], category_list[payment["category"]], datetime.now(), "01010", "n"))
    db.commit()
    db.close()

    #데이터 삭제
    payment_list.pop(0)



# gpt를 통해 당일 결제될 내역을 받아옴
def getTodaysPayment():
    url = "https://api.openai.com/v1/chat/completions"
    
    #오늘 날짜 
    today = datetime.now()
    str_today = str(today.year)+"년 "+str(today.month)+"월 "+str(today.day)+"일"
    
    # 대화 형식의 메시지 생성
    messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "assistant", "content": json.dumps(persona)},
            {"role": "assistant", "content": json.dumps(payment_data)},
            {"role": "assistant", "content": json.dumps(category_list)},
            {"role": "assistant", "content": "결제내역의 description항목은 스타벅스, 맥도날드 같은 거래가 이루어진 장소야"},
            {"role": "assistant", "content": "결제내역의 amount항목은 결제한 가격이야"},
            {"role": "assistant", "content": "카테고리의 식료품은 마트, 슈퍼마켓, 시장에서 구매한 내역이야"},
            {"role": "assistant", "content": "카테고리의 음식점은 카페, 음식점에서 구매한 내역이야"},
            {"role": "assistant", "content": "카테고리의 생활은 의류, 신발, 가전제품, 가구를 구매한 내역이야"},
            {"role": "assistant", "content": "카테고리의 문화는 영화관, 공연장, 스포츠, 놀이공원에서 구매한 내역이야"},
            {"role": "assistant", "content": "카테고리의 숙박은 모텔, 호텔에서 구매한 내역이야"},
            {"role": "assistant", "content": "카테고리의 교통은 항공사, 철도, 버스, 택시, 여행사에서 구매한 내역이야"},
            {"role": "assistant", "content": "카테고리의 전자상거래는 온라인쇼핑, 인터넷서비스, 게임에서 구매한 내역이야"},
            {"role": "assistant", "content": "카테고리의 현금서비스는 ATM, 현금인출을 한 내역이야"},
            {"role": "assistant", "content": "카테고리의 기타는 약국, 병원, 미용실, 세탁소, 편의점에서 구매한 내역이야"},
            {"role": "user", "content": "주어진 페르소나랑 결제내역을 기반으로 "+str_today+"의 새로운 결제내역을 생성해줘. 주어진 결제내역이랑 같은 JSON 형식으로, 카테고리는 주어진 카테고리들 중에 하나로 만들어줘."}
        ]
    #요청 헤더
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {key}"
    }

    #요청 데이터
    data = {
        "model": "gpt-3.5-turbo",
        "messages": messages,
        "temperature": 1  # 다양성을 조절하는 temperature 값 설정
    }

    cnt=0
    while cnt<1:
        try:
            response = requests.post(url, headers=headers, json=data)
            content = response.json()["choices"][0]["message"]["content"]
            cnt += 1

            return eval(content)["transactions"]
        
        except Exception as e:
            print(e)

    


# 메인 함수: 현재시간 확인해서 함수 호출
def main():
    cnt=0
    while cnt<1:
        try: 
            #정각에 aws 호출, 당일 결제내역(payment)을 받아옴
            global payment_list
            payment_list = getTodaysPayment()
            payment_list = sorted(payment_list, key=lambda k:k['timestamp'])
            file = open('todaySchedule.txt', 'w')
            #스케줄러에 등록
            for p in payment_list:
                print(p)
                if p["category"] not in category_list: 
                    raise Exception('카테고리 오류')
                file.write(str(p)+'\n')
                getTime = datetime.strptime(p["timestamp"], '%Y-%m-%d %H:%M:%S')
                hour = "0"+str(getTime.hour) if (len(str(getTime.hour))==1)  else str(getTime.hour)
                minute = "0"+str(getTime.minute) if (len(str(getTime.minute))==1)  else str(getTime.minute)
                strTime = hour+":"+minute
                print(strTime)
                schedule.every().day.at(strTime).do(putInDB, p)
            file.close()
            cnt+=1

        except Exception as e:
            print(e)

    while True:
        # 정해진 결제내역을 모두 입력한 경우 해제
        if len(payment_list)==0 : 
            break

        schedule.run_pending()
        time.sleep(60)

# 프로그램 실행
if __name__ == '__main__':
    main()
