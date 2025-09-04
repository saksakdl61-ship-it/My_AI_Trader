import pandas as pd
import numpy as np

def is_valid_candle(candle):
    """
    캔들 데이터가 유효한지 검사합니다.
    """
    if candle is None or pd.isna(candle.high) or pd.isna(candle.low) or pd.isna(candle.open) or pd.isna(candle.close):
        return False
    return True

def doji_check(df_slice):
    """
    도지 캔들인지 확인하고 유사도를 반환합니다.
    """
    if not isinstance(df_slice, pd.DataFrame) or len(df_slice) < 1:
        return 0
    candle = df_slice.iloc[-1]
    if not is_valid_candle(candle):
        return 0

    body = abs(candle.close - candle.open)
    range_ = abs(candle.high - candle.low)

    if range_ == 0:
        return 100
    if body / range_ < 0.1:
        return 100 - (body / range_ * 100)
    return 0

def bullish_engulfing(df_slice):
    """
    불리시 엥걸핑(Bullish Engulfing) 패턴을 감지하고 유사도를 반환합니다.
    """
    if not isinstance(df_slice, pd.DataFrame) or len(df_slice) < 2:
        return 0
    
    prev_candle = df_slice.iloc[-2]
    curr_candle = df_slice.iloc[-1]
    
    if not is_valid_candle(prev_candle) or not is_valid_candle(curr_candle):
        return 0

    is_bullish = curr_candle.close > curr_candle.open
    is_bearish = prev_candle.close < prev_candle.open
    
    if is_bullish and is_bearish:
        if curr_candle.high > prev_candle.high and curr_candle.low < prev_candle.low:
            return 100
        elif curr_candle.high > prev_candle.high and curr_candle.low > prev_candle.low:
            return 80
    return 0

def bearish_engulfing(df_slice):
    """
    베어리시 엥걸핑(Bearish Engulfing) 패턴을 감지하고 유사도를 반환합니다.
    """
    if not isinstance(df_slice, pd.DataFrame) or len(df_slice) < 2:
        return 0
    
    prev_candle = df_slice.iloc[-2]
    curr_candle = df_slice.iloc[-1]
    
    if not is_valid_candle(prev_candle) or not is_valid_candle(curr_candle):
        return 0

    is_bullish = prev_candle.close > prev_candle.open
    is_bearish = curr_candle.close < curr_candle.open
    
    if is_bullish and is_bearish:
        if curr_candle.high > prev_candle.high and curr_candle.low < prev_candle.low:
            return 100
        elif curr_candle.high > prev_candle.high and curr_candle.low > prev_candle.low:
            return 80
    return 0

def piercing_line(df_slice):
    """
    피어싱 라인(Piercing Line) 패턴을 감지하고 유사도를 반환합니다.
    """
    if not isinstance(df_slice, pd.DataFrame) or len(df_slice) < 2:
        return 0
    
    prev_candle = df_slice.iloc[-2]
    curr_candle = df_slice.iloc[-1]
    
    if not is_valid_candle(prev_candle) or not is_valid_candle(curr_candle):
        return 0

    if prev_candle.close < prev_candle.open and curr_candle.close > curr_candle.open:
        mid_prev = (prev_candle.close + prev_candle.open) / 2
        if curr_candle.open < prev_candle.close and curr_candle.close > mid_prev:
            return 100
    return 0

def dark_cloud_cover(df_slice):
    """
    다크 클라우드 커버(Dark Cloud Cover) 패턴을 감지하고 유사도를 반환합니다.
    """
    if not isinstance(df_slice, pd.DataFrame) or len(df_slice) < 2:
        return 0
    
    prev_candle = df_slice.iloc[-2]
    curr_candle = df_slice.iloc[-1]
    
    if not is_valid_candle(prev_candle) or not is_valid_candle(curr_candle):
        return 0

    if prev_candle.close > prev_candle.open and curr_candle.close < curr_candle.open:
        mid_prev = (prev_candle.close + prev_candle.open) / 2
        if curr_candle.open > prev_candle.close and curr_candle.close < mid_prev:
            return 100
    return 0

