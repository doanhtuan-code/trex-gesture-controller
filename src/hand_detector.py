"""Module phát hiện bàn tay và nhận diện ngón tay sử dụng MediaPipe & OpenCV.
"""

import math
import cv2
import mediapipe as mp


class HandDetector:
    """Lớp xử lý phát hiện bàn tay, trích xuất landmarks và đếm số ngón tay."""

    def __init__(
        self,
        mode: bool = False,
        max_hands: int = 1,
        detection_confidence: float = 0.7,
        tracking_confidence: float = 0.5,
    ):
        """Khởi tạo HandDetector với MediaPipe Hands.

        Args:
            mode: False cho video streaming (nhanh hơn), True cho ảnh tĩnh.
            max_hands: Số lượng bàn tay tối đa cần theo dõi (mặc định 1 để tối ưu hiệu năng).
            detection_confidence: Ngưỡng tự tin phát hiện (0.0 - 1.0).
            tracking_confidence: Ngưỡng tự tin theo dõi (0.0 - 1.0).
        """
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=mode,
            max_num_hands=max_hands,
            min_detection_confidence=detection_confidence,
            min_tracking_confidence=tracking_confidence,
        )
        self.mp_draw = mp.solutions.drawing_utils
        self.mp_draw_styles = mp.solutions.drawing_styles

        # Danh sách ID đỉnh của 4 ngón (Trỏ, Giữa, Áp út, Út)
        self.tip_ids = [8, 12, 16, 20]
        # ID khớp PIP tương ứng để so sánh mở/đóng
        self.pip_ids = [6, 10, 14, 18]

        self.results = None

    def find_hands(self, frame, draw: bool = True):
        """Xử lý frame để phát hiện bàn tay và vẽ khung xương nếu draw=True.

        Args:
            frame: Ảnh BGR từ OpenCV webcam.
            draw: Vẽ landmark và đường nối bàn tay lên ảnh hay không.

        Returns:
            frame: Ảnh đã được vẽ (nếu draw=True).
        """
        # Chuyển BGR sang RGB cho MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb_frame.flags.writeable = False
        self.results = self.hands.process(rgb_frame)
        rgb_frame.flags.writeable = True

        if self.results.multi_hand_landmarks and draw:
            for hand_lms in self.results.multi_hand_landmarks:
                self.mp_draw.draw_landmarks(
                    frame,
                    hand_lms,
                    self.mp_hands.HAND_CONNECTIONS,
                    self.mp_draw.DrawingSpec(color=(0, 255, 128), thickness=2, circle_radius=3),
                    self.mp_draw.DrawingSpec(color=(255, 200, 0), thickness=2),
                )
        return frame

    def find_positions(self, frame, hand_idx: int = 0):
        """Lấy danh sách tọa độ (id, x, y, z) của 21 điểm landmark trên bàn tay.

        Args:
            frame: Ảnh đầu vào để tính kích thước pixel.
            hand_idx: Chỉ số bàn tay cần lấy (0 là bàn tay đầu tiên).

        Returns:
            lm_list: Danh sách 21 phần tử dạng [id, x_pixel, y_pixel, z_norm].
                     Trả về rỗng [] nếu không tìm thấy bàn tay.
        """
        lm_list = []
        if self.results and self.results.multi_hand_landmarks:
            if hand_idx < len(self.results.multi_hand_landmarks):
                my_hand = self.results.multi_hand_landmarks[hand_idx]
                h, w, _ = frame.shape
                for idx, lm in enumerate(my_hand.landmark):
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    lm_list.append([idx, cx, cy, lm.z])
        return lm_list

    def get_handedness(self, hand_idx: int = 0) -> str:
        """Lấy nhãn tay ('Left' hoặc 'Right')."""
        if self.results and self.results.multi_handedness:
            if hand_idx < len(self.results.multi_handedness):
                return self.results.multi_handedness[hand_idx].classification[0].label
        return "Unknown"

    def count_fingers(self, lm_list, handedness: str = "Right"):
        """Đếm số ngón tay đang mở dựa trên vị trí landmark.

        Args:
            lm_list: Danh sách tọa độ từ `find_positions`.
            handedness: 'Left' hoặc 'Right'.

        Returns:
            fingers: List 5 số [ngón cái, trỏ, giữa, áp út, út] (1: mở, 0: đóng).
            total: Tổng số ngón đang mở (0 đến 5).
        """
        if not lm_list or len(lm_list) < 21:
            return [], 0

        fingers = []

        # 1. Kiểm tra Ngón Cái (Thumb: Tip=4, IP=3, MCP=2, Pinky_MCP=17)
        # Sử dụng khoảng cách hình học từ đỉnh ngón cái (4) đến gốc ngón út (17)
        # Khi ngón cái xòe ra, khoảng cách này tăng đáng kể so với khi khép lại
        thumb_tip = lm_list[4]
        thumb_mcp = lm_list[2]
        pinky_mcp = lm_list[17]

        dist_tip_pinky = math.hypot(thumb_tip[1] - pinky_mcp[1], thumb_tip[2] - pinky_mcp[2])
        dist_mcp_pinky = math.hypot(thumb_mcp[1] - pinky_mcp[1], thumb_mcp[2] - pinky_mcp[2])

        # Ngón cái được tính là mở nếu khoảng cách đỉnh tới gốc ngón út > 1.25 lần gốc ngón cái
        if dist_tip_pinky > dist_mcp_pinky * 1.25:
            fingers.append(1)
        else:
            fingers.append(0)

        # 2. Kiểm tra 4 ngón còn lại (Trỏ, Giữa, Áp út, Út)
        # Nếu tọa độ Y của Tip nhỏ hơn tọa độ Y của PIP thì ngón tay đang giơ lên (ảnh gốc có Y tăng dần từ trên xuống dưới)
        for tip_id, pip_id in zip(self.tip_ids, self.pip_ids):
            if lm_list[tip_id][2] < lm_list[pip_id][2]:
                fingers.append(1)
            else:
                fingers.append(0)

        return fingers, sum(fingers)

    def get_hand_center_y_ratio(self, lm_list, frame_height: int) -> float:
        """Tính tỉ lệ vị trí Y của trọng tâm bàn tay (0.0 ở mép trên, 1.0 ở mép dưới).

        Args:
            lm_list: Danh sách landmarks.
            frame_height: Chiều cao khung hình (pixel).

        Returns:
            Tỉ lệ Y từ 0.0 đến 1.0, hoặc -1.0 nếu không có bàn tay.
        """
        if not lm_list or len(lm_list) < 21:
            return -1.0

        # Lấy tọa độ Y của cổ tay (0) và gốc ngón giữa (9) để tính tâm bàn tay
        wrist_y = lm_list[0][2]
        middle_mcp_y = lm_list[9][2]
        center_y = (wrist_y + middle_mcp_y) / 2.0
        return max(0.0, min(1.0, center_y / frame_height))
