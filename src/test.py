import time
from flask import Flask, jsonify
import cv2
import os
from time import sleep
from threading import Thread

app = Flask(__name__)

sun_coordinates = (0, 0)  # 초기 좌표 설정
last_print_time = time.time()  # 마지막 출력 시간 초기화
running = True  # 추적을 위한 상태 변수

@app.route('/sun_coordinates', methods=['GET'])  # 데이터를 확인하는 URL
def get_sun_coordinates():
    return jsonify({'coordinates': sun_coordinates})

def suntracking():  # 비디오 시작하는 함수
    global sun_coordinates,last_print_time, running
    print("SUNTRACKING")
    cap = cv2.VideoCapture('../video/annesa1.mp4')
    fgbg = cv2.createBackgroundSubtractorMOG2(history=500, varThreshold=16, detectShadows=True)

    while running and cap.isOpened():
        sleep(0.01)
        ret, frame = cap.read()
        if not ret:
            break

        fgmask = fgbg.apply(frame)
        _, thresh = cv2.threshold(fgmask, 244, 255, cv2.THRESH_BINARY)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

        contours, _ = cv2.findContours(cleaned, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for contour in contours:
            if cv2.contourArea(contour) < 500:
                continue
            x, y, w, h = cv2.boundingRect(contour)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            # 태양의 중심 좌표 업데이트
            sun_coordinates = (x + w // 2, y + h // 2)

        # 출력 간격 조정
        current_time = time.time()
        if current_time - last_print_time > 1:  # 1초마다 출력
            print(f"Sun Coordinates: {sun_coordinates}")
            last_print_time = current_time  # 마지막 출력 시간 업데이트

        cv2.imshow('Motion Detection', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    # 태양 추적 스레드 시작
    Thread(target=suntracking).start()
    # REST API 서버 실행
    app.run(host='0.0.0.0', port=5000)
