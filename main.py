"""Điểm khởi chạy chương trình điều khiển Chrome Dino bằng cử chỉ tay.
Sử dụng OpenCV + MediaPipe để nhận diện cử chỉ từ Camera và mô phỏng phím Space, Down Arrow.
"""

import sys
import time
import cv2

from src.hand_detector import HandDetector
from src.controller import DinoController
from src.ui import HUDDrawer


def main():
    print("=" * 60)
    print(" 🦖 CHROME T-REX RUN GESTURE CONTROLLER 🦖 ")
    print("=" * 60)
    print("Đang khởi tạo Camera và mô hình MediaPipe Hands...")

    # Khởi tạo Camera (Chỉ số 0 là camera mặc định)
    camera_idx = 0
    cap = cv2.VideoCapture(camera_idx)

    # Đặt độ phân giải tối ưu để đạt FPS cao và mượt mà
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    if not cap.isOpened():
        print(f"[LỖI] Không thể kết nối với Camera (index={camera_idx}).")
        print("Vui lòng kiểm tra lại webcam hoặc quyền truy cập camera!")
        sys.exit(1)

    print("[OK] Kết nối Camera thành công!")
    print("-" * 60)
    print("HƯỚNG DẪN CỬ CHỈ:")
    print("  • Chế độ FINGERS (Mặc định):")
    print("      🖐️  Xòe 4 - 5 ngón  ->  NHẢY  (Phím Space)")
    print("      ✊  Nắm đấm (0 ngón) ->  CÚI   (Phím Mũi tên Xuống)")
    print("      ✌️   1 - 3 ngón       ->  CHẠY  (Thả phím)")
    print("  • Phím tắt điều khiển cửa sổ:")
    print("      [M] Chuyển đổi chế độ (Ngón tay <-> Vị trí bàn tay)")
    print("      [H] Bật/tắt hướng dẫn trực tiếp trên màn hình")
    print("      [Q] hoặc [ESC] để Thoát chương trình")
    print("-" * 60)
    print("Mở Google Chrome, truy cập: chrome://dino để bắt đầu chơi!")
    print("=" * 60)

    # Khởi tạo các thành phần xử lý
    detector = HandDetector(
        mode=False,
        max_hands=1,
        detection_confidence=0.7,
        tracking_confidence=0.5,
    )
    controller = DinoController(mode=DinoController.MODE_FINGERS)
    hud = HUDDrawer()

    prev_time = time.time()
    fps = 0.0

    try:
        while True:
            success, frame = cap.read()
            if not success or frame is None:
                print("[CẢNH BÁO] Không đọc được frame từ camera. Đang thử lại...")
                time.sleep(0.05)
                continue

            # Lật ảnh theo chiều ngang (Mirror effect) để cử chỉ trực quan như soi gương
            frame = cv2.flip(frame, 1)
            h, w, _ = frame.shape

            # 1. Phát hiện bàn tay và vẽ khung xương
            frame = detector.find_hands(frame, draw=True)

            # 2. Lấy tọa độ các điểm landmarks
            lm_list = detector.find_positions(frame, hand_idx=0)
            hand_detected = len(lm_list) >= 21

            finger_count = 0
            fingers_list = []
            hand_y_ratio = -1.0

            if hand_detected:
                handedness = detector.get_handedness(hand_idx=0)
                fingers_list, finger_count = detector.count_fingers(lm_list, handedness=handedness)
                hand_y_ratio = detector.get_hand_center_y_ratio(lm_list, frame_height=h)

            # 3. Xử lý logic cử chỉ và mô phỏng phím bấm
            action = controller.process_input(
                finger_count=finger_count,
                hand_y_ratio=hand_y_ratio,
                hand_detected=hand_detected,
            )

            # 4. Tính toán FPS
            curr_time = time.time()
            fps_val = 1.0 / (curr_time - prev_time) if (curr_time - prev_time) > 0 else 30.0
            fps = 0.9 * fps + 0.1 * fps_val  # Exponential smoothing
            prev_time = curr_time

            # 5. Vẽ giao diện HUD lên khung hình
            frame = hud.draw_hud(
                frame=frame,
                fps=fps,
                action=action,
                mode=controller.mode,
                finger_count=finger_count,
                fingers_list=fingers_list,
                hand_y_ratio=hand_y_ratio,
                hand_detected=hand_detected,
            )

            # 6. Hiển thị cửa sổ OpenCV
            cv2.imshow("Chrome Dino Gesture Controller", frame)

            # 7. Bắt phím bấm điều khiển từ người dùng
            key = cv2.waitKey(1) & 0xFF
            if key in [ord("q"), ord("Q"), 27]:  # 'q' hoặc ESC để thoát
                print("\n[THOÁT] Đang tắt chương trình...")
                break
            elif key in [ord("m"), ord("M")]:    # 'm' đổi chế độ
                new_mode = controller.toggle_mode()
                print(f"[CHẾ ĐỘ] Đã chuyển sang chế độ: {new_mode}")
            elif key in [ord("h"), ord("H")]:    # 'h' xem trợ giúp
                hud.toggle_help()

    except KeyboardInterrupt:
        print("\n[NGẮT] Đã nhận tín hiệu dừng từ bàn phím (Ctrl+C).")

    finally:
        # Giải phóng tài nguyên và bảo đảm không bị kẹt phím
        controller.release_all()
        cap.release()
        cv2.destroyAllWindows()
        print("[HOÀN TẤT] Đã giải phóng Camera và phím bấm an toàn.")


if __name__ == "__main__":
    main()
