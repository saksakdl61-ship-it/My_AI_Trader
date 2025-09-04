import configparser
import logging
from pathlib import Path
import pandas as pd
import re

class ResultAnalyzer:
    """
    백테스팅 결과 리포트 파일을 분석하고, 성과가 좋은 순서대로 순위를 매겨 출력합니다.
    모든 설정은 외부 config 객체로부터 주입받습니다.
    """
    def __init__(self, config: configparser.ConfigParser):
        """
        ResultAnalyzer를 초기화합니다.
        
        Args:
            config (configparser.ConfigParser): 프로젝트의 전체 설정이 담긴 객체.
        """
        self.config = config
        self.report_file_path = None
        self._configure()

    def _configure(self):
        """설정 객체로부터 필요한 파일 경로를 불러와 클래스 내부 변수를 설정합니다."""
        logging.info("결과 분석기(ResultAnalyzer) 설정 시작...")
        try:
            base_path = Path(self.config.get('PATHS', 'BASE_PATH'))
            report_file = self.config.get('PATHS', 'report_file')
            self.report_file_path = base_path / report_file
            logging.info("✅ 결과 분석기 설정 완료.")
        except (configparser.NoSectionError, configparser.NoOptionError) as e:
            logging.error(f"설정 파일에서 필요한 경로 키를 찾을 수 없습니다: {e}")
            raise KeyError(f"설정 파일의 [PATHS] 섹션을 확인해주세요: {e}")

    def _parse_results(self) -> list[dict]:
        """리포트 파일을 읽고 정규식을 사용하여 각 줄을 파싱합니다."""
        if not self.report_file_path.exists():
            logging.error(f"결과 분석 오류: 리포트 파일 '{self.report_file_path}'를 찾을 수 없습니다.")
            raise FileNotFoundError(f"리포트 파일 '{self.report_file_path}'가 존재하지 않습니다.")

        results = []
        # 정규식 패턴: 전략 이름, 총 수익률, 승률, MDD를 추출
        pattern = re.compile(
            r"^(.*?) -> 총 수익률: ([\-\d\.]+)%, 승률: ([\d\.]+)%, MDD: ([\d\.]+)%"
        )
        
        logging.info(f"'{self.report_file_path}' 파일 분석 시작...")
        with open(self.report_file_path, "r", encoding="utf-8") as f:
            for line in f:
                match = pattern.match(line.strip())
                if match:
                    results.append({
                        "전략": match.group(1).strip(),
                        "총 수익률(%)": float(match.group(2)),
                        "승률(%)": float(match.group(3)),
                        "MDD(%)": float(match.group(4))
                    })
        return results

    def display_ranking(self):
        """
        분석된 결과를 총 수익률이 높은 순서대로 정렬하여 표 형태로 로깅합니다.
        """
        try:
            results_data = self._parse_results()
            if not results_data:
                logging.warning("분석할 유효한 백테스팅 결과 데이터가 없습니다.")
                return

            df = pd.DataFrame(results_data)
            
            # 총수익률이 높은 순서대로 정렬
            df_sorted = df.sort_values(by="총 수익률(%)", ascending=False)
            
            # 보기 좋은 표 형태로 변환하여 로깅
            ranking_table = df_sorted.to_string(index=False)
            
            # logging.info()는 여러 줄 출력이 깔끔하지 않으므로, 구분선을 넣어 별도로 출력
            report_header = "\n--- 백테스팅 전략 순위 (총 수익률 기준) ---"
            report_footer = "-------------------------------------------\n"
            
            # 최종 보고서를 콘솔과 로그 파일에 기록
            full_report = f"{report_header}\n{ranking_table}\n{report_footer}"
            logging.info(full_report)

        except FileNotFoundError:
            # _parse_results에서 이미 로깅했으므로 여기서는 예외를 다시 발생시켜 main 흐름을 중단
            raise
        except Exception as e:
            logging.error(f"결과 분석 또는 순위 표시 중 예상치 못한 오류 발생: {e}")
            raise

if __name__ == '__main__':
    # 이 파일을 단독으로 테스트하고 싶을 때 사용하는 코드
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    test_config = configparser.ConfigParser()
    try:
        test_config.read('config_home.ini', encoding='utf-8')
        if not test_config.sections():
             raise FileNotFoundError("config_home.ini 파일을 찾을 수 없거나 비어있습니다.")
        
        analyzer = ResultAnalyzer(config=test_config)
        analyzer.display_ranking()
    except (FileNotFoundError, KeyError) as e:
        logging.error(f"테스트 실행 실패: {e}")

