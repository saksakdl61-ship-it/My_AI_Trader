import pandas as pd
import numpy as np

# 우리가 만든 모든 패턴 모듈들을 불러옵니다.
from .single_candle_patterns import *
from .reversal_patterns import *
from .continuation_patterns import *
from .triangle_patterns import *
from .flag_pennant_patterns import *
from .wedge_patterns import *
from .complex_patterns import *

class Indicators:
    """
    모든 기술적 지표 및 차트 패턴 함수를 통합 관리하는 클래스입니다.
    """
    def calculate_rsi(self, df_slice, period=14):
        delta = df_slice['close'].diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        
        avg_gain = gain.rolling(window=period).mean()
        avg_loss = loss.rolling(window=period).mean()
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi.iloc[-1] if not rsi.empty else 0
    
    def calculate_macd(self, df_slice):
        ema_12 = df_slice['close'].ewm(span=12, adjust=False).mean()
        ema_26 = df_slice['close'].ewm(span=26, adjust=False).mean()
        macd_line = ema_12 - ema_26
        signal_line = macd_line.ewm(span=9, adjust=False).mean()
        
        return macd_line.iloc[-1], signal_line.iloc[-1]
    
    def is_doji(self, df_slice):
        return doji(df_slice)
        
    def is_hammer(self, df_slice):
        return hammer(df_slice)
        
    def is_shooting_star(self, df_slice):
        return shooting_star(df_slice)

    def is_bullish_engulfing(self, df_slice):
        return bullish_engulfing(df_slice)

    def is_morning_star(self, df_slice):
        return morning_star(df_slice)
        
    def is_inverse_head_and_shoulders(self, df_slice):
        return inverse_head_and_shoulders(df_slice)

    def is_cup_and_handle(self, df_slice):
        return cup_and_handle(df_slice)
        
    def is_ascending_triangle(self, df_slice):
        return ascending_triangle(df_slice)

    def is_bullish_flag(self, df_slice):
        return bullish_flag(df_slice)
        
    def is_rising_wedge(self, df_slice):
        return rising_wedge(df_slice)
        
    # 여기에 다른 모든 패턴 함수를 추가할 수 있습니다.
    
if __name__ == "__main__":
    print("indicators.py 파일이 성공적으로 로드되었습니다. 모든 하위 모듈이 연결되었습니다.")
