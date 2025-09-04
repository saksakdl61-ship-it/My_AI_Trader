import pandas as pd
import numpy as np

def is_valid_data(df_slice):
    """
    데이터프레임의 유효성을 검사합니다.
    """
    if not isinstance(df_slice, pd.DataFrame) or len(df_slice) < 20:
        return False
    return True

def rising_wedge(df_slice):
    """
    라이징 웻지(상승 쐐기형) 패턴을 감지하고 유사도를 반환합니다.
    """
    if not is_valid_data(df_slice):
        return 0

    highs = df_slice['high']
    lows = df_slice['low']

    # 1. 고점과 저점이 모두 상승하는지 확인
    is_rising_highs = all(highs.iloc[i] < highs.iloc[i+1] for i in range(len(highs)-1))
    is_rising_lows = all(lows.iloc[i] < lows.iloc[i+1] for i in range(len(lows)-1))
    
    # 2. 고점과 저점의 상승 기울기가 수렴하는지 확인
    high_slope = np.polyfit(range(len(highs)), highs, 1)[0]
    low_slope = np.polyfit(range(len(lows)), lows, 1)[0]

    if is_rising_highs and is_rising_lows and (high_slope > 0 and low_slope > 0):
        if high_slope > low_slope:
            similarity = min(100, 100 - (high_slope - low_slope) * 100)
            return similarity
    return 0

def falling_wedge(df_slice):
    """
    폴링 웻지(하락 쐐기형) 패턴을 감지하고 유사도를 반환합니다.
    """
    if not is_valid_data(df_slice):
        return 0

    highs = df_slice['high']
    lows = df_slice['low']

    # 1. 고점과 저점이 모두 하락하는지 확인
    is_falling_highs = all(highs.iloc[i] > highs.iloc[i+1] for i in range(len(highs)-1))
    is_falling_lows = all(lows.iloc[i] > lows.iloc[i+1] for i in range(len(lows)-1))
    
    # 2. 고점과 저점의 하락 기울기가 수렴하는지 확인
    high_slope = np.polyfit(range(len(highs)), highs, 1)[0]
    low_slope = np.polyfit(range(len(lows)), lows, 1)[0]

    if is_falling_highs and is_falling_lows and (high_slope < 0 and low_slope < 0):
        if abs(low_slope) > abs(high_slope):
            similarity = min(100, 100 - (abs(low_slope) - abs(high_slope)) * 100)
            return similarity
    return 0

if __name__ == "__main__":
    # 이 부분은 테스트를 위한 예시 코드입니다.
    # 실제 백테스팅에서는 다른 파일에서 이 함수들을 호출합니다.
    print("wedge_patterns.py 파일이 성공적으로 로드되었습니다.")
