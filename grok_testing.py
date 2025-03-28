import requests
from flask import Flask, request, jsonify
import os

API_KEY = os.getenv("CLOVA_API_KEY")  # 또는 config.json에서 가져옴

print(f"현재 사용 중인 API 키: {API_KEY}")  # 이걸 추가해서 API 키가 제대로 불러와지는지 확인


app = Flask(__name__)

# CLOVA X 설정
CLOVA_X_URL = ''
CLOVA_X_API_KEY = ''  # 실제 키로 교체
CLOVA_X_APP_ID = ''    # 실제 ID로 교체



# CLOVA X API 호출 함수
def call_clova_x_chatbot(user_input):
    headers = {
        'Content-Type': 'application/json; charset=UTF-8',
        'X-NCP-APIGW-API-KEY': CLOVA_X_API_KEY,
        'X-NCP-CLOVASTUDIO-API-KEY': CLOVA_X_APP_ID
    }
    
    preset_text = [
        {"role": "system", "content": "친절한 의사처럼 사용자의 증상을 듣고 공감하며 위로한 뒤, 적절한 진료과를 안내하세요. 의학적 정확성을 유지하고, 병원 방문을 권장하며 따뜻하게 마무리하세요. 사용자가 증상을 명확히 말하지 않으면 자연스럽게 증상을 물어보세요."},
        {"role": "user", "content": user_input}
    ]
    
    payload = {
        'messages': preset_text,
        'maxTokens': 256,
        'temperature': 0.5
    }

    try:
        response = requests.post(CLOVA_X_URL, headers=headers, json=payload)
        print(f"상태 코드: {response.status_code}")
        print(f"CLOVA X 응답: {response.text}")
        if response.status_code == 200:
            json_data = response.json()
            return json_data['result']['message']['content']
        return f"CLOVA X 응답 실패: {response.status_code} - {response.text}"
    except Exception as e:
        print(f"CLOVA X 호출 중 오류: {str(e)}")
        return f"API 호출 중 오류 발생: {str(e)}"

# 기본 경로 (테스트용)
@app.route('/', methods=['GET'])
def home():
    return "Medical Advice Bot 서버가 실행 중입니다! 카카오톡에서 자유롭게 증상을 말해보세요."

# 카카오톡 스킬 엔드포인트
@app.route('/skill', methods=['POST'])
def skill():
    try:
        data = request.get_json()
        print(f"수신된 요청: {data}")
        user_input = data.get('userRequest', {}).get('utterance', '').strip()

        if not user_input:
            response_text = "어떤 도움을 드릴까요? 증상을 말씀해 주세요!"
        else:
            # "아파 " 조건 제거, 모든 입력을 CLOVA X로 처리
            response_text = call_clova_x_chatbot(user_input)

        response = {
            "version": "2.0",
            "template": {
                "outputs": [{"simpleText": {"text": response_text}}]
            }
        }
        print(f"응답 준비: {response}")
        return jsonify(response)
    except Exception as e:
        print(f"스킬 처리 중 오류: {str(e)}")
        return jsonify({
            "version": "2.0",
            "template": {
                "outputs": [{"simpleText": {"text": f"서버 오류: {str(e)}"}}]
            }
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)