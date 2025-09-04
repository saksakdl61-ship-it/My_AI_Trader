import pandas as pd
import numpy as np

class ReversalPatterns:
    def detect_bullish_engulfing(self, df_slice):
        """
        불리시 엥걸핑(Bullish Engulfing) 패턴을 감지하고 유사도를 0-100% 점수로 반환합니다.
        """
        if len(df_slice) < 2: return 0
        current_candle = df_slice.iloc[-1]
        prev_candle = df_slice.iloc[-2]

        is_bearish_prev = prev_candle['close'] < prev_candle['open']
        is_bullish_curr = current_candle['close'] > current_candle['open']
        
        engulfs_prev_body = (current_candle['open'] < prev_candle['close'] and
                             current_candle['close'] > prev_candle['open'])
                             
        if is_bearish_prev and is_bullish_curr and engulfs_prev_body:
            prev_body = abs(prev_candle['close'] - prev_candle['open'])
            curr_body = abs(current_candle['close'] - current_candle['open'])
            if prev_body == 0: return 0
            
            similarity = min(1.0, curr_body / prev_body)
            return int(similarity * 100)
            
        return 0

    def detect_bearish_engulfing(self, df_slice):
        """
        베어리시 엥걸핑(Bearish Engulfing) 패턴을 감지하고 유사도를 0-100% 점수로 반환합니다.
        """
        if len(df_slice) < 2: return 0
        current_candle = df_slice.iloc[-1]
        prev_candle = df_slice.iloc[-2]

        is_bullish_prev = prev_candle['close'] > prev_candle['open']
        is_bearish_curr = current_candle['close'] < current_candle['open']
        
        engulfs_prev_body = (current_candle['open'] > prev_candle['close'] and
                             current_candle['close'] < prev_candle['open'])
                             
        if is_bullish_prev and is_bearish_curr and engulfs_prev_body:
            prev_body = abs(prev_candle['close'] - prev_candle['open'])
            curr_body = abs(current_candle['close'] - current_candle['open'])
            if prev_body == 0: return 0
            
            similarity = min(1.0, curr_body / prev_body)
            return int(similarity * 100)
            
        return 0

    def detect_bullish_harami(self, df_slice):
        """
        불리시 하라미(Bullish Harami) 패턴을 감지하고 유사도를 0-100% 점수로 반환합니다.
        """
        if len(df_slice) < 2: return 0
        prev_c, curr_c = df_slice.iloc[-2], df_slice.iloc[-1]
        
        if prev_c['close'] < prev_c['open'] and curr_c['close'] > curr_c['open'] and curr_c['high'] < prev_c['high'] and curr_c['low'] > prev_c['low']:
            prev_body = abs(prev_c['close'] - prev_c['open'])
            curr_body = abs(curr_c['close'] - curr_c['open'])
            if prev_body == 0: return 0
            
            similarity = min(1.0, curr_body / prev_body)
            return int((1 - similarity) * 100)
            
        return 0
        
    def detect_morning_star(self, df_slice):
        """
        모닝 스타(Morning Star) 패턴을 감지하고 유사도를 0-100% 점수로 반환합니다.
        """
        if len(df_slice) < 3: return 0
        
        c1, c2, c3 = df_slice.iloc[-3], df_slice.iloc[-2], df_slice.iloc[-1]
        
        if not (c1['close'] < c1['open'] and # 첫 캔들 하락
                c2['high'] < c1['low'] and # 두 번째 캔들 갭 하락
                c3['close'] > c3['open'] and # 세 번째 캔들 상승
                c3['close'] > c1['open']): # 세 번째 캔들이 첫 번째 캔들 절반 이상
            return 0
        
        c2_body = abs(c2['open'] - c2['close'])
        c2_range = c2['high'] - c2['low']
        
        if c2_range == 0: return 0
        
        similarity = 1 - (c2_body / c2_range)
        return int(similarity * 100)
        
    def detect_evening_star(self, df_slice):
        """
        이브닝 스타(Evening Star) 패턴을 감지하고 유사도를 0-100% 점수로 반환합니다.
        """
        if len(df_slice) < 3: return 0
        
        c1, c2, c3 = df_slice.iloc[-3], df_slice.iloc[-2], df_slice.iloc[-1]
        
        if not (c1['close'] > c1['open'] and
                c2['low'] > c1['high'] and
                c3['close'] < c3['open'] and
                c3['close'] < c1['open']):
            return 0
        
        c2_body = abs(c2['open'] - c2['close'])
        c2_range = c2['high'] - c2['low']
        
        if c2_range == 0: return 0
        
        similarity = 1 - (c2_body / c2_range)
        return int(similarity * 100)

    def detect_three_white_soldiers(self, df_slice):
        """
        삼백병(Three White Soldiers) 패턴을 감지하고 유사도를 0-100% 점수로 반환합니다.
        """
        if len(df_slice) < 3: return 0
        
        c1, c2, c3 = df_slice.iloc[-3], df_slice.iloc[-2], df_slice.iloc[-1]

        if not (c1['close'] > c1['open'] and 
                c2['close'] > c2['open'] and
                c3['close'] > c3['open']): return 0
        
        if not (c2['open'] > c1['open'] and c2['close'] > c1['close'] and 
                c3['open'] > c2['open'] and c3['close'] > c2['close']): return 0
        
        c1_shadow_ratio = (c1['high'] - c1['low']) / (c1['close'] - c1['open']) if (c1['close'] - c1['open']) != 0 else 0
        c2_shadow_ratio = (c2['high'] - c2['low']) / (c2['close'] - c2['open']) if (c2['close'] - c2['open']) != 0 else 0
        c3_shadow_ratio = (c3['high'] - c3['low']) / (c3['close'] - c3['open']) if (c3['close'] - c3['open']) != 0 else 0
        
        if not (c1_shadow_ratio < 2 and c2_shadow_ratio < 2 and c3_shadow_ratio < 2): return 0

        avg_body_size = (c1['close']-c1['open'] + c2['close']-c2['open'] + c3['close']-c3['open']) / 3
        avg_range = (c1['high']-c1['low'] + c2['high']-c2['low'] + c3['high']-c3['low']) / 3
        
        if avg_range == 0: return 0
        
        similarity = (avg_body_size / avg_range)
        return int(similarity * 100)
    
    def detect_piercing_line(self, df_slice):
        """
        피어싱 라인(Piercing Line) 패턴을 감지하고 유사도를 0-100% 점수로 반환합니다.
        """
        if len(df_slice) < 2: return 0
        prev_c, curr_c = df_slice.iloc[-2], df_slice.iloc[-1]
        
        if prev_c['close'] < prev_c['open'] and curr_c['close'] > curr_c['open'] and curr_c['open'] < prev_c['low'] and curr_c['close'] > (prev_c['open'] + prev_c['close']) / 2:
            body_range = prev_c['open'] - prev_c['close']
            if body_range == 0: return 0
            similarity = (curr_c['close'] - prev_c['close']) / body_range
            return int(min(1, similarity) * 100)
            
        return 0

    def detect_dark_cloud_cover(self, df_slice):
        """
        다크 클라우드 커버(Dark Cloud Cover) 패턴을 감지하고 유사도를 0-100% 점수로 반환합니다.
        """
        if len(df_slice) < 2: return 0
        prev_c, curr_c = df_slice.iloc[-2], df_slice.iloc[-1]
        
        if prev_c['close'] > prev_c['open'] and curr_c['close'] < curr_c['open'] and curr_c['open'] > prev_c['high'] and curr_c['close'] < (prev_c['open'] + prev_c['close']) / 2:
            body_range = prev_c['close'] - prev_c['open']
            if body_range == 0: return 0
            similarity = (prev_c['close'] - curr_c['close']) / body_range
            return int(min(1, similarity) * 100)
            
        return 0
    
    def detect_tweezer_top(self, df_slice):
        """
        트위저 탑(Tweezer Top) 패턴을 감지하고 유사도를 0-100% 점수로 반환합니다.
        """
        if len(df_slice) < 2: return 0
        c1, c2 = df_slice.iloc[-2], df_slice.iloc[-1]
        
        if c1['high'] == c2['high'] and c1['close'] > c1['open'] and c2['close'] < c2['open']:
            peak_diff = abs(c1['high'] - c2['high'])
            if c1['high'] == 0: return 0
            similarity = 1 - (peak_diff / c1['high'])
            return int(similarity * 100)
            
        return 0

    def detect_tweezer_bottom(self, df_slice):
        """
        트위저 바텀(Tweezer Bottom) 패턴을 감지하고 유사도를 0-100% 점수로 반환합니다.
        """
        if len(df_slice) < 2: return 0
        c1, c2 = df_slice.iloc[-2], df_slice.iloc[-1]
        
        if c1['low'] == c2['low'] and c1['close'] < c1['open'] and c2['close'] > c2['open']:
            trough_diff = abs(c1['low'] - c2['low'])
            if c1['low'] == 0: return 0
            similarity = 1 - (trough_diff / c1['low'])
            return int(similarity * 100)
            
        return 0
