import os
import strategy_generator
import ai_backtester
import result_analyzer

def run_project_automation():
    """
    AI 트레이딩 프로젝트의 전체 워크플로우를 자동화하는 메인 함수.
    전략 생성, 백테스팅, 결과 분석을 순서대로 실행합니다.
    """
    print("--- [프로젝트 자동화 시작] ---")

    # 1단계: 트레이딩 전략 생성
    try:
        print("\n[1/3] 새로운 AI 전략을 생성하고 있습니다...")
        generator = strategy_generator.StrategyGenerator()
        generator.generate_strategy()
        print("✅ 전략 생성 완료.")
    except Exception as e:
        print(f"❌ 전략 생성 중 오류가 발생했습니다: {e}")
        return  # 오류 발생 시 프로세스 중단

    # 2단계: 생성된 전략으로 백테스팅 실행
    try:
        print("\n[2/3] 생성된 전략으로 백테스팅을 시작합니다...")
        backtester = ai_backtester.AIBacktester()
        backtester.run_backtest()
        print("✅ 백테스팅 완료.")
    except Exception as e:
        print(f"❌ 백테스팅 중 오류가 발생했습니다: {e}")
        return # 오류 발생 시 프로세스 중단

    # 3단계: 백테스팅 결과 분석
    try:
        print("\n[3/3] 백테스팅 결과를 분석하고 최종 보고서를 생성합니다...")
        analyzer = result_analyzer.ResultAnalyzer()
        analyzer.analyze_results()
        print("✅ 분석 완료. 최종 보고서가 생성되었습니다.")
    except Exception as e:
        print(f"❌ 결과 분석 중 오류가 발생했습니다: {e}")
        return # 오류 발생 시 프로세스 중단

    print("\n--- [모든 프로세스 완료] ---")
    print("성공적으로 프로젝트의 모든 작업을 완료했습니다. GitHub에 푸시할 준비가 되었습니다!")

if __name__ == "__main__":
    run_project_automation()