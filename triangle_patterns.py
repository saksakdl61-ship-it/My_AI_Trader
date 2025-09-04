import pandas as pd
import numpy as np

def is_valid_data(df_slice):
    """
    데이터프레임의 유효성을 검사합니다.
    """
    if not isinstance(df_slice, pd.DataFrame) or len(df_slice) == 0:
        return False
    return True

def ascending_triangle(df_slice):
    """
    어센딩 트라이앵글(상승삼각형) 패턴을 감지하고 유사도를 반환합니다.
    """
    if not is_valid_data(df_slice) or len(df_slice) < 10:
        return 0

    highs = df_slice['high']
    lows = df_slice['low']
    
    # 1. 고점이 수평 저항선을 형성하는지 확인
    resistance_line = highs.iloc[-5:].mean()
    highs_in_range = highs[(highs > resistance_line * 0.99) & (highs < resistance_line * 1.01)]
    is_horizontal_high = len(highs_in_range) > len(highs) * 0.5
    
    # 2. 저점이 점진적으로 상승하는지 확인
    is_rising_lows = all(lows.iloc[i] < lows.iloc[i+1] for i in range(len(lows)-1))
    
    if is_horizontal_high and is_rising_lows:
        # 유사도 계산: 저점 상승 각도와 고점 수평도
        low_slope = np.polyfit(range(len(lows)), lows, 1)[0]
        similarity = min(100, (low_slope * 10) + (100 - (abs(highs.max() - highs.min()) / highs.mean()) * 100))
        return similarity
    return 0

def descending_triangle(df_slice):
    """
    디센딩 트라이앵글(하락삼각형) 패턴을 감지하고 유사도를 반환합니다.
    """
    if not is_valid_data(df_slice) or len(df_slice) < 10:
        return 0

    highs = df_slice['high']
    lows = df_slice['low']

    # 1. 저점이 수평 지지선을 형성하는지 확인
    support_line = lows.iloc[-5:].mean()
    lows_in_range = lows[(lows > support_line * 0.99) & (lows < support_line * 1.01)]
    is_horizontal_low = len(lows_in_range) > len(lows) * 0.5

    # 2. 고점이 점진적으로 하락하는지 확인
    is_falling_highs = all(highs.iloc[i] > highs.iloc[i+1] for i in range(len(highs)-1))
    
    if is_horizontal_low and is_falling_highs:
        # 유사도 계산: 고점 하락 각도와 저점 수평도
        high_slope = np.polyfit(range(len(highs)), highs, 1)[0]
        similarity = min(100, (abs(high_slope) * 10) + (100 - (abs(lows.max() - lows.min()) / lows.mean()) * 100))
        return similarity
    return 0

def symmetrical_triangle(df_slice):
    """
    시메트리컬 트라이앵글(대칭삼각형) 패턴을 감지하고 유사도를 반환합니다.
    """
    if not is_valid_data(df_slice) or len(df_slice) < 10:
        return 0

    highs = df_slice['high']
    lows = df_slice['low']

    # 1. 고점이 점진적으로 하락하는지 확인
    is_falling_highs = all(highs.iloc[i] > highs.iloc[i+1] for i in range(len(highs)-1))

    # 2. 저점이 점진적으로 상승하는지 확인
    is_rising_lows = all(lows.iloc[i] < lows.iloc[i+1] for i in range(len(lows)-1))
    
    if is_falling_highs and is_rising_lows:
        # 유사도 계산: 고점 하락 각도와 저점 상승 각도
        high_slope = np.polyfit(range(len(highs)), highs, 1)[0]
        low_slope = np.polyfit(range(len(lows)), lows, 1)[0]
        
        # 두 선이 수렴하는지 확인
        if high_slope < 0 and low_slope > 0:
            similarity = min(100, 100 - (abs(high_slope + low_slope) * 50))
            return similarity
    return 0

if __name__ == "__main__":
    # 이 부분은 테스트를 위한 예시 코드입니다.
    # 실제 백테스팅에서는 다른 파일에서 이 함수들을 호출합니다.
    print("triangle_patterns.py 파일이 성공적으로 로드되었습니다.")
