import time
import pyupbit
import pandas as pd


# 코인 목록 가져오기
coins = pyupbit.get_tickers(fiat="KRW")
# 분봉 데이터를 저장할 빈 DataFrame 초기화
df_minute = pd.DataFrame()

# 각 코인의 분봉 데이터를 가져와서 합치기
for coin in coins:
    # OHLCV(open, high, low , close, volume) 당일 시가, 고가, 저가, 종가, 거래량에 대한 데이터
    # interval="minute1" 은 분봉, to는 지정 시각까지의 데이터
    tempDf = pyupbit.get_ohlcv(coin, interval="minute1", to="2024-03-28", count= 1440)
    # API 요청 제한: 분당 600회, 초당 10회 : 자동으로 0.1초 간격으로 호출하지만 코인이 바뀔 때는 수동으로 쉬는시간 줘야됨
    time.sleep(0.1)
    # tempDf가 None이 아닐 때만 처리
    if tempDf is not None:
        # 코인 이름 컬럼 추가
        tempDf['Coin'] = coin

        # 첫 번째 데이터프레임이면 바로 할당, 그렇지 않으면 합치기
        if df_minute.empty:
            df_minute = tempDf
        else:
            df_minute = pd.concat([df_minute, tempDf])
    else: print("api erorr: 데이터 없음")

# 시간 순으로 정렬
df_minute = df_minute.sort_index()

# 인덱스 리셋 후 'Coin' 컬럼을 두 번째 위치로 이동
df_minute = df_minute.reset_index()
cols = df_minute.columns.tolist()
# 'Coin' 컬럼을 추출하고 나머지 컬럼 순서를 조정
cols = cols[:1] + [cols[-1]] + cols[1:-1]
df_minute = df_minute[cols]

# 결과 출력
print(df_minute)

# 엑셀로 저장
df_minute.to_excel("2024-03-27.xlsx")