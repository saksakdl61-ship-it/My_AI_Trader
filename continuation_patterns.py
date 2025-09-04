import pandas as pd
import numpy as np

def is_valid_candle(candle):
    """
    캔들 데이터가 유효한지 검사합니다.
    """
    if candle is None or pd.isna(candle.high) or pd.isna(candle.low) or pd.isna(candle.open) or pd.isna(candle.close):
        return False
    return True

def three_white_soldiers(df_slice):
    """
    쓰리 화이트 솔저(Three White Soldiers) 패턴을 감지하고 유사도를 반환합니다.
    이 패턴은 상승 추세 지속을 나타냅니다.
    """
    if not isinstance(df_slice, pd.DataFrame) or len(df_slice) < 3:
        return 0
    
    c1 = df_slice.iloc[-3]
    c2 = df_slice.iloc[-2]
    c3 = df_slice.iloc[-1]
    
    if not is_valid_candle(c1) or not is_valid_candle(c2) or not is_valid_candle(c3):
        return 0
    
    is_bullish1 = c1.close > c1.open
    is_bullish2 = c2.close > c2.open
    is_bullish3 = c3.close > c3.open
    
    if is_bullish1 and is_bullish2 and is_bullish3:
        if c2.close > c1.close and c3.close > c2.close:
            # 시가 갭이 없는지 확인
            if c2.open > c1.close and c3.open > c2.close:
                return 100
            else:
                return 75 # 작은 갭이 있을 경우
    return 0

def three_black_crows(df_slice):
    """
    쓰리 블랙 크로우즈(Three Black Crows) 패턴을 감지하고 유사도를 반환합니다.
    이 패턴은 하락 추세 지속을 나타냅니다.
    """
    if not isinstance(df_slice, pd.DataFrame) or len(df_slice) < 3:
        return 0
    
    c1 = df_slice.iloc[-3]
    c2 = df_slice.iloc[-2]
    c3 = df_slice.iloc[-1]

    if not is_valid_candle(c1) or not is_valid_candle(c2) or not is_valid_candle(c3):
        return 0
    
    is_bearish1 = c1.close < c1.open
    is_bearish2 = c2.close < c2.open
    is_bearish3 = c3.close < c3.open
    
    if is_bearish1 and is_bearish2 and is_bearish3:
        if c2.close < c1.close and c3.close < c2.close:
            # 시가 갭이 없는지 확인
            if c2.open < c1.close and c3.open < c2.close:
                return 100
            else:
                return 75 # 작은 갭이 있을 경우
    return 0

def rising_three_methods(df_slice):
    """
    라이징 쓰리 메소드(Rising Three Methods) 패턴을 감지하고 유사도를 반환합니다.
    이 패턴은 상승 추세 지속을 나타냅니다.
    """
    if not isinstance(df_slice, pd.DataFrame) or len(df_slice) < 5:
        return 0

    c1 = df_slice.iloc[-5]
    c2 = df_slice.iloc[-4]
    c3 = df_slice.iloc[-3]
    c4 = df_slice.iloc[-2]
    c5 = df_slice.iloc[-1]

    if not all(is_valid_candle(c) for c in [c1, c2, c3, c4, c5]):
        return 0

    if c1.close > c1.open and c5.close > c5.open:
        if all(c.close < c.open for c in [c2, c3, c4]):
            if c2.close < c1.open and c4.open > c1.close:
                return 100
    return 0

def falling_three_methods(df_slice):
    """
    폴링 쓰리 메소드(Falling Three Methods) 패턴을 감지하고 유사도를 반환합니다.
    이 패턴은 하락 추세 지속을 나타냅니다.
    """
    if not isinstance(df_slice, pd.DataFrame) or len(df_slice) < 5:
        return 0

    c1 = df_slice.iloc[-5]
    c2 = df_slice.iloc[-4]
    c3 = df_slice.iloc[-3]
    c4 = df_slice.iloc[-2]
    c5 = df_slice.iloc[-1]
    
    if not all(is_valid_candle(c) for c in [c1, c2, c3, c4, c5]):
        return 0

    if c1.close < c1.open and c5.close < c5.open:
        if all(c.close > c.open for c in [c2, c3, c4]):
            if c2.close > c1.open and c4.open < c1.close:
                return 100
    return 0
