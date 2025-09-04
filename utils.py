# utils.py
# 이 파일은 프로젝트의 모든 스크립트가 공통으로 사용하는 유틸리티 함수들을 모아놓은 모듈입니다.

import configparser
import logging
import requests

# --- 설정값 ---
LOG_FILE_PATH = "project_log.txt"

def setup_logging():
    """
    프로젝트의 모든 스크립트가 공유할 로깅 시스템을 설정합니다.
    로그를 콘솔과 파일에 동시에 기록합니다.
    """
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(LOG_FILE_PATH, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )

def get_telegram_credentials():
    """
    config_home.ini 파일에서 텔레그램 인증 정보를 불러옵니다.
    """
    config = configparser.ConfigParser()
    config.read('config_home.ini', encoding='utf-8')
    
    bot_token = None
    chat_id = None
    
    try:
        if 'TELEGRAM' in config:
            bot_token = config['TELEGRAM'].get('TELEGRAM_BOT_TOKEN')
            chat_id = config['TELEGRAM'].get('TELEGRAM_CHAT_ID')
        else:
            logging.warning("config_home.ini 파일에 [TELEGRAM] 섹션이 없습니다. 텔레그램 알림을 보내려면 이 섹션을 추가해야 합니다.")
    except KeyError:
        logging.error("config_home.ini 파일에서 TELEGRAM_BOT_TOKEN 또는 TELEGRAM_CHAT_ID를 찾을 수 없습니다.")
        
    return bot_token, chat_id

def send_telegram_notification(message):
    """
    텔레그램 봇으로 알림 메시지를 보냅니다.
    """
    bot_token, chat_id = get_telegram_credentials()

    if not bot_token or not chat_id:
        logging.warning("텔레그램 알림을 보낼 수 없습니다. config_home.ini 파일에 올바른 인증 정보를 입력해주세요.")
        return

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': message
    }
    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()
        logging.info("텔레그램 알림 전송 완료!")
    except requests.exceptions.RequestException as e:
        logging.error(f"텔레그램 알림 전송 실패: {e}")

if __name__ == "__main__":
    setup_logging()
    logging.info("utils.py 모듈이 정상적으로 설정되었습니다.")
