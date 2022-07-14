from pybit import usdt_perpetual
import datetime
import time
import pandas as pd
import numpy as np



# 로그인
# -------------------------------------------------
api_key = ""
api_secret = ""

session = usdt_perpetual.HTTP(
    endpoint="https://api.bybit.com", 
    api_key=api_key, 
    api_secret=api_secret
)

ws = usdt_perpetual.WebSocket(
    test=False,
    api_key=api_key,
    api_secret=api_secret
)

print("BTC Derivatives Trading\n")
# -------------------------------------------------


btc = "BTCUSDT"


# 비트코인 5분봉 ohlcv
# -------------------------------------------------------------------------------------------
def get_minute_bar(sym):

    t = (datetime.datetime.now() - datetime.timedelta(hours=9)).strftime('%Y-%m-%d %H:%M:%S')
    from_time = time.mktime(datetime.datetime.strptime(t, '%Y-%m-%d %H:%M:%S').timetuple())

    resp = session.query_kline(
        symbol=sym,
        interval=5,
        limit=400,
        from_time=int(from_time)
    )

    result = resp['result']
    df = pd.DataFrame(result)
    ts = pd.to_datetime(df['open_time'], unit='s') + datetime.timedelta(hours=9)
    df.set_index(ts, inplace=True)
    df = df[['open', 'high', 'low', 'close']]

    return df
# -------------------------------------------------------------------------------------------

# 비트코인 현재가
# ------------------------------------------------
def get_current_price(sym):

    price = get_minute_bar(sym)['close'][-1]

    return price
# ------------------------------------------------

# RSI
# -----------------------------------------------------------------
def RSI(sym):

    df = get_minute_bar(sym)

    df['변화량'] = df['close'] - df['close'].shift(1)
    df['상승폭'] = np.where(df['변화량'] >= 0, df['변화량'], 0)
    df['하락폭'] = np.where(df['변화량'] < 0, df['변화량'].abs(), 0)

    df['AU'] = df['상승폭'].ewm(alpha=1/7, min_periods=7).mean()
    df['AD'] = df['하락폭'].ewm(alpha=1/7, min_periods=7).mean()

    df['RSI'] = df['AU'] / (df['AU'] + df['AD']) * 100

    now_rsi = round(df['RSI'][-1], 4)
    before_rsi = round(df['RSI'][-2], 4)

    rsi = [now_rsi, before_rsi]

    return rsi
# ------------------------------------------------------------------

# 포지션 정보
# -------------------------------------------------------
def long_position():

    long_info = session.my_position(symbol=btc)['result'][0]

    return long_info

def short_position():

    short_info = session.my_position(symbol=btc)['result'][1]

    return short_info



'''
'result': [{'auto_add_margin': 0,
             'bust_price': 26589.5,
             'cum_realised_pnl': -722.98318742,
             'deleverage_indicator': 2,
             'entry_price': 29829,
             'free_qty': -0.001,
             'is_isolated': True,
             'leverage': 10,
             'liq_price': 26739,
             'mode': 'BothSide',
             'occ_closing_fee': 0.0159537,
             'position_idx': 1,
             'position_margin': 3.23955396,
             'position_value': 29.829,
             'realised_pnl': -0.0029829,
             'risk_id': 1,
             'side': 'Buy',
             'size': 0.001,
             'stop_loss': 0,
             'symbol': 'BTCUSDT',
             'take_profit': 0,
             'tp_sl_mode': 'Full',
             'trailing_stop': 0,
             'unrealised_pnl': 0.12105,
             'user_id': 2510271},
            {'auto_add_margin': 0,
             'bust_price': 0,
             'cum_realised_pnl': -278.18714945,
             'deleverage_indicator': 0,
             'entry_price': 0,
             'free_qty': 0,
             'is_isolated': True,
             'leverage': 10,
             'liq_price': 0,
             'mode': 'BothSide',
             'occ_closing_fee': 0,
             'position_idx': 2,
             'position_margin': 0,
             'position_value': 0,
             'realised_pnl': 0,
             'risk_id': 1,
             'side': 'Sell',
             'size': 0,
             'stop_loss': 0,
             'symbol': 'BTCUSDT',
             'take_profit': 0,
             'tp_sl_mode': 'Full',
             'trailing_stop': 0,
             'unrealised_pnl': 0,
             'user_id': 2510271}],
'''
# ---------------------------------------------

