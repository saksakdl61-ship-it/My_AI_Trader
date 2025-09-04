import configparser
import logging
from pathlib import Path
import google.generativeai as genai

class StrategyGenerator:
    """
    AI를 사용하여 트레이딩 전략을 생성하고 파일에 저장하는 역할을 담당하는 클래스.
    모든 설정은 외부 config 객체로부터 주입받습니다.
    """
    def __init__(self, config: configparser.ConfigParser):
        """
        StrategyGenerator를 초기화합니다.
        
        Args:
            config (configparser.ConfigParser): 프로젝트의 전체 설정이 담긴 객체.
        """
        self.config = config
        self.gemini_api_key = None
        self.strategy_file_path = None
        self._configure()

    def _configure(self):
        """설정 객체로부터 필요한 값들을 불러와 클래스 내부 변수를 설정합니다."""
        logging.info("전략 생성기(StrategyGenerator) 설정 시작...")
        try:
            # API 키 설정
            self.gemini_api_key = self.config.get('API_KEYS', 'GEMINI_API_KEY')
            genai.configure(api_key=self.gemini_api_key)

            # 파일 경로 설정
            base_path = Path(self.config.get('PATHS', 'BASE_PATH'))
            strategy_file = self.config.get('PATHS', 'strategy_file')
            self.strategy_file_path = base_path / strategy_file
            
            # 생성된 전략을 저장할 디렉토리가 없으면 생성
            self.strategy_file_path.parent.mkdir(parents=True, exist_ok=True)
            
            logging.info("✅ 전략 생성기 설정 완료.")
        except (configparser.NoSectionError, configparser.NoOptionError) as e:
            logging.error(f"설정 파일에서 필요한 키를 찾을 수 없습니다: {e}")
            raise KeyError(f"설정 파일의 [API_KEYS] 또는 [PATHS] 섹션을 확인해주세요: {e}")
        except Exception as e:
            logging.error(f"Gemini API 설정 중 예상치 못한 오류 발생: {e}")
            raise

    def generate_strategy(self):
        """
        Gemini AI 모델을 사용하여 새로운 트레이딩 전략을 생성하고 파일에 저장합니다.
        """
        logging.info("Gemini AI를 통해 새로운 트레이딩 전략 생성을 시작합니다.")
        try:
            model = genai.GenerativeModel('gemini-pro')
            
            # AI에게 보낼 프롬프트를 정의합니다.
            prompt = """
            You are an expert in financial trading strategies.
            Generate a single, unique trading strategy based on a combination of technical indicators for the stock market.
            The strategy should be described in one line and formatted as follows:
            
            buy: [Indicator 1] [Condition 1] AND [Indicator 2] [Condition 2] | sell: [Indicator 3] [Condition 3]
            
            Example:
            buy: RSI(14) < 30 AND MACD_hist(12,26,9) > 0 | sell: RSI(14) > 70
            """
            
            response = model.generate_content(prompt)
            new_strategy = response.text.strip()

            if not new_strategy:
                logging.warning("AI가 유효한 전략을 생성하지 못했습니다.")
                return

            logging.info(f"생성된 새로운 전략: {new_strategy}")
            
            # 생성된 전략을 파일에 추가합니다. 'a' 모드는 덮어쓰지 않고 이어씁니다.
            with open(self.strategy_file_path, 'a', encoding='utf-8') as f:
                f.write(new_strategy + '\n')
            
            logging.info(f"✅ 새로운 전략을 '{self.strategy_file_path}' 파일에 성공적으로 저장했습니다.")

        except Exception as e:
            logging.error(f"AI 전략 생성 또는 파일 저장 중 오류 발생: {e}")
            # 오류가 발생해도 워크플로우가 중단되도록 예외를 다시 발생시킵니다.
            raise

if __name__ == '__main__':
    # 이 파일을 단독으로 테스트하고 싶을 때 사용하는 코드
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    # 테스트를 위해 실제 config 파일을 읽어옵니다.
    test_config = configparser.ConfigParser()
    try:
        test_config.read('config_home.ini', encoding='utf-8')
        if not test_config.sections():
             raise FileNotFoundError("config_home.ini 파일을 찾을 수 없거나 비어있습니다.")
        
        generator = StrategyGenerator(config=test_config)
        generator.generate_strategy()
    except (FileNotFoundError, KeyError) as e:
        logging.error(f"테스트 실행 실패: {e}")
