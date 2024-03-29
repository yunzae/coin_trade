import time
import pyupbit
import datetime



access = "asdsdLpJ"
secret = "asdsads"

def get_target_price(ticker, k):
    """변동성 돌파 전략으로 매수 목표가 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=2)
    target_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * k
    return target_price

def get_start_time(ticker):
    """시작 시간 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=1)
    start_time = df.index[0]
    return start_time

def get_balance(ticker):
    """잔고 조회"""
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == ticker:
            if b['balance'] is not None:
                return float(b['balance'])
            else:
                return 0
    return 0

def get_current_price(ticker):
    """현재가 조회"""
    return pyupbit.get_orderbook(ticker=ticker)["orderbook_units"][0]["ask_price"]

# 로그인
upbit = pyupbit.Upbit(access, secret)

#수수료
fee = 0.005

#거래 품목
COIN = "GLM"
COIN_KRW ="KRW-"+COIN
# 자동매매 시작
print("autotrade start")
while True:
    try:
        now = datetime.datetime.now()
        start_time = get_start_time(COIN_KRW) #9시
        end_time = start_time + datetime.timedelta(days=1)

        # 9:00 < 현재 < 8:59:50 인지
        if start_time < now < end_time - datetime.timedelta(seconds=10):
            target_price = get_target_price(COIN_KRW, 0.2)
            current_price = get_current_price(COIN_KRW)
            if target_price < current_price:
                krw = get_balance("KRW")
                # 구입 최소비용보다 자금이 많은지
                if krw > 5000:
                    upbit.buy_market_order(COIN_KRW, krw*(1-fee))
                    print("buy")
        #08:59:50 부터 전량 매도 시작
        else:
            coin_held = get_balance(COIN)
            if coin_held > 0.00008:
                upbit.sell_market_order(COIN_KRW, coin_held*(1-fee))
                print("sell")
        time.sleep(1)
    except Exception as e:
        print(e)
        time.sleep(1)