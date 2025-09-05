import configparser
import logging
import os
from pathlib import Path
from typing import Optional

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

# --- 2. 워크플로우 단계별 함수 정의 ---
def _load_config(config_path: str) -> Optional[configparser.ConfigParser]:
    """
    설정 파일을 안전하게 로드하고 파싱합니다.
    [PATHS] 섹션의 존재 여부를 명확하게 검증합니다.
    """
    absolute_path = os.path.abspath(config_path)
    logging.info(f"설정 파일 로딩 시도: '{absolute_path}'")
    if not os.path.exists(absolute_path):
        logging.error(f"치명적 오류: 설정 파일 '{absolute_path}'을 찾을 수 없습니다.")
        return None
    
    config = configparser.ConfigParser()
    read_files = config.read(absolute_path, encoding='utf-8')

    if not read_files:
        logging.error(f"설정 파일을 읽을 수 없습니다: '{absolute_path}'. 파일이 비어있거나, 형식에 오류가 있을 수 있습니다.")
        return None

    logging.info("✅ 설정 파일 로드 완료.")

    # --- 필수 섹션([PATHS])의 존재 여부를 명확히 검증합니다. ---
    logging.info("--- 로드된 설정 내용 확인 ---")
    if config.sections():
        for section in config.sections():
            logging.info(f"섹션: [{section}]")
            for key, value in config.items(section):
                logging.info(f"  {key} = {value}")
    else:
        logging.warning("경고: 설정 파일에서 섹션을 찾을 수 없습니다.")
    logging.info("-----------------------------")
    
    if not config.has_section('PATHS'):
        logging.critical("치명적 오류: 설정 파일에서 필수 섹션 '[PATHS]'를 찾을 수 없습니다.")
        # KeyError 대신 더 명확한 ValueError를 발생시켜 실행을 중단합니다.
        raise ValueError("설정 파일에서 필수 섹션 '[PATHS]'를 찾을 수 없습니다. 파일 경로 또는 내용을 다시 확인해주세요.")

    return config

def _run_step(step_name: str, step_function, *args, fail_on_error: bool = True) -> bool:
    """
    워크플로우의 각 단계를 실행하고 결과를 로깅하는 헬퍼 함수.
    
    Args:
        step_name (str): 단계 이름 (로깅용).
        step_function (callable): 실행할 함수.
        *args: step_function에 전달할 인수.
        fail_on_error (bool): True인 경우, 오류 발생 시 False를 반환하여 워크플로우를 중단합니다.
                            False인 경우, 오류를 로깅하고 True를 반환하여 계속 진행합니다.
    Returns:
        bool: 단계 성공 여부.
    """
    logging.info(f"--- [단계 시작] {step_name} ---")
    try:
        step_function(*args)
        logging.info(f"✅ [단계 완료] {step_name}")
        return True
    except Exception as e:
        logging.error(f"❌ [단계 실패] {step_name} 중 오류 발생: {e}", exc_info=True)
        if fail_on_error:
            return False
        else:
            return True

def _step_run_backtest(config: configparser.ConfigParser):
    """설정 파일에 정의된 파라미터로 백테스팅을 실행합니다."""
    backtester = ai_backtester.AIBacktester(config=config)
    backtester.run_backtest()

def _step_analyze_results(config: configparser.ConfigParser):
    """백테스팅 결과 리포트를 분석하고 순위를 출력합니다."""
    analyzer = result_analyzer.ResultAnalyzer(config=config)
    analyzer.display_ranking()

# --- 3. 전체 워크플로우를 실행하는 메인 함수 ---
def execute_workflow(config: configparser.ConfigParser):
    """전체 자동화 워크플로우를 순서대로 실행합니다."""
    logging.info("🚀 프로젝트 전체 자동화 워크플로우를 시작합니다.")

    # 백테스팅 단계는 반드시 성공해야 하므로 fail_on_error=True (기본값)
    if not _run_step("설정 기반 전략 백테스팅", _step_run_backtest, config):
        return
    
    # 결과 분석 단계는 오류가 나더라도 워크플로우를 중단하지 않도록 설정
    if not _run_step("결과 분석 및 보고", _step_analyze_results, config, fail_on_error=False):
        # 이 예시에서는 continue를 사용하지 않고 return을 유지하여 전체 워크플로우는 
        # 여전히 분석 단계 실패 시 종료됩니다.
        # 유연성 제어를 위한 예시일 뿐입니다.
        return

    logging.info("🎉 모든 워크플로우 단계가 성공적으로 완료되었습니다.")

# --- 4. 프로그램 시작점 ---
if __name__ == "__main__":
    CONFIG_FILE = 'config_home.ini'
    try:
        config = _load_config(config_path=CONFIG_FILE)
        if config:
            execute_workflow(config=config)
        else:
            raise ValueError("설정 파일 로드 실패")
    except (ValueError, KeyError) as e:
        logging.critical(f"프로젝트 실행에 실패했습니다. 원인: {e}")
