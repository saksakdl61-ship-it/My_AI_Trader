# main.py
# 이 스크립트는 AI 트레이딩 시스템의 중앙 관제 시스템 역할을 하며,
# 설정 파일에서 필요한 정보를 불러와 텔레그램 라이브 모드를 시작합니다.

import os
import configparser
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

def setup_logging():
    """로깅 설정을 초기화합니다."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
    )

def load_config(file_path):
    """
    지정된 경로의 설정 파일을 읽어옵니다.
    
    Args:
        file_path (str): 설정 파일의 경로.
    
    Returns:
        configparser.ConfigParser: 설정 객체.
    """
    if not os.path.exists(file_path):
        logging.error(f"오류: '{file_path}' 파일을 찾을 수 없습니다. 파일을 확인해주세요.")
        return None
        
    config = configparser.ConfigParser()
    try:
        config.read(file_path, encoding='utf-8')
    except Exception as e:
        logging.error(f"오류: '{file_path}' 파일 읽기 오류: {e}")
        return None
        
    return config

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/start 명령어를 처리하는 핸들러."""
    user_name = update.effective_user.first_name if update.effective_user else "사용자"
    logging.info(f"명령어 감지: /start (보낸 사람: {user_name}, ID: {update.effective_chat.id})")
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"안녕하세요, {user_name}님! AI 트레이딩 봇이 시작되었습니다. 필요한 명령을 입력해주세요."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """모든 텍스트 메시지를 처리하는 핸들러."""
    if update.message and update.message.text:
        logging.info(f"받은 메시지: {update.message.text} (보낸 사람: {update.effective_user.first_name})")
        
        if not update.message.text.startswith('/'):
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"받은 메시지: {update.message.text}"
            )

def main():
    """메인 실행 함수."""
    setup_logging()
    
    config_file = "config_home.ini"
    config = load_config(config_file)
    
    if config is None:
        return
        
    logging.info("🚀 중앙 관제 시스템 (텔레그램 라이브 모드)을 시작합니다...")
    
    # 텔레그램 설정 로드
    if 'TELEGRAM' in config:
        bot_token = config.get('TELEGRAM', 'bot_token', fallback=None)
        
        if not bot_token:
            logging.error("봇 토큰을 찾을 수 없습니다. config_home.ini 파일을 확인해주세요.")
            return
            
        logging.info("✅ 텔레그램 설정이 성공적으로 로드되었습니다.")
        
        # 텔레그램 봇 초기화 및 시작
        application = ApplicationBuilder().token(bot_token).build()
        
        # 명령어 핸들러 추가
        start_handler = CommandHandler('start', start)
        application.add_handler(start_handler)
        
        # 모든 텍스트 메시지를 처리하는 핸들러 추가 (명령어 제외)
        message_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
        application.add_handler(message_handler)
        
        # 봇 실행 시작 (무한 대기)
        logging.info("🤖 봇이 메시지를 대기 중입니다. 텔레그램에서 '/start'를 입력해보세요.")
        application.run_polling(allowed_updates=Update.ALL_TYPES)
        
    else:
        logging.warning("config_home.ini 파일에 [TELEGRAM] 섹션이 없습니다. 텔레그램 알림을 보내려면 이 섹션을 추가해야 합니다.")
        
    # PATHS 설정 로드
    if 'PATHS' in config and 'BASE_PATH' in config['PATHS']:
        base_path = config['PATHS']['BASE_PATH']
        logging.info(f"📁 기본 경로 설정: {base_path}")
    
if __name__ == "__main__":
    main()
