import pandas as pd
import numpy as np

def is_valid_candle(candle):
    """
    캔들 데이터가 유효한지 검사합니다.
    """
    if candle is None or pd.isna(candle.high) or pd.isna(candle.low) or pd.isna(candle.open) or pd.isna(candle.close):
        return False
    return True

def doji(df_slice):
    """
    도지 패턴을 감지하고 유사도를 반환합니다.
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

def hammer(df_slice):
    """
    해머 패턴을 감지하고 유사도를 반환합니다.
    """
    if not isinstance(df_slice, pd.DataFrame) or len(df_slice) < 1:
        return 0
    candle = df_slice.iloc[-1]
    if not is_valid_candle(candle):
        return 0

    is_bearish_trend = (df_slice['close'].iloc[-4:-1].mean() > df_slice['close'].iloc[-1])
    is_long_lower_shadow = (candle.low < candle.open) and (candle.low < candle.close)
    body_size = abs(candle.open - candle.close)
    lower_shadow = min(candle.open, candle.close) - candle.low
    upper_shadow = candle.high - max(candle.open, candle.close)

    if is_bearish_trend and is_long_lower_shadow and (lower_shadow > 2 * body_size) and (upper_shadow < body_size):
        similarity = min(100, (lower_shadow / (2 * body_size)) * 50)
        return similarity
    return 0

def spinning_top(df_slice):
    """
    스피닝 탑 패턴을 감지하고 유사도를 반환합니다.
    """
    if not isinstance(df_slice, pd.DataFrame) or len(df_slice) < 1:
        return 0
    candle = df_slice.iloc[-1]
    if not is_valid_candle(candle):
        return 0

    body = abs(candle.close - candle.open)
    range_ = abs(candle.high - candle.low)
    
    if range_ == 0:
        return 0

    if body / range_ > 0.1 and body / range_ < 0.5:
        return 100 - abs(0.3 - body / range_) * 100
    return 0

def marubozu(df_slice):
    """
    마루보즈 패턴을 감지하고 유사도를 반환합니다.
    """
    if not isinstance(df_slice, pd.DataFrame) or len(df_slice) < 1:
        return 0
    candle = df_slice.iloc[-1]
    if not is_valid_candle(candle):
        return 0

    body = abs(candle.close - candle.open)
    range_ = abs(candle.high - candle.low)
    
    if range_ == 0:
        return 0

    if body / range_ > 0.95:
        return 100 - (1 - body / range_) * 100
    return 0

def shooting_star(df_slice):
    """
    슈팅 스타 패턴을 감지하고 유사도를 반환합니다.
    """
    if not isinstance(df_slice, pd.DataFrame) or len(df_slice) < 1:
        return 0
    candle = df_slice.iloc[-1]
    if not is_valid_candle(candle):
        return 0

    is_bullish_trend = (df_slice['close'].iloc[-4:-1].mean() < df_slice['close'].iloc[-1])
    is_long_upper_shadow = (candle.high > candle.open) and (candle.high > candle.close)
    body_size = abs(candle.open - candle.close)
    lower_shadow = min(candle.open, candle.close) - candle.low
    upper_shadow = candle.high - max(candle.open, candle.close)

    if is_bullish_trend and is_long_upper_shadow and (upper_shadow > 2 * body_size) and (lower_shadow < body_size):
        similarity = min(100, (upper_shadow / (2 * body_size)) * 50)
        return similarity
    return 0

def inverted_hammer(df_slice):
    """
    역망치형 패턴을 감지하고 유사도를 반환합니다.
    """
    if not isinstance(df_slice, pd.DataFrame) or len(df_slice) < 1:
        return 0
    candle = df_slice.iloc[-1]
    if not is_valid_candle(candle):
        return 0

    is_bearish_trend = (df_slice['close'].iloc[-4:-1].mean() > df_slice['close'].iloc[-1])
    is_long_upper_shadow = (candle.high > candle.open) and (candle.high > candle.close)
    body_size = abs(candle.open - candle.close)
    lower_shadow = min(candle.open, candle.close) - candle.low
    upper_shadow = candle.high - max(candle.open, candle.close)
    
    if is_bearish_trend and is_long_upper_shadow and (upper_shadow > 2 * body_size) and (lower_shadow < body_size):
        similarity = min(100, (upper_shadow / (2 * body_size)) * 50)
        return similarity
    return 0

def gravestone_doji(df_slice):
    """
    비석형 도지 패턴을 감지하고 유사도를 반환합니다.
    """
    if not isinstance(df_slice, pd.DataFrame) or len(df_slice) < 1:
        return 0
    candle = df_slice.iloc[-1]
    if not is_valid_candle(candle):
        return 0

    body = abs(candle.close - candle.open)
    if body != 0 and (candle.high - max(candle.open, candle.close)) / body < 2:
        return 0
    
    if abs(candle.high - max(candle.open, candle.close)) > abs(min(candle.open, candle.close) - candle.low) * 2:
        return 100 - (abs(candle.close - candle.open) / (candle.high - candle.low)) * 100
    return 0

def dragonfly_doji(df_slice):
    """
    잠자리형 도지 패턴을 감지하고 유사도를 반환합니다.
    """
    if not isinstance(df_slice, pd.DataFrame) or len(df_slice) < 1:
        return 0
    candle = df_slice.iloc[-1]
    if not is_valid_candle(candle):
        return 0

    body = abs(candle.close - candle.open)
    if body != 0 and (min(candle.open, candle.close) - candle.low) / body < 2:
        return 0
    
    if abs(min(candle.open, candle.close) - candle.low) > abs(candle.high - max(candle.open, candle.close)) * 2:
        return 100 - (abs(candle.close - candle.open) / (candle.high - candle.low)) * 100
    return 0

def long_legged_doji(df_slice):
    """
    긴 다리형 도지 패턴을 감지하고 유사도를 반환합니다.
    """
    if not isinstance(df_slice, pd.DataFrame) or len(df_slice) < 1:
        return 0
    candle = df_slice.iloc[-1]
    if not is_valid_candle(candle):
        return 0

    body = abs(candle.close - candle.open)
    range_ = abs(candle.high - candle.low)
    
    if range_ == 0:
        return 0
    
    if (candle.high - max(candle.open, candle.close)) / range_ > 0.4 and (min(candle.open, candle.close) - candle.low) / range_ > 0.4:
        return 100 - (body / range_) * 100
    return 0

def paper_umbrella(df_slice):
    """
    페이퍼 우산형 패턴을 감지하고 유사도를 반환합니다.
    """
    if not isinstance(df_slice, pd.DataFrame) or len(df_slice) < 1:
        return 0
    candle = df_slice.iloc[-1]
    if not is_valid_candle(candle):
        return 0

    body_size = abs(candle.open - candle.close)
    lower_shadow = min(candle.open, candle.close) - candle.low
    upper_shadow = candle.high - max(candle.open, candle.close)

    if (lower_shadow > 2 * body_size) and (upper_shadow < body_size):
        return 100 - (upper_shadow / body_size) * 10
    return 0

def hanging_man(df_slice):
    """
    행잉맨 패턴을 감지하고 유사도를 반환합니다.
    """
    if not isinstance(df_slice, pd.DataFrame) or len(df_slice) < 1:
        return 0
    candle = df_slice.iloc[-1]
    if not is_valid_candle(candle):
        return 0
    
    is_bullish_trend = (df_slice['close'].iloc[-4:-1].mean() < df_slice['close'].iloc[-1])
    is_paper_umbrella = paper_umbrella(df_slice)
    
    if is_bullish_trend and is_paper_umbrella:
        return is_paper_umbrella
    return 0

def green_hammer(df_slice):
    """
    상승 망치형 패턴을 감지하고 유사도를 반환합니다.
    """
    if not isinstance(df_slice, pd.DataFrame) or len(df_slice) < 1:
        return 0
    candle = df_slice.iloc[-1]
    if not is_valid_candle(candle):
        return 0
    
    is_bearish_trend = (df_slice['close'].iloc[-4:-1].mean() > df_slice['close'].iloc[-1])
    is_hammer = hammer(df_slice)
    
    if is_bearish_trend and is_hammer > 0 and candle.close > candle.open:
        return is_hammer
    return 0

def red_hammer(df_slice):
    """
    하락 망치형 패턴을 감지하고 유사도를 반환합니다.
    """
    if not isinstance(df_slice, pd.DataFrame) or len(df_slice) < 1:
        return 0
    candle = df_slice.iloc[-1]
    if not is_valid_candle(candle):
        return 0
    
    is_bearish_trend = (df_slice['close'].iloc[-4:-1].mean() > df_slice['close'].iloc[-1])
    is_hammer = hammer(df_slice)
    
    if is_bearish_trend and is_hammer > 0 and candle.close < candle.open:
        return is_hammer
    return 0

if __name__ == "__main__":
    # 이 부분은 테스트를 위한 예시 코드입니다.
    # 실제 백테스팅에서는 main.py에서 이 함수들을 호출합니다.
    
    # 예시 데이터 생성
    data = {'date': pd.to_datetime(['2023-01-01', '2023-01-02', '2023-01-03', '2023-01-04', '2023-01-05']),
            'open': [100, 95, 90, 85, 80],
            'high': [105, 100, 95, 90, 85],
            'low': [90, 85, 80, 75, 70],
            'close': [95, 90, 85, 80, 85]}
    df_test = pd.DataFrame(data)
    
    # 해머 패턴 감지 테스트
    test_hammer_df = df_test.copy()
    test_hammer_df.loc[4, 'open'] = 85
    test_hammer_df.loc[4, 'high'] = 90
    test_hammer_df.loc[4, 'low'] = 75
    test_hammer_df.loc[4, 'close'] = 82
    
    hammer_similarity = hammer(test_hammer_df)
    print(f"Hammer similarity: {hammer_similarity}")
