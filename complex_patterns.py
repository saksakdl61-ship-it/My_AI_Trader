import pandas as pd
import numpy as np

def is_valid_data(df_slice):
    """
    데이터프레임의 유효성을 검사합니다.
    """
    if not isinstance(df_slice, pd.DataFrame) or len(df_slice) < 50:
        return False
    return True

def find_pivot_points(data):
    """
    고점 및 저점 피벗 포인트를 찾습니다.
    """
    pivots = []
    for i in range(2, len(data) - 2):
        is_high_pivot = (data['high'].iloc[i] > data['high'].iloc[i-1] and
                         data['high'].iloc[i] > data['high'].iloc[i-2] and
                         data['high'].iloc[i] > data['high'].iloc[i+1] and
                         data['high'].iloc[i] > data['high'].iloc[i+2])
        is_low_pivot = (data['low'].iloc[i] < data['low'].iloc[i-1] and
                        data['low'].iloc[i] < data['low'].iloc[i-2] and
                        data['low'].iloc[i] < data['low'].iloc[i+1] and
                        data['low'].iloc[i] < data['low'].iloc[i+2])
        if is_high_pivot:
            pivots.append({'type': 'high', 'price': data['high'].iloc[i], 'index': i})
        elif is_low_pivot:
            pivots.append({'type': 'low', 'price': data['low'].iloc[i], 'index': i})
    return pivots

def cup_and_handle(df_slice):
    """
    컵앤핸들 패턴을 감지하고 유사도를 반환합니다.
    """
    if not is_valid_data(df_slice):
        return 0
    
    pivots = find_pivot_points(df_slice)
    
    # 컵 모양 찾기
    cup_end_index = None
    cup_start_index = None
    cup_low_index = None

    for i in range(len(pivots) - 2):
        if pivots[i]['type'] == 'high' and pivots[i+2]['type'] == 'high' and pivots[i+1]['type'] == 'low':
            if pivots[i]['price'] > pivots[i+2]['price'] * 0.95 and pivots[i]['price'] < pivots[i+2]['price'] * 1.05:
                if pivots[i+1]['price'] < pivots[i]['price'] * 0.8:
                    cup_start_index = pivots[i]['index']
                    cup_end_index = pivots[i+2]['index']
                    cup_low_index = pivots[i+1]['index']
                    break
    
    if cup_start_index is None:
        return 0

    # 손잡이 모양 찾기
    handle_start_index = cup_end_index
    handle_end_index = None
    for i in range(len(pivots) - 1):
        if pivots[i]['index'] >= handle_start_index and pivots[i+1]['type'] == 'low' and pivots[i+1]['price'] > pivots[i]['price'] * 0.9 and pivots[i+1]['index'] > handle_start_index:
            handle_end_index = pivots[i+1]['index']
            break

    if handle_end_index is None:
        return 0
        
    # 유사도 계산
    cup_depth = df_slice['high'].iloc[cup_end_index] - df_slice['low'].iloc[cup_low_index]
    handle_depth = df_slice['high'].iloc[handle_start_index:handle_end_index].max() - df_slice['low'].iloc[handle_start_index:handle_end_index].min()
    
    if handle_depth < cup_depth * 0.5:
        return 100 - (handle_depth / (cup_depth * 0.5)) * 100
    
    return 0

def inverse_head_and_shoulders(df_slice):
    """
    역헤드앤숄더 패턴을 감지하고 유사도를 반환합니다.
    """
    if not is_valid_data(df_slice):
        return 0
    
    pivots = find_pivot_points(df_slice)
    
    # 패턴의 세 지점(왼쪽 어깨, 머리, 오른쪽 어깨) 찾기
    lows = [p for p in pivots if p['type'] == 'low']
    if len(lows) < 3:
        return 0

    left_shoulder = None
    head = None
    right_shoulder = None
    
    for i in range(len(lows) - 2):
        if lows[i]['index'] < lows[i+1]['index'] and lows[i+1]['index'] < lows[i+2]['index']:
            # 머리가 양쪽 어깨보다 깊은지 확인
            if lows[i+1]['price'] < lows[i]['price'] and lows[i+1]['price'] < lows[i+2]['price']:
                # 머리와 어깨 사이의 고점이 있는지 확인
                if len([p for p in pivots if p['type'] == 'high' and pivots[i]['index'] < p['index'] < pivots[i+1]['index']]) > 0 and \
                   len([p for p in pivots if p['type'] == 'high' and pivots[i+1]['index'] < p['index'] < pivots[i+2]['index']]) > 0:
                    left_shoulder = lows[i]
                    head = lows[i+1]
                    right_shoulder = lows[i+2]
                    break

    if not all([left_shoulder, head, right_shoulder]):
        return 0
        
    # 유사도 계산: 어깨 높이, 대칭성, 넥라인 기울기
    shoulder_diff = abs(left_shoulder['price'] - right_shoulder['price'])
    head_depth = head['price']
    
    similarity = min(100, 100 - shoulder_diff / head_depth * 100)
    return similarity

if __name__ == "__main__":
    print("complex_patterns.py 파일이 성공적으로 로드되었습니다.")
