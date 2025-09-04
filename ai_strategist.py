# ai_strategist.py
# 이 스크립트는 가장 성과가 좋았던 백테스팅 전략들을 분석하여
# 인공지능 모델에게 새로운 거래 전략 아이디어를 제안받습니다.

import json
import os
import sys
import configparser

# 프로젝트의 상위 디렉토리를 PYTHONPATH에 추가하여 라이브러리 접근을 용이하게 합니다.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# API 호출에 필요한 기본 정보들을 설정합니다.
def get_api_key_from_config(file_path, section, key):
    """
    지정된 .ini 파일에서 API 키를 읽어오는 함수.
    """
    config = configparser.ConfigParser()
    
    # config.ini 파일이 없으면 빈 파일을 생성
    if not os.path.exists(file_path):
        with open(file_path, 'w') as f:
            f.write(f'[{section}]\n{key}=\n')
        print(f"경고: '{file_path}' 파일이 존재하지 않아 새로 생성했습니다. 파일을 열어 [{section}] 섹션 아래에 {key} 값을 입력해주세요.")
        return None
        
    try:
        config.read(file_path, encoding='utf-8')
        api_key = config.get(section, key)
        if not api_key:
            print(f"오류: '{file_path}' 파일의 [{section}] 섹션에 {key} 값이 비어 있습니다. 유효한 API 키를 입력해주세요.")
            return None
        return api_key
    except configparser.NoSectionError:
        print(f"오류: '{file_path}' 파일에 [{section}] 섹션이 존재하지 않습니다. 섹션을 추가해주세요.")
        return None
    except configparser.NoOptionError:
        print(f"오류: '{file_path}' 파일의 [{section}] 섹션에 '{key}' 옵션이 존재하지 않습니다. 옵션을 추가해주세요.")
        return None
    except Exception as e:
        print(f"오류: '{file_path}' 파일을 읽는 중 예기치 않은 오류가 발생했습니다: {e}")
        return None

# 'config_home.ini' 파일에서 API 키를 불러옵니다.
CONFIG_FILE_PATH = 'config_home.ini'
API_KEY = get_api_key_from_config(CONFIG_FILE_PATH, 'API_KEYS', 'GEMINI_API_KEY')
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent?key={API_KEY}"