# 잔고 조회
# -------------------------------------------------------------------
def balances():
    
    balances = balances = session.get_wallet_balance(coin="USDT")['result']['USDT']

    return balances
'''
'available_balance': 76.52219056,     매매 가능 금액
'cum_realised_pnl': -1073.61788504,   전체 실현 손익
'equity': 79.88290822,                전체 계좌 금액
'given_cash': 0,
'occ_closing_fee': 0.0159537,         포지션 종료시 수수료
'occ_funding_fee': 0,
'order_margin': 0,
'position_margin': 3.25550766,        진입 포지션 금액
'realised_pnl': -0.0029829,           당일 실현 손익
'service_cash': 0,
'unrealised_pnl': 0.10521,            미실현 손익
'used_margin': 3.25550766,            사용된 마진
'wallet_balance': 79.77769822}}       전체 계좌 잔고
'''
# -------------------------------------------------------------------

# 주문
# ---------------------------------------------------------
def open_long(qty, price):
    session.place_active_order(
            symbol = "BTCUSDT", 
            side = "Buy",
            order_type = "Limit",  
            qty = qty, 
            price = price+100,
            time_in_force = "GoodTillCancel",
            reduce_only = False,
            close_on_trigger = False
            )

def close_long(qty, price):
    session.place_active_order(
            symbol = "BTCUSDT", 
            side = "Sell",
            order_type = "Limit",  
            qty = qty, 
            price = price-100,
            time_in_force = "GoodTillCancel",
            reduce_only = True,
            close_on_trigger = False
            )

def open_short(qty, price):
    session.place_active_order(
            symbol = "BTCUSDT", 
            side = "Sell",
            order_type = "Limit",  
            qty = qty, 
            price = price-100,
            time_in_force = "GoodTillCancel",
            reduce_only = False,
            close_on_trigger = False
            )
    
def close_short(qty, price):
    session.place_active_order(
            symbol = "BTCUSDT", 
            side = "Buy",
            order_type = "Limit",  
            qty = qty, 
            price = price+100,
            time_in_force = "GoodTillCancel",
            reduce_only = True,
            close_on_trigger = False
            )
# ---------------------------------------------------------

# Stop Loss 주문
# ---------------------------------------
class stop_loss(object):

    def __init__(self,a):

        self.price = a

    def stop_loss_long(self):

        session.set_trading_stop(
            symbol = btc,
            side = "Buy",
            stop_loss = self.price
        )

    def stop_loss_short(self):

        session.set_trading_stop(
            symbol = btc,
            side = "Short",
            stop_loss = self.price
        )
# ---------------------------------------

# 정보 저장
# 초기 USDT 잔고 - 기준 매수 시간 - 축적 매수량 - 평균 매수가 - 카운팅
# ----------------------------------------------------------------
class save(object):

    def __init__(self,a,b,c,d,e):
        self.a = a
        self.b = b
        self.c = c
        self.d = d
        self.e = e

    def save_first_usdt(self):
        f = open("usdt_balance.txt", "w")
        f.write(str(self.a))
        f.close()
    
    def save_after_time(self):
        f = open("trade_time.txt", "w")
        f.write(str(self.b))
        f.close()
    
    def save_accumulated_volume(self):
        f = open("save_accumulated_volume.txt", "w")
        f.write(str(self.c))
        f.close()

    def save_avg_price(self):
        f = open("save_avg_price.txt", "w")
        f.write(str(self.d))
        f.close()

    def save_counting(self):
        f = open("save_counting.txt", "w")
        f.write(str(self.e))
        f.close()
