"""Module giả lập bàn phím điều khiển trò chơi Khủng long (Chrome Dino).
Hỗ trợ phím Space (Nhảy), Down Arrow (Cúi) và trạng thái Chạy bình thường.
"""

import time
import pyautogui

# Tắt thời gian chờ nhân tạo của PyAutoGUI để đạt độ phản hồi tức thì
pyautogui.PAUSE = 0.0
# Tắt FailSafe để tránh lỗi khi con trỏ chuột vô tình ở góc màn hình
pyautogui.FAILSAFE = False


class DinoController:
    """Lớp quản lý trạng thái và mô phỏng phím bấm cho Chrome Dino."""

    # Các chế độ điều khiển
    MODE_FINGERS = "FINGERS"  # Điều khiển bằng số ngón tay
    MODE_ZONE = "ZONE"        # Điều khiển bằng vị trí bàn tay (trên/dưới)

    def __init__(self, mode: str = MODE_FINGERS):
        """Khởi tạo bộ điều khiển.

        Args:
            mode: MODE_FINGERS hoặc MODE_ZONE.
        """
        self.mode = mode
        self.current_action = "RUN"  # "RUN", "JUMP", "DUCK"
        self.is_space_down = False
        self.is_down_down = False

        # Thời gian bắt đầu giữ phím Space (để tự động nhả tránh kẹt phím)
        self.jump_start_time = 0.0
        self.max_jump_hold_sec = 0.35  # Thời gian nhảy tối đa của T-Rex

    def toggle_mode(self) -> str:
        """Chuyển đổi qua lại giữa 2 chế độ điều khiển."""
        self.release_all()
        if self.mode == self.MODE_FINGERS:
            self.mode = self.MODE_ZONE
        else:
            self.mode = self.MODE_FINGERS
        return self.mode

    def process_input(self, finger_count: int, hand_y_ratio: float, hand_detected: bool) -> str:
        """Nhận diện hành động tương ứng từ dữ liệu bàn tay và thực hiện bấm phím.

        Args:
            finger_count: Số ngón tay đang mở (0 đến 5).
            hand_y_ratio: Vị trí Y của bàn tay (0.0 đến 1.0).
            hand_detected: Có bàn tay trong khung hình hay không.

        Returns:
            action: Hành động hiện tại ("RUN", "JUMP", "DUCK").
        """
        if not hand_detected:
            # Không có bàn tay -> Chạy bình thường, nhả mọi phím
            self.update_action("RUN")
            return "RUN"

        action = "RUN"

        if self.mode == self.MODE_FINGERS:
            # --- Chế độ 1: Dựa trên số ngón tay ---
            # 🖐️ Xòe cả bàn tay (>= 4 ngón): NHẢY (Space)
            if finger_count >= 4:
                action = "JUMP"
            # ✊ Nắm đấm (0 ngón): CÚI (Mũi tên xuống)
            elif finger_count == 0:
                action = "DUCK"
            # ✌️/☝️ 1 đến 3 ngón (hoặc trạng thái thả lỏng): CHẠY (Không bấm phím)
            else:
                action = "RUN"

        elif self.mode == self.MODE_ZONE:
            # --- Chế độ 2: Dựa trên vị trí cao/thấp của bàn tay ---
            # Vùng trên (Y < 0.35): NHẢY
            if hand_y_ratio < 0.35:
                action = "JUMP"
            # Vùng dưới (Y > 0.65): CÚI
            elif hand_y_ratio > 0.65:
                action = "DUCK"
            # Vùng giữa (0.35 <= Y <= 0.65): CHẠY
            else:
                action = "RUN"

        self.update_action(action)
        return action

    def update_action(self, new_action: str):
        """Cập nhật trạng thái và kích hoạt phím bấm tương ứng một cách mượt mà."""
        now = time.time()

        # Xử lý tự động nhả phím Space nếu giữ quá lâu
        if self.is_space_down and (now - self.jump_start_time > self.max_jump_hold_sec):
            pyautogui.keyUp("space")
            self.is_space_down = False

        # Nếu không đổi hành động
        if new_action == self.current_action:
            return

        # Khi chuyển trạng thái:
        if new_action == "JUMP":
            # Nhả phím Cúi nếu đang bấm
            if self.is_down_down:
                pyautogui.keyUp("down")
                self.is_down_down = False
            # Bấm phím Nhảy (Space)
            if not self.is_space_down:
                pyautogui.keyDown("space")
                self.is_space_down = True
                self.jump_start_time = now

        elif new_action == "DUCK":
            # Nhả phím Nhảy nếu đang bấm
            if self.is_space_down:
                pyautogui.keyUp("space")
                self.is_space_down = False
            # Giữ phím Cúi (Down Arrow)
            if not self.is_down_down:
                pyautogui.keyDown("down")
                self.is_down_down = True

        elif new_action == "RUN":
            # Nhả cả 2 phím để chạy tự nhiên
            if self.is_space_down:
                pyautogui.keyUp("space")
                self.is_space_down = False
            if self.is_down_down:
                pyautogui.keyUp("down")
                self.is_down_down = False

        self.current_action = new_action

    def release_all(self):
        """Nhả toàn bộ phím bấm để tránh kẹt phím khi thoát hoặc chuyển chế độ."""
        if self.is_space_down:
            try:
                pyautogui.keyUp("space")
            except Exception:
                pass
            self.is_space_down = False

        if self.is_down_down:
            try:
                pyautogui.keyUp("down")
            except Exception:
                pass
            self.is_down_down = False

        self.current_action = "RUN"
