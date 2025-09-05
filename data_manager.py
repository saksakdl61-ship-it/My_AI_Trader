import os
import pandas as pd
import FinanceDataReader as fdr
import configparser

class DataManager:
    """
    Manages loading, updating, and managing stock data.
    """
    def __init__(self, config):
        """
        configparser 객체를 직접 인수로 받아 초기화합니다.
        """
        self.config = config
        
        # configparser는 키를 소문자로 자동 변환하므로 'base_path'를 사용합니다.
        self.base_path = self.config['PATHS']['base_path']
        self.data_path = os.path.join(self.base_path, "daily_price_fdr")
        if not os.path.exists(self.data_path):
            os.makedirs(self.data_path)

    def load_stock_list(self):
        """
        Loads the list of all KRX stock symbols.
        """
        try:
            stock_list_df = fdr.StockListing('KRX')
            if 'Code' in stock_list_df.columns:
                stock_list_df.rename(columns={'Code': 'Symbol'}, inplace=True)
            stock_codes = stock_list_df[stock_list_df['Symbol'].str.match(r'^\d{6}$')]['Symbol'].tolist()
            return stock_codes
        except Exception as e:
            print(f"❌ 종목 리스트 로딩 실패: {e}")
            return None

    def load_stock_data(self, code):
        """
        Loads historical data for a specific stock from a CSV file.
        """
        file_path = os.path.join(self.data_path, f"{code}.csv")
        if not os.path.exists(file_path):
            return None

        try:
            df = pd.read_csv(file_path)
            df['date'] = pd.to_datetime(df['date'].astype(str), errors='coerce')
            df.dropna(subset=['date'], inplace=True)
            df.set_index('date', inplace=True)
            return df
        except Exception as e:
            print(f"❌ {code} 데이터 로딩 중 오류: {e}")
            return None