if __name__ == "__main__":
    if not API_KEY:
        print("API 키가 없어 스크립트를 실행할 수 없습니다. 'config_home.ini' 파일을 확인해주세요.")
    else:
        # 사용자로부터 받은 백테스팅 상위 전략 3개를 하드코딩합니다.
        top_strategies = [
            {'Strategy': '수익_20%_손절_3%_물타기_없음', 'Total Return (%)': 14.95},
            {'Strategy': '수익_20%_손절_5%_물타기_없음', 'Total Return (%)': 14.47},
            {'Strategy': '수익_15%_손절_3%_물타기_없음', 'Total Return (%)': 14.40}
        ]
        
        # AI에게 전달할 시스템 메시지를 작성합니다.
        # 전문가 페르소나와 요청 내용을 구체적으로 정의합니다.
        system_instruction = (
            "당신은 세계적인 금융 및 AI 전문가입니다. "
            "다음은 최근 백테스팅을 통해 가장 높은 성과를 낸 전략들의 결과입니다. "
            "이 데이터를 분석하여 기존 전략의 장점을 극대화하고 약점을 보완할 수 있는 "
            "새로운 거래 전략 아이디어를 세 가지 제안해주세요. "
            "각 전략 아이디어는 100자 이내의 간결한 설명과 함께 제공되어야 합니다."
        )
        
        # 백테스팅 결과를 사용자 입력 메시지로 변환합니다.
        user_prompt = "다음은 백테스팅 결과입니다:\n"
        for rank, strategy in enumerate(top_strategies):
            user_prompt += f"{rank + 1}. 전략: {strategy['Strategy']}, 총수익률: {strategy['Total Return (%)']}%\n"
            
        user_prompt += "\n위 결과를 바탕으로 새로운 전략 아이디어를 세 가지 제안해주세요."
        
        # Gemini API 요청에 사용할 페이로드를 구성합니다.
        payload = {
            "contents": [{"parts": [{"text": user_prompt}]}],
            "systemInstruction": {"parts": [{"text": system_instruction}]},
        }
        
        # API 호출을 위한 JavaScript 코드를 문자열로 생성합니다.
        fetch_code = f"""
            async function fetchAIStrategy() {{
                const payload = {json.dumps(payload, ensure_ascii=False, indent=4)};
                const apiUrl = "{API_URL}";
                
                try {{
                    // API 호출을 시작하기 전에 로딩 상태를 표시합니다.
                    document.getElementById('loading').style.display = 'block';
                    document.getElementById('suggestions-container').style.display = 'none';

                    const response = await fetch(apiUrl, {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify(payload)
                    }});
                    
                    // HTTP 오류 응답을 확인합니다.
                    if (!response.ok) {{
                        const errorData = await response.json();
                        console.error('API Error:', errorData);
                        throw new Error(`API 호출 실패: ${{response.status}} ${{response.statusText}}`);
                    }}
                    
                    const result = await response.json();
                    const candidate = result.candidates?.[0];
                    const generatedText = candidate?.content?.parts?.[0]?.text;
                    
                    // 생성된 텍스트가 없으면 오류 처리합니다.
                    if (!generatedText) {{
                        throw new Error('AI 응답에서 유효한 텍스트를 찾을 수 없습니다.');
                    }}
                    
                    // 생성된 텍스트를 HTML에 표시합니다.
                    document.getElementById('ai-suggestions').innerText = generatedText;
                    document.getElementById('suggestions-container').style.display = 'block';

                }} catch (error) {{
                    console.error('API 호출 중 오류 발생:', error);
                    document.getElementById('ai-suggestions').innerText = `오류: ${{error.message}}`;
                }} finally {{
                    // API 호출이 완료되면 로딩 상태를 숨깁니다.
                    document.getElementById('loading').style.display = 'none';
                }}
            }}
            
            // 함수를 즉시 호출합니다.
            fetchAIStrategy();
        """
        
        # HTML 템플릿에 스크립트를 포함하여 전체 파일을 생성합니다.
        html_template = f"""
        <!DOCTYPE html>
        <html lang="ko">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>AI 전략 제안</title>
            <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
            <script src="https://cdn.tailwindcss.com"></script>
            <style>
                body {{
                    font-family: 'Inter', sans-serif;
                    background-color: #f3f4f6;
                    color: #1f2937;
                }}
                .container {{
                    max-width: 800px;
                    margin: 2rem auto;
                    padding: 2rem;
                    background-color: #ffffff;
                    border-radius: 12px;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                }}
                .loading-spinner {{
                    border: 4px solid rgba(0, 0, 0, 0.1);
                    border-left-color: #3b82f6;
                    border-radius: 50%;
                    width: 36px;
                    height: 36px;
                    animation: spin 1s linear infinite;
                    margin: 2rem auto;
                }}
                @keyframes spin {{
                    0% {{ transform: rotate(0deg); }}
                    100% {{ transform: rotate(360deg); }}
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1 class="text-3xl font-bold text-center text-blue-600 mb-6">AI 전략 분석 및 제안</h1>
                <p class="text-center text-gray-600 mb-8">백테스팅 결과를 바탕으로 AI가 새로운 전략을 생성하고 있습니다.</p>
                
                <div id="loading" class="flex justify-center" style="display: none;">
                    <div class="loading-spinner"></div>
                </div>

                <div id="suggestions-container" class="space-y-6" style="display: none;">
                    <h2 class="text-xl font-semibold text-gray-800">AI의 전략 제안:</h2>
                    <div id="ai-suggestions" class="p-4 bg-gray-100 rounded-lg text-gray-700 whitespace-pre-wrap"></div>
                </div>
            </div>
            <script>{fetch_code}</script>
        </body>
        </html>
        """
        
        # HTML 파일을 직접 출력하여 캔버스에 렌더링되도록 합니다.
        print(html_template)