def morning_star(df_slice):
    """
    모닝 스타(Morning Star) 패턴을 감지하고 유사도를 반환합니다.
    """
    if not isinstance(df_slice, pd.DataFrame) or len(df_slice) < 3:
        return 0
    
    candle1 = df_slice.iloc[-3]
    candle2 = df_slice.iloc[-2]
    candle3 = df_slice.iloc[-1]
    
    if not is_valid_candle(candle1) or not is_valid_candle(candle2) or not is_valid_candle(candle3):
        return 0

    is_bearish1 = candle1.close < candle1.open
    is_doji2 = doji_check(pd.DataFrame([candle2])) > 50
    is_bullish3 = candle3.close > candle3.open
    
    if is_bearish1 and is_doji2 and is_bullish3 and candle3.open > candle2.close and candle3.close > candle1.close:
        return 100
    return 0

def evening_star(df_slice):
    """
    이브닝 스타(Evening Star) 패턴을 감지하고 유사도를 반환합니다.
    """
    if not isinstance(df_slice, pd.DataFrame) or len(df_slice) < 3:
        return 0
    
    candle1 = df_slice.iloc[-3]
    candle2 = df_slice.iloc[-2]
    candle3 = df_slice.iloc[-1]
    
    if not is_valid_candle(candle1) or not is_valid_candle(candle2) or not is_valid_candle(candle3):
        return 0

    is_bullish1 = candle1.close > candle1.open
    is_doji2 = doji_check(pd.DataFrame([candle2])) > 50
    is_bearish3 = candle3.close < candle3.open
    
    if is_bullish1 and is_doji2 and is_bearish3 and candle3.open < candle2.close and candle3.close < candle1.close:
        return 100
    return 0

def three_white_soldiers(df_slice):
    """
    쓰리 화이트 솔저(Three White Soldiers) 패턴을 감지하고 유사도를 반환합니다.
    """
    if not isinstance(df_slice, pd.DataFrame) or len(df_slice) < 3:
        return 0
    
    candle1 = df_slice.iloc[-3]
    candle2 = df_slice.iloc[-2]
    candle3 = df_slice.iloc[-1]
    
    if not is_valid_candle(candle1) or not is_valid_candle(candle2) or not is_valid_candle(candle3):
        return 0
    
    if candle1.close > candle1.open and candle2.close > candle2.open and candle3.close > candle3.open:
        if candle2.open > candle1.open and candle2.close > candle1.close:
            if candle3.open > candle2.open and candle3.close > candle2.close:
                return 100
    return 0

def three_black_crows(df_slice):
    """
    쓰리 블랙 크로우즈(Three Black Crows) 패턴을 감지하고 유사도를 반환합니다.
    """
    if not isinstance(df_slice, pd.DataFrame) or len(df_slice) < 3:
        return 0
    
    candle1 = df_slice.iloc[-3]
    candle2 = df_slice.iloc[-2]
    candle3 = df_slice.iloc[-1]

    if not is_valid_candle(candle1) or not is_valid_candle(candle2) or not is_valid_candle(candle3):
        return 0
    
    if candle1.close < candle1.open and candle2.close < candle2.open and candle3.close < candle3.open:
        if candle2.open < candle1.open and candle2.close < candle1.close:
            if candle3.open < candle2.open and candle3.close < candle2.close:
                return 100
    return 0

def tweezer_bottom(df_slice):
    """
    트위저 바텀(Tweezer Bottom) 패턴을 감지하고 유사도를 반환합니다.
    """
    if not isinstance(df_slice, pd.DataFrame) or len(df_slice) < 2:
        return 0
    
    prev_candle = df_slice.iloc[-2]
    curr_candle = df_slice.iloc[-1]

    if not is_valid_candle(prev_candle) or not is_valid_candle(curr_candle):
        return 0

    if abs(prev_candle.low - curr_candle.low) < (prev_candle.close - prev_candle.open) * 0.1:
        return 100 - abs(prev_candle.low - curr_candle.low) * 10
    return 0

