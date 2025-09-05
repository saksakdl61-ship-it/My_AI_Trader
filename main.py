import configparser
import logging
import os
from pathlib import Path

# 프로젝트의 다른 모듈들을 가져옵니다.
import strategy_generator
import ai_backtester
import result_analyzer

# --- 1. 전문 로깅 시스템 설정 ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('project_workflow.log', mode='w', encoding='utf-8')
    ]
)

class ProjectOrchestrator:
    """
    프로젝트의 전체 워크플로우를 조율하고 실행하는 클래스.
    설정 로드, 단계별 실행, 오류 처리를 중앙에서 관리합니다.
    """
    def __init__(self, config_path: str):
        """
        Orchestrator를 초기화하고 설정을 로드합니다.
        
        Args:
            config_path (str): 설정 파일의 경로.
        """
        self.config = self._load_config(config_path)
        if not self.config:
            raise ValueError("설정 파일 로드에 실패하여 Orchestrator를 초기화할 수 없습니다.")

    def _load_config(self, config_path: str) -> configparser.ConfigParser | None:
        """설정 파일을 안전하게 로드하고 파싱합니다."""
        logging.info(f"설정 파일 로딩 시도: '{config_path}'")
        if not os.path.exists(config_path):
            logging.error(f"치명적 오류: 설정 파일 '{config_path}'을 찾을 수 없습니다.")
            return None
        
        config = configparser.ConfigParser()
        config.read(config_path, encoding='utf-8')
        logging.info("✅ 설정 파일 로드 완료.")
        return config

    def run_step(self, step_name: str, step_function) -> bool:
        """워크플로우의 각 단계를 실행하고 결과를 로깅하는 헬퍼 함수."""
        logging.info(f"--- [단계 시작] {step_name} ---")
        try:
            step_function()
            logging.info(f"✅ [단계 완료] {step_name}")
            return True
        except Exception as e:
            logging.error(f"❌ [단계 실패] {step_name} 중 오류 발생: {e}", exc_info=True)
            return False

    def execute_workflow(self):
        """전체 자동화 워크플로우를 순서대로 실행합니다."""
        logging.info("🚀 프로젝트 전체 자동화 워크플로우를 시작합니다.")

        if not self.run_step("설정 기반 전략 백테스팅", self._step_run_backtest):
            return
        
        if not self.run_step("결과 분석 및 보고", self._step_analyze_results):
            return

        logging.info("🎉 모든 워크플로우 단계가 성공적으로 완료되었습니다.")

    # --- 각 워크플로우 단계별 구현 ---
    def _step_run_backtest(self):
        """설정 파일에 정의된 파라미터로 백테스팅을 실행합니다."""
        backtester = ai_backtester.AIBacktester(config=self.config)
        backtester.run_backtest()

    def _step_analyze_results(self):
        """백테스팅 결과 리포트를 분석하고 순위를 출력합니다."""
        # ResultAnalyzer 객체를 생성할 때, self.config를 인자로 전달합니다.
        # 이제 파일 경로를 직접 넘겨줄 필요가 없습니다.
        analyzer = result_analyzer.ResultAnalyzer(config=self.config)
        analyzer.display_ranking()


if __name__ == "__main__":
    CONFIG_FILE = 'config_home.ini'
    try:
        orchestrator = ProjectOrchestrator(config_path=CONFIG_FILE)
        orchestrator.execute_workflow()
    except (ValueError, KeyError) as e:
        logging.critical(f"프로젝트 실행에 실패했습니다. 원인: {e}")


def _step_analyze_results(self):
    # ResultAnalyzer 객체를 생성할 때, self.config를 인자로 전달합니다.
    analyzer = result_analyzer.ResultAnalyzer(config=self.config)
    analyzer.display_ranking()

