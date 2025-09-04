import pandas as pd
import numpy as np

def is_valid_data(df_slice):
    """
    데이터프레임의 유효성을 검사합니다.
    """
    if not isinstance(df_slice, pd.DataFrame) or len(df_slice) < 20:
        return False
    return True

def bullish_flag(df_slice):
    """
    불리시 플래그(상승 깃발형) 패턴을 감지하고 유사도를 반환합니다.
    """
    if not is_valid_data(df_slice):
        return 0
    
    # 1단계: 강한 상승 추세(깃대) 찾기
    pole = df_slice.iloc[:len(df_slice)//2]
    if pole['close'].iloc[-1] <= pole['close'].iloc[0]:
        return 0
    pole_return = (pole['close'].iloc[-1] - pole['close'].iloc[0]) / pole['close'].iloc[0]
    
    # 2단계: 깃발 모양(약한 하락/횡보) 찾기
    flag = df_slice.iloc[len(df_slice)//2:]
    if flag['close'].iloc[-1] >= flag['close'].iloc[0]:
        return 0
        
    # 3단계: 유사도 계산
    flag_slope = np.polyfit(range(len(flag)), flag['close'], 1)[0]
    ideal_slope = -0.1
    similarity = 100 - abs(flag_slope - ideal_slope) * 50
    
    if pole_return > 0.1 and flag_slope < 0:
        return min(100, similarity)
    return 0

def bearish_flag(df_slice):
    """
    베어리시 플래그(하락 깃발형) 패턴을 감지하고 유사도를 반환합니다.
    """
    if not is_valid_data(df_slice):
        return 0
    
    # 1단계: 강한 하락 추세(깃대) 찾기
    pole = df_slice.iloc[:len(df_slice)//2]
    if pole['close'].iloc[-1] >= pole['close'].iloc[0]:
        return 0
    pole_return = (pole['close'].iloc[-1] - pole['close'].iloc[0]) / pole['close'].iloc[0]
    
    # 2단계: 깃발 모양(약한 상승/횡보) 찾기
    flag = df_slice.iloc[len(df_slice)//2:]
    if flag['close'].iloc[-1] <= flag['close'].iloc[0]:
        return 0
        
    # 3단계: 유사도 계산
    flag_slope = np.polyfit(range(len(flag)), flag['close'], 1)[0]
    ideal_slope = 0.1
    similarity = 100 - abs(flag_slope - ideal_slope) * 50
    
    if pole_return < -0.1 and flag_slope > 0:
        return min(100, similarity)
    return 0

def bullish_pennant(df_slice):
    """
    불리시 페넌트(상승 페넌트형) 패턴을 감지하고 유사도를 반환합니다.
    """
    if not is_valid_data(df_slice):
        return 0
    
    # 1단계: 강한 상승 추세(깃대) 찾기
    pole = df_slice.iloc[:len(df_slice)//2]
    if pole['close'].iloc[-1] <= pole['close'].iloc[0]:
        return 0
    pole_return = (pole['close'].iloc[-1] - pole['close'].iloc[0]) / pole['close'].iloc[0]
    
    # 2단계: 페넌트 모양(수렴) 찾기
    pennant = df_slice.iloc[len(df_slice)//2:]
    
    highs = pennant['high']
    lows = pennant['low']
    is_falling_highs = all(highs.iloc[i] > highs.iloc[i+1] for i in range(len(highs)-1))
    is_rising_lows = all(lows.iloc[i] < lows.iloc[i+1] for i in range(len(lows)-1))
    
    if is_falling_highs and is_rising_lows:
        high_slope = np.polyfit(range(len(highs)), highs, 1)[0]
        low_slope = np.polyfit(range(len(lows)), lows, 1)[0]
        similarity = min(100, 100 - (abs(high_slope + low_slope) * 50))
        return similarity
    return 0

def bearish_pennant(df_slice):
    """
    베어리시 페넌트(하락 페넌트형) 패턴을 감지하고 유사도를 반환합니다.
    """
    if not is_valid_data(df_slice):
        return 0
    
    # 1단계: 강한 하락 추세(깃대) 찾기
    pole = df_slice.iloc[:len(df_slice)//2]
    if pole['close'].iloc[-1] >= pole['close'].iloc[0]:
        return 0
    pole_return = (pole['close'].iloc[-1] - pole['close'].iloc[0]) / pole['close'].iloc[0]
    
    # 2단계: 페넌트 모양(수렴) 찾기
    pennant = df_slice.iloc[len(df_slice)//2:]
    
    highs = pennant['high']
    lows = pennant['low']
    is_falling_highs = all(highs.iloc[i] > highs.iloc[i+1] for i in range(len(highs)-1))
    is_rising_lows = all(lows.iloc[i] < lows.iloc[i+1] for i in range(len(lows)-1))

    if is_falling_highs and is_rising_lows:
        high_slope = np.polyfit(range(len(highs)), highs, 1)[0]
        low_slope = np.polyfit(range(len(lows)), lows, 1)[0]
        similarity = min(100, 100 - (abs(high_slope + low_slope) * 50))
        return similarity
    return 0

if __name__ == "__main__":
    # 이 부분은 테스트를 위한 예시 코드입니다.
    # 실제 백테스팅에서는 다른 파일에서 이 함수들을 호출합니다.
    print("flag_pennant_patterns.py 파일이 성공적으로 로드되었습니다.")