def tweezer_top(df_slice):
    """
    트위저 탑(Tweezer Top) 패턴을 감지하고 유사도를 반환합니다.
    """
    if not isinstance(df_slice, pd.DataFrame) or len(df_slice) < 2:
        return 0
    
    prev_candle = df_slice.iloc[-2]
    curr_candle = df_slice.iloc[-1]
    
    if not is_valid_candle(prev_candle) or not is_valid_candle(curr_candle):
        return 0

    if abs(prev_candle.high - curr_candle.high) < (prev_candle.close - prev_candle.open) * 0.1:
        return 100 - abs(prev_candle.high - curr_candle.high) * 10
    return 0

def golden_cross(df_slice):
    """
    골든 크로스(Golden Cross) 패턴을 감지하고 유사도를 반환합니다.
    """
    if not isinstance(df_slice, pd.DataFrame) or len(df_slice) < 50:
        return 0
    
    ma5 = df_slice['close'].rolling(window=5).mean()
    ma20 = df_slice['close'].rolling(window=20).mean()
    
    if ma5.iloc[-2] < ma20.iloc[-2] and ma5.iloc[-1] > ma20.iloc[-1]:
        return 100
    return 0

def death_cross(df_slice):
    """
    데스 크로스(Death Cross) 패턴을 감지하고 유사도를 반환합니다.
    """
    if not isinstance(df_slice, pd.DataFrame) or len(df_slice) < 50:
        return 0
    
    ma5 = df_slice['close'].rolling(window=5).mean()
    ma20 = df_slice['close'].rolling(window=20).mean()

    if ma5.iloc[-2] > ma20.iloc[-2] and ma5.iloc[-1] < ma20.iloc[-1]:
        return 100
    return 0

def bullish_harami(df_slice):
    """
    불리시 하라미(Bullish Harami) 패턴을 감지하고 유사도를 반환합니다.
    """
    if not isinstance(df_slice, pd.DataFrame) or len(df_slice) < 2:
        return 0
    
    prev_candle = df_slice.iloc[-2]
    curr_candle = df_slice.iloc[-1]

    if not is_valid_candle(prev_candle) or not is_valid_candle(curr_candle):
        return 0

    if prev_candle.close < prev_candle.open and curr_candle.close > curr_candle.open:
        if curr_candle.open > prev_candle.close and curr_candle.close < prev_candle.open:
            return 100
    return 0

def bearish_harami(df_slice):
    """
    베어리시 하라미(Bearish Harami) 패턴을 감지하고 유사도를 반환합니다.
    """
    if not isinstance(df_slice, pd.DataFrame) or len(df_slice) < 2:
        return 0
    
    prev_candle = df_slice.iloc[-2]
    curr_candle = df_slice.iloc[-1]

    if not is_valid_candle(prev_candle) or not is_valid_candle(curr_candle):
        return 0

    if prev_candle.close > prev_candle.open and curr_candle.close < curr_candle.open:
        if curr_candle.open < prev_candle.close and curr_candle.close > prev_candle.open:
            return 100
    return 0

def on_neck_line(df_slice):
    """
    온 넥 라인(On Neck Line) 패턴을 감지하고 유사도를 반환합니다.
    """
    if not isinstance(df_slice, pd.DataFrame) or len(df_slice) < 2:
        return 0
    
    prev_candle = df_slice.iloc[-2]
    curr_candle = df_slice.iloc[-1]

    if not is_valid_candle(prev_candle) or not is_valid_candle(curr_candle):
        return 0

    if prev_candle.close < prev_candle.open and curr_candle.close > curr_candle.open:
        if abs(prev_candle.close - curr_candle.close) / prev_candle.close < 0.001:
            return 100
    return 0

if __name__ == "__main__":
    # 이 부분은 테스트를 위한 예시 코드입니다.
    # 실제 백테스팅에서는 main.py에서 이 함수들을 호출합니다.
    
    data = {'open': [100, 110], 'high': [105, 115], 'low': [90, 100], 'close': [105, 110]}
    df_test = pd.DataFrame(data)

    print(f"Bullish Engulfing: {bullish_engulfing(df_test)}")
