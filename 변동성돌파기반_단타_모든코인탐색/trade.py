import time
import pyupbit
import datetime

access = "ㅁ"
secret = "ㅁ"


def get_target_price(ticker, k):
    """변동성 돌파 전략으로 매수 목표가 조회"""
    """거래량 변화율 구하기"""
    # 1시간전 기록을 기준으로 타켓금액 설정
    df = pyupbit.get_ohlcv(ticker, interval="minute60", count=2)
    target_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * k
    if(df.iloc[0]['volume']==0):
        dv = 0
    else:
        dv = (df.iloc[1]['volume'] - df.iloc[0]['volume']) / df.iloc[0]['volume']
    return target_price, dv


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


def buy(coin):
    krw = get_balance("KRW")
    # 구입 최소비용보다 자금이 많은지
    if krw > 5000:
        print("buy")
        print(upbit.buy_market_order(coin, krw * (1 - fee)))
        print()
        return True
    else:
        print("구매 실패: 자금 부족")
        return False

def sell(coin):
    coin_held = get_balance(coin.split("-")[1])
    print(coin_held)
    if coin_held > 0.00008:
        print("sell")
        print(upbit.sell_market_order(coin, coin_held))
        print()
        return True
    else:
        return False

""" 변수 세팅 """
# 거래 수수료
fee = 0.0005
# 타겟 금액 설정 이전기록의 (고점-저점)*k 만큼의 상승이 일어나면 매수
k = 0.5

# 익절 계수: 0.02 -> 2프로 이익시 매도
plus_set = 0.02
# 손절 계수: 0.01 -> 1프로 손해시 매도
minus_set = 0.003
""" 변수 세팅 """

# 초기 상태 설정
is_buy = False
buy_coin = None
buy_price = 0
buy_time = None
coins = pyupbit.get_tickers(fiat="KRW")

# 로그인
upbit = pyupbit.Upbit(access, secret)

# 자동매매 시작
print("autotrade start")
while True:
    try:
        if not is_buy:
            max_volume_increase =0
            target_coin= None
            target_price=0
            # 모든 코인 반복물 돌면서 타켓가격을 넘긴 코인중 거래변화량이 가장 큰 코인을 선택
            for coin in coins:
                # 해당 시간 기준 한시간 전부터 지금까지의 고점,저점을 찾기 -> 돌파기준범위 계산(고점-저가) *k값
                # 거래량 증가율 계산 # 거래량 증가률 = (현재거래량-이전분의 거래량)/이전분의 거래량
                price, dv = get_target_price(coin, k)
                # 현재가격 가져오기
                current_price = get_current_price(coin)

                # 매수조건을 만족하는 코인중 거래 변화량이 가장 큰 코인 찾기
                if price < current_price:
                    if dv>max_volume_increase:
                        max_volume_increase = dv
                        target_coin = coin
                        target_price = price


            # 매수조건을 만족하는 코인이 있다면
            if target_coin:
                if(buy(target_coin)):
                    is_buy = True
                    buy_coin = target_coin
                    buy_price = target_price
                    buy_time = datetime.datetime.now()
                    print("현재 가격: ", get_current_price(buy_coin))
                    print("목표 매도가: ", buy_price * (1 + plus_set))
                    print("목표 손절가: ", buy_price*(1-minus_set))
                    print("구입 시간: ", datetime.datetime.now())
                    print("강제 판매 예정 시간: ", buy_time+datetime.timedelta(hours=1))

        else:
            current_price = get_current_price(buy_coin)
            current_time = datetime.datetime.now()
            # 매도 조건 확인
            # 현재 금액이 구입가의 102%이상이면 매도
            # 만약 buytime이후 한시간이 지났다면 매도
            # 1% 하락하면 매도

            if((current_price >= buy_price * (1+plus_set)) or (current_time >= buy_time + datetime.timedelta(hours=1)) or (current_price <= buy_price*(1-minus_set))):
                if( sell(buy_coin)):
                    is_buy = False
                    buy_coin = None


        time.sleep(1)
    except Exception as e:
        print(e)
        # 에러 발생시 수동으로 전량 판매를 해주어야 함
        is_buy = False
        buy_coin = None
        buy_price = 0
        buy_time = None
        time.sleep(1)