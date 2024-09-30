from flask import Flask, jsonify, request
import cv2
import os
from time import sleep
app = Flask(__name__)


# 모든 책 목록 조회(GET)
@app.route('/books1', methods=['GET'])
def get_books1():
    suntracking()
    return '', 204

@app.route('/books2', methods=['GET'])
def get_books2():
    return jsonify(tracking)



# 새로운 책 추가(POST)
@app.route('/books', methods=['POST'])
def add_books():
    new_book = request.get_json()
    books.append(new_book)
    return jsonify(new_book), 201

#책 정보 업데이트(PUT)
@app.route('/books/<int:id>', methods=['PUT'])
def update_books(id):
    # ID로 책 찾기
    book = next((b for b in books if b['id'] == id), None)

    if book:
        # 요청 바디에서 JSON 데이터 가져오기
        data = request.get_json()
        # 책 정보 업데이트a
        book.update(data)
        return jsonify(book)
    # 책을 찾지 못한 경우 404 상태 코드 변환
    return jsonify({'error': 'Book not found'}), 404


# 책 삭제 (DELETE)
@app.route('/books/<int:id>', methods=['DELETE'])
def delete_books(id):
    global books
    # 해당 ID의 책을 리스트에서 제거
    books = [b for b in books if b['id'] != id]
    # 204 상태 코드 반환 (콘텐츠 없음)
    return '', 204

def suntracking():
    print("SUNTRACKING")
    # 비디오 캡처 객체 생성
    cap = cv2.VideoCapture('annesa1.mp4')

    # 배경 제거 객체 생성
    fgbg = cv2.createBackgroundSubtractorMOG2(history=500, varThreshold=16, detectShadows=True)

    frame_count = 0

    output_folder = 'captured_images'
    os.makedirs(output_folder, exist_ok=True)  # 폴더가 없으면 생성

    while cap.isOpened():
        sleep(0.01)
        x1 = 0
        ret, frame = cap.read()
        if not ret:
            break
        # # 전체 이미지 캡처 및 저장
        # cv2.imwrite(os.path.join(output_folder, f'{frame_count}.jpg'), frame)  # 특정 폴더에 전체 프레임 저장
        # frame_count += 1  # 프레임 카운터 증가

        # 배경 제거 적용하여 모션 감지
        fgmask = fgbg.apply(frame)

        # 잡음 제거를 위한 이진화 및 모폴로지 연산
        _, thresh = cv2.threshold(fgmask, 244, 255, cv2.THRESH_BINARY)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

        # 윤곽선 검출
        contours, _ = cv2.findContours(cleaned, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for contour in contours:
            # 작은 잡음을 무시하기 위한 조건
            if cv2.contourArea(contour) < 500:
                continue
            # 객체에 사각형 그리기
            x, y, w, h = cv2.boundingRect(contour)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            if 0 <= x < 286:
                x1 = 1

            elif 286 <= x < 572:
                x1 = 2

            elif 572 <= x < 858:
                x1 = 4

            elif 858 <= x < 1144:
                x1 = 32

            else:
                x1 = 64


        # 결과 출력
        cv2.imshow('Motion Detection', frame)
        # 전체 이미지 캡처 및 저장
        cv2.imwrite(os.path.join(output_folder, 'captured_image.jpg'), frame)  # 특정 폴더에 전체 프레임 저장
        frame_count += 1  # 프레임 카운터 증가
        # 'q' 키를 누르면 종료
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    # 디버그 모드로 애플리케이션 실행
    app.run(debug=True)