# ----------------------------------------------------------------

# 정보 읽기
# 초기 원화 잔고 - 기준 매수 시간 - 축적 매수량 - 평균 매수가 - 카운팅
# --------------------------------------------------------------------
class read(object):

    def __init__(self):
        self.a = 0

    def read_first_usdt(self):
        f = open("usdt_balance.txt", "r")
        first_krw_balance = float(f.readline())
        f.close()
        return first_krw_balance

    def read_after_time(self):
        f = open("trade_time.txt", "r")
        line = f.readline()
        ttime = datetime.datetime.strptime(line, "%Y-%m-%d %H:%M:%S")
        f.close()
        return ttime
    
    def read_accumulated_volume(self):
        f = open("save_accumulated_volume.txt", "r")
        accumulated_volume = float(f.readline())
        f.close()
        return accumulated_volume

    def read_avg_price(self):
        f = open("save_avg_price.txt", "r")
        avg_buy_price = float(f.readline())
        f.close()
        return avg_buy_price
    
    def read_counting(self):
        f = open("save_counting.txt", "r")
        counting = float(f.readline())
        f.close()
        return counting
# --------------------------------------------------------------------

r = read()
rsi_up = 70
rsi_down = 30
leverage = 10
stop_loss_percent = 10



    
while True:

    try:

    
        now_rsi = RSI(btc)[0]
        before_rsi = RSI(btc)[1]
        
        # 첫 매수
        # 아무 포지션이 없는 경우 매수 준비
        if balances()['position_margin'] == 0:

            # 롱 포지션을 잡는 경우
            if before_rsi < rsi_down and before_rsi < now_rsi:

                # 최초 USDT 잔고 저장
                fir_usdt = balances()['equity']
                s = save(fir_usdt,0,0,0,0)
                s.save_first_usdt()

                qty = round(fir_usdt / 20 * leverage / get_current_price(btc), 3)
                
                # 롱 포지션 주문
                open_long(qty, get_current_price(btc))

                # 매수 한 시간
                t = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                # 매수 한 다음 5분봉 기준 시간
                after_time = get_minute_bar(btc).iloc[[-1]].index[0] + datetime.timedelta(minutes=5)

                # 평균 매수가
                ap = long_position()['entry_price']

                # 누적 매수량
                accumulated_volume = balances()['position_margin']

                # 정보 저장
                s = save(0,after_time,accumulated_volume,ap,1)
                s.save_after_time()
                s.save_accumulated_volume()
                s.save_avg_price()
                s.save_counting()

            
            # 숏 포지션을 잡는 경우
            if before_rsi > rsi_up and before_rsi > now_rsi:

                # 최초 USDT 잔고 저장
                fir_usdt = balances()['equity']
                s = save(fir_usdt,0,0,0,0)
                s.save_first_usdt()

                qty = round(fir_usdt / 20 * leverage / get_current_price(btc), 3)
                
                # 숏 포지션 주문
                open_short(qty, get_current_price(btc))

                # 매수 한 시간
                t = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                # 매수 한 다음 5분봉 기준 시간
                after_time = get_minute_bar(btc).iloc[[-1]].index[0] + datetime.timedelta(minutes=5)

                # 평균 매수가
                ap = short_position()['entry_price']

                # 누적 매수량
                accumulated_volume = balances()['position_margin']

                # 정보 저장
                s = save(0,after_time,accumulated_volume,ap,1)
                s.save_after_time()
                s.save_accumulated_volume()
                s.save_avg_price()
                s.save_counting()


        # 현 상태 표시
        if balances()['position_margin'] == 0:

            print("매매 대기중")
            print(get_current_price(btc))

        else:

            # 포지션 진입 후 다음 5분봉부터 재매수 시작

            print("----------포지션 진입중----------")

            first_usdt_balance = r.read_first_usdt()
            qty = round(first_usdt_balance/20*leverage/get_current_price(btc), 3)
            after_time = r.read_after_time()
            accumulated_volume = r.read_accumulated_volume()
            avg_buy_price = r.read_avg_price()
            counting = r.read_counting()
            
            if long_position()['position_margin'] > 0 :

                now_earning_rate = (get_current_price(btc) - avg_buy_price) / avg_buy_price * leverage * 100

            if short_position()['position_margin'] > 0:

                now_earning_rate = -(get_current_price(btc) - avg_buy_price) / avg_buy_price * leverage * 100


            
            earnings = round(accumulated_volume * now_earning_rate / 100, 2)
            
            print("현재 수익률:", round(now_earning_rate,2), "%")
            print("현재 수익금:", earnings, "$")
            print("현재가 :", get_current_price(btc), "$")

            if after_time < datetime.datetime.now():

                loss = -10

                # 롱 포지션을 잡았을 경우 추가 매수
                if long_position()['position_margin'] > 0 and now_earning_rate < loss and before_rsi < rsi_down and before_rsi < now_rsi:

                    # 첫번째 추가 매수
                    if counting == 1:
                        
                        # 롱 포지션 주문
                        open_long(qty, get_current_price(btc))

                        # 매수 한 시간
                        t = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                        # 매수 한 다음 5분봉 기준 시간
                        after_time = get_minute_bar(btc).iloc[[-1]].index[0] + datetime.timedelta(minutes=5)

                        # 평균 매수가
                        ap = long_position()['entry_price']

                        # 누적 매수량
                        accumulated_volume = balances()['position_margin']

                        # 정보 저장
                        s = save(0,after_time,accumulated_volume,ap,counting+1)
                        s.save_after_time()
                        s.save_accumulated_volume()
                        s.save_avg_price()
                        s.save_counting()

                    # 매수 3번째 이상
                    if counting > 1:

                        if balances()['available_balance'] > qty*(2**(counting-1)):

                            # 롱 포지션 주문
                            open_long(qty*(2**(counting-1)), get_current_price(btc))

                            # 매수 한 시간
                            t = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                            # 매수 한 다음 5분봉 기준 시간
                            after_time = get_minute_bar(btc).iloc[[-1]].index[0] + datetime.timedelta(minutes=5)

                            # 평균 매수가
                            ap = long_position()['entry_price']

                            # 누적 매수량
                            accumulated_volume = balances()['position_margin']

                            # 정보 저장
                            s = save(0,after_time,accumulated_volume,ap,counting+1)
                            s.save_after_time()
                            s.save_accumulated_volume()
                            s.save_avg_price()
                            s.save_counting()
                        
                        # 물 탈 금액 부족할 때 최종 매수
                        else:

                            fb = balances()['available_balance']

                            qty = round(fb * leverage *0.97 / get_current_price(btc), 3)

                            # 롱 포지션 주문
                            open_long(fb, get_current_price(btc))

                            # 매수 한 시간
                            t = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                            # 매수 한 다음 5분봉 기준 시간
                            after_time = get_minute_bar(btc).iloc[[-1]].index[0] + datetime.timedelta(minutes=5)

                            # 평균 매수가
                            ap = long_position()['entry_price']

                            # 누적 매수량
                            accumulated_volume = balances()['position_margin']

                            # 정보 저장
                            s = save(0,after_time,accumulated_volume,ap,counting+1)
                            s.save_after_time()
                            s.save_accumulated_volume()
                            s.save_avg_price()
                            s.save_counting()


                
                # 숏 포지션을 잡았을 경우 추가 매수
                if short_position()['position_margin'] > 0 and now_earning_rate < loss and before_rsi > rsi_up and before_rsi > now_rsi:
                    
                    
                    # 첫번째 추가 매수
                    if counting == 1:
                        
                        # 숏 포지션 주문
                        open_short(qty, get_current_price(btc))

                        # 매수 한 시간
                        t = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                        # 매수 한 다음 5분봉 기준 시간
                        after_time = get_minute_bar(btc).iloc[[-1]].index[0] + datetime.timedelta(minutes=5)

                        # 평균 매수가
                        ap = short_position()['entry_price']

                        # 누적 매수량
                        accumulated_volume = balances()['position_margin']

                        # 정보 저장
                        s = save(0,after_time,accumulated_volume,ap,counting+1)
                        s.save_after_time()
                        s.save_accumulated_volume()
                        s.save_avg_price()
                        s.save_counting()

                    # 매수 3번째 이상
                    if counting > 1:

                        if balances()['available_balance'] > qty*(2**(counting-1)):

                            # 숏 포지션 주문
                            open_short(qty*(2**(counting-1)), get_current_price(btc))

                            # 매수 한 시간
                            t = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                            # 매수 한 다음 5분봉 기준 시간
                            after_time = get_minute_bar(btc).iloc[[-1]].index[0] + datetime.timedelta(minutes=5)

                            # 평균 매수가
                            ap = short_position()['entry_price']

                            # 누적 매수량
                            accumulated_volume = balances()['position_margin']

                            # 정보 저장
                            s = save(0,after_time,accumulated_volume,ap,counting+1)
                            s.save_after_time()
                            s.save_accumulated_volume()
                            s.save_avg_price()
                            s.save_counting()
                        
                        # 물 탈 금액 부족할 때 최종 매수
                        else:

                            fb = balances()['available_balance']

                            qty = round(fb * leverage *0.97 / get_current_price(btc), 3)

                            # 숏 포지션 주문
                            open_short(fb, get_current_price(btc))

                            # 매수 한 시간
                            t = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                            # 매수 한 다음 5분봉 기준 시간
                            after_time = get_minute_bar(btc).iloc[[-1]].index[0] + datetime.timedelta(minutes=5)

                            # 평균 매수가
                            ap = short_position()['entry_price']

                            # 누적 매수량
                            accumulated_volume = balances()['position_margin']

                            # 정보 저장
                            s = save(0,after_time,accumulated_volume,ap,counting+1)
                            s.save_after_time()
                            s.save_accumulated_volume()
                            s.save_avg_price()
                            s.save_counting()



            else:
                print("아직 다음봉 갱신 안 됨")

            
            # 롱 포지션 보유중 - RSI 꺾인 지점 70 이상이면 전량 매도
            if long_position()['position_margin'] > 0 and before_rsi > rsi_up and before_rsi > now_rsi and now_earning_rate > 2:

                qty = abs(long_position()['free_qty'])

                close_long(qty, get_current_price(btc))


            # 숏 포지션 보유중 - RSI 꺾인 지점 30 이하면 전량 매도
            if short_position()['position_margin'] > 0 and before_rsi < rsi_down and before_rsi < now_rsi and now_earning_rate > 2:

                qty = abs(short_position()['free_qty'])

                close_short(qty, get_current_price(btc))


            # # 추가 매수 금액 부족 - Stop Loss 주문
            # if balances()['available_balance'] < 3:
                
            #     if long_position()['position_margin'] > 0 and long_position()['stop_loss'] == 0:

            #         avg_price = long_position()['entry_price']

            #         sl_price = avg_price - avg_price * stop_loss_percent / 100 / leverage

            #         session.set_trading_stop(
            #             symbol=btc,
            #             side="Buy",
            #             stop_loss=sl_price
            #         )
                
            #     if short_position()['position_margin'] > 0 and short_position()['stop_loss'] == 0:

            #         avg_price = short_position()['entry_price']
            #         print(avg_price)

            #         sl_price = avg_price + avg_price * stop_loss_percent / 100 / leverage
            #         print(sl_price)
            #         session.set_trading_stop(
            #             symbol=btc,
            #             side="Sell",
            #             stop_loss=sl_price
            #         )

        time.sleep(1.2)

    except Exception as e:
        print(e)

    time.sleep(0.2)
