import pymysql
import mysql_auth

#오늘 결제내역 가져오기
def getYesterdayHistoryTotalAmount(cursor):

    sql="SELECT ah.user_no, date_format(ah.transaction_datetime, '%Y-%m-%d'), SUM(ah.transaction_amount), cd.challenge_amount, cd.challenge_no FROM Account_History ah JOIN Challenge_Detail cd ON ah.user_no = cd.user_no WHERE date_format(ah.transaction_datetime, '%Y-%m-%d') = date_format(now()-INTERVAL 1 DAY, '%Y-%m-%d');"
    cursor.execute(sql)
    
    #데이터 다루기
    yesterdayHistory = [item for item in cursor.fetchall()]
    return yesterdayHistory

#성공정보 저장
def insertSuccessData(cursor, history):
    sql = "INSERT INTO Callenge_Success_Detail (challenge_detail_success_date, challenge_no, user_no, challenge_detail_success_amount, register_datetime, register_id) VALUES ( %s, %s, %s, %s now(), '01010') "
    cursor.execute(sql, history[1], history[4], history[0], history[2])

def main():

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

    yesterdayHistory = getYesterdayHistoryTotalAmount(cursor)
    print(yesterdayHistory)
    for history in yesterdayHistory:
        # 오늘 총 사용금액 <= 목표금액
        if history[2] <= history[3]:
            insertSuccessData(cursor, history)
    
    db.close()

# 프로그램 실행
if __name__ == '__main__':
    main()
