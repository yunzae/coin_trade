# 1. 모든 코인을 검색한다.(o)
# 2. 각 코인의 이전 한시간을 기준으로 k를 구한다.(보류)
# 3. 어떤 코인을 매수할지 결정한다. 거래량이 많은 것으로 구매한다.
# 4. 만약 돌파점을 통과한다면 매수 -> 2% 이익시 매도
# 5. 만약 -1%가 된다면 바로 매도
# 6. 만약 +2%와 -1% 사이에서 5분동안 머문다면 매도후 1로 이동

## 상승장이라면 K 낮게, 하락장은 높게, 배치프로그램 돌려? 또는 수익률이 일정 시간 이상 상승장이면 K를 조금씩 낮춰, 하락이면 k 높여
import pandas as pd


""" 변수 세팅 """
# 테스트 날짜 양식: 2024-02-01 , 날짜.xlsx 파일이 있어야함
test_date = "2024-03-14"
# 거래 수수료
fee = 0.003
# 타겟 금액 설정 이전기록의 (고점-저점)*k 만큼의 상승이 일어나면 매수
k = 0.6
# 타켓 범위 설정 시간 설정 : 1 -> 현재시각과 1시간전 사이의 고점과 저점을 기준으로 계산 , 2면 2시간전
hour_set = 1
# 익절 계수: 0.02 -> 2프로 이익시 매도
plus_set = 0.02
# 손절 계수: 0.01 -> 1프로 손해시 매도
minus_set = 0.001
""" 세팅 """

def calculate_target_range(data, current_time, coin, k, hour_set):
    """
    주어진 시간 범위에 대해 고점과 저점을 찾아 k를 곱한 값을 반환합니다.
    :param data: 데이터프레임
    :param current_time: 현재 시간 인덱스
    :param k: 변동성 돌파 계수
    :return: 돌파 기준 범위
    """
    one_hour_ago = current_time - pd.Timedelta(hours=hour_set)
    filtered_data = data[(data['index'] >= one_hour_ago) & (data['index'] <= current_time) & (data['Coin'] == coin)]
    high_price = filtered_data['high'].max()
    low_price = filtered_data['low'].min()
    return (high_price - low_price) * k



# 초기 상태 설정
is_buy = False
buy_coin = None
buy_price = 0
buy_time = None

# 결과를 저장할 데이터프레임
result = []
# 시간순 분봉 데이터 가져오기
df = pd.read_excel(test_date+".xlsx")


# 시간별 데이터 순회
for current_time, group in df.groupby('index'):
    ## 그룹의 코인수가 50개 이하면 넘어가도록 변형해도 될듯
    if not is_buy:
        max_volume_increase = 0
        target_coin = None
        target_price = 0

        for _, row in group.iterrows():
            # 고점과 저점 차이 계산
            # 해당 시간 기준 한시간 전부터 지금까지의 고점,저점을 찾기 -> 돌파기준범위 계산(고점-저가) *k값
            target_range = calculate_target_range(df, current_time, row['Coin'], k, hour_set)

            # 만약 지금 시간에 거래 조건 충족되면 장바구니에 (코인명, 거래량증가률)넣기
            if row['close'] > row['open'] + target_range:
                # 거래량 증가율 계산 # 거래량 증가률 = (현재거래량-이전분의 거래량)/이전분의 거래량
                volume_increase = (row['volume'] - group['volume'].shift(1).loc[row.name]) / group['volume'].shift(1).loc[row.name]

                # 장바구니에서 거래증가률이 제일 많은 코인 구매
                if volume_increase > max_volume_increase:
                    max_volume_increase = volume_increase
                    target_coin = row['Coin']
                    target_price = row['open']
                    buy_time = current_time
        # 매수조건을 만족하는 코인이 있다면
        if target_coin:
            is_buy = True
            buy_coin = target_coin
            buy_price = target_price
            result.append({'time': current_time, 'action': 'buy', 'coin': buy_coin, 'ror(수익률)': 1})

        # 장바구니에 아무것도 없다면
        else:
            result.append({'time': current_time, 'action': 'money_hold', 'coin': None, 'ror(수익률)': 1})
    else:
        # 매도 조건 확인
        # 현재 금액이 구입가의 102%이상이면 매도
        # 만약 buytime이후 5분이 지났다면 매도
        # 1% 하락하면 매도
        try:
            row = group[group['Coin'] == buy_coin].iloc[0]
            if row['open'] >= buy_price * (1+plus_set) or current_time >= buy_time + pd.Timedelta(minutes=5) or row[
                'open'] <= buy_price * (1-minus_set):
                is_buy = False
                result.append({'time': current_time, 'action': 'sell', 'coin': buy_coin,
                               'ror(수익률)': 1 + (row['open'] - buy_price) / buy_price - fee})
                buy_coin = None
            else:
                result.append({'time': current_time, 'action': 'coin_hold', 'coin': buy_coin,
                               'ror(수익률)': 1 })
        except:
            print("해당 시간에 코인 정보가 없습니다.")

# 결과 데이터프레임 생성 및 엑셀로 저장
result_df = pd.DataFrame(result)


# # 누적 곱 계산(cumprod) => 누적 수익률
result_df['hpr(누적수익률)'] = result_df['ror(수익률)'].cumprod()

file_name = f"{test_date}_backtest_result_k={k}_hour_set={hour_set}_plus_set={plus_set}_minus_set={minus_set}.xlsx"
result_df.to_excel(file_name)
