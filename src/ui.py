"""Module hiển thị giao diện HUD thông tin và hướng dẫn lên khung hình OpenCV.
"""

import cv2
import numpy as np


class HUDDrawer:
    """Lớp vẽ giao diện điều khiển (Heads-Up Display) trực quan trên camera."""

    # Bảng màu (BGR)
    COLOR_BG = (20, 20, 20)
    COLOR_WHITE = (245, 245, 245)
    COLOR_GRAY = (140, 140, 140)
    COLOR_RUN = (50, 205, 50)       # Xanh lá cây (Lime)
    COLOR_JUMP = (0, 215, 255)      # Vàng cam rực rỡ (Gold)
    COLOR_DUCK = (0, 69, 255)       # Đỏ cam (Orange-Red)
    COLOR_CYAN = (255, 215, 0)      # Xanh dương nhạt
    COLOR_ACCENT = (180, 105, 255)  # Hồng tím nhẹ

    def __init__(self):
        self.show_help = False

    def toggle_help(self):
        """Bật/tắt bảng hướng dẫn chi tiết."""
        self.show_help = not self.show_help

    def draw_hud(
        self,
        frame,
        fps: float,
        action: str,
        mode: str,
        finger_count: int,
        fingers_list: list,
        hand_y_ratio: float,
        hand_detected: bool,
    ):
        """Vẽ toàn bộ thông tin trạng thái lên ảnh.

        Args:
            frame: Ảnh BGR.
            fps: Số khung hình trên giây.
            action: "RUN", "JUMP", "DUCK".
            mode: "FINGERS" hoặc "ZONE".
            finger_count: Số ngón đang mở.
            fingers_list: Danh sách [ngón cái, trỏ, giữa, áp út, út].
            hand_y_ratio: Vị trí Y bàn tay (0.0 đến 1.0).
            hand_detected: Có bàn tay hay không.

        Returns:
            frame: Ảnh đã được vẽ HUD.
        """
        h, w, _ = frame.shape

        # 1. Vẽ các vạch ranh giới nếu ở chế độ ZONE
        if mode == "ZONE":
            jump_y = int(h * 0.35)
            duck_y = int(h * 0.65)

            # Vùng JUMP
            cv2.line(frame, (0, jump_y), (w, jump_y), self.COLOR_JUMP, 2)
            cv2.putText(
                frame,
                "JUMP ZONE (Y < 35%)",
                (w - 230, jump_y - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                self.COLOR_JUMP,
                2,
            )

            # Vùng DUCK
            cv2.line(frame, (0, duck_y), (w, duck_y), self.COLOR_DUCK, 2)
            cv2.putText(
                frame,
                "DUCK ZONE (Y > 65%)",
                (w - 230, duck_y + 25),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                self.COLOR_DUCK,
                2,
            )

            # Nếu phát hiện bàn tay, vẽ điểm định vị vị trí Y
            if hand_detected and hand_y_ratio >= 0:
                cur_y = int(hand_y_ratio * h)
                cv2.circle(frame, (w - 30, cur_y), 10, self.COLOR_ACCENT, -1)
                cv2.circle(frame, (w - 30, cur_y), 12, self.COLOR_WHITE, 2)

        # 2. Thanh tiêu đề phía trên (Top HUD Bar)
        # Tạo hiệu ứng nền mờ (Alpha Blending)
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (w, 65), self.COLOR_BG, -1)
        cv2.addWeighted(overlay, 0.75, frame, 0.25, 0, frame)

        # Trạng thái hành động (ACTION)
        action_color = self.COLOR_RUN
        action_text = "RUNNING"
        if action == "JUMP":
            action_color = self.COLOR_JUMP
            action_text = "JUMP  [SPACE]"
        elif action == "DUCK":
            action_color = self.COLOR_DUCK
            action_text = "DUCK  [DOWN]"
        elif not hand_detected:
            action_text = "NO HAND (RUN)"
            action_color = self.COLOR_GRAY

        # Khối màu trạng thái
        cv2.rectangle(frame, (15, 12), (230, 52), action_color, -1)
        cv2.putText(
            frame,
            action_text,
            (25, 41),
            cv2.FONT_HERSHEY_DUPLEX,
            0.7,
            (10, 10, 10),
            2,
        )

        # Chế độ hiện tại (MODE)
        mode_text = f"Mode: {mode}"
        cv2.putText(
            frame,
            mode_text,
            (250, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            self.COLOR_CYAN,
            2,
        )

        # Số ngón tay hoặc thông tin bàn tay
        if hand_detected:
            info_text = f"Fingers: {finger_count}/5"
        else:
            info_text = "Hand: None"
        cv2.putText(
            frame,
            info_text,
            (440, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            self.COLOR_WHITE,
            2,
        )

        # FPS
        fps_text = f"FPS: {int(fps)}"
        cv2.putText(
            frame,
            fps_text,
            (w - 110, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 255, 128),
            2,
        )

        # 3. Thanh phím tắt phía dưới (Bottom Help Bar)
        overlay_bottom = frame.copy()
        cv2.rectangle(overlay_bottom, (0, h - 35), (w, h), self.COLOR_BG, -1)
        cv2.addWeighted(overlay_bottom, 0.8, frame, 0.2, 0, frame)

        footer_text = "[M] Switch Mode   |   [H] Help / Guide   |   [Q / ESC] Quit"
        cv2.putText(
            frame,
            footer_text,
            (20, h - 12),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.48,
            self.COLOR_WHITE,
            1,
        )

        # 4. Bảng hướng dẫn chi tiết (Khi ấn 'H')
        if self.show_help:
            self._draw_help_popup(frame, w, h)

        return frame

    def _draw_help_popup(self, frame, w: int, h: int):
        """Vẽ bảng popup hướng dẫn chi tiết, căn chỉnh tự động theo kích thước khung hình."""
        # Tự động tính kích thước hộp popup tỉ lệ với khung hình để không bao giờ bị tràn
        box_w = min(620, int(w * 0.88))
        box_h = min(410, int(h * 0.86))
        x1 = (w - box_w) // 2
        y1 = (h - box_h) // 2
        x2, y2 = x1 + box_w, y1 + box_h

        # Nền đen trong suốt hiện đại
        overlay = frame.copy()
        cv2.rectangle(overlay, (x1, y1), (x2, y2), (20, 20, 25), -1)
        cv2.addWeighted(overlay, 0.92, frame, 0.08, 0, frame)

        # Viền hộp popup
        cv2.rectangle(frame, (x1, y1), (x2, y2), self.COLOR_CYAN, 2)

        # Tiêu đề
        title = "HUONG DAN CU CHI DIEU KHIEN DINO"
        cv2.putText(
            frame,
            title,
            (x1 + 30, y1 + 36),
            cv2.FONT_HERSHEY_DUPLEX,
            0.62,
            self.COLOR_JUMP,
            2,
        )

        # Đường kẻ phân cách dưới tiêu đề
        cv2.line(frame, (x1 + 25, y1 + 48), (x2 - 25, y1 + 48), self.COLOR_GRAY, 1)

        # Nội dung hướng dẫn
        lines = [
            ("CHE DO 1: FINGERS (So ngon tay - Khuyen dung):", self.COLOR_ACCENT, 0.48, 1),
            ("   + Xoe 4 - 5 ngon        -> NHAY (Phim Space)", self.COLOR_JUMP, 0.45, 1),
            ("   + Nam chat tay (0 ngon)  -> CUI (Mui ten Xuong)", self.COLOR_DUCK, 0.45, 1),
            ("   + 1 - 3 ngon / Tha long  -> CHAY (Tha phim)", self.COLOR_WHITE, 0.45, 1),
            ("", self.COLOR_WHITE, 0.45, 1),
            ("CHE DO 2: ZONE (Vi tri cao/thap cua ban tay):", self.COLOR_ACCENT, 0.48, 1),
            ("   + Dua tay len cao        -> NHAY (Space)", self.COLOR_JUMP, 0.45, 1),
            ("   + Ha tay xuong thap      -> CUI (Down)", self.COLOR_DUCK, 0.45, 1),
            ("   + Tay o vung giua        -> CHAY BINH THUONG", self.COLOR_WHITE, 0.45, 1),
            ("", self.COLOR_WHITE, 0.45, 1),
            ("MEO: Mo Chrome go 'chrome://dino', click vao trang de choi!", (100, 240, 255), 0.45, 1),
        ]

        curr_y = y1 + 75
        for text, color, scale, thickness in lines:
            if text:
                cv2.putText(
                    frame,
                    text,
                    (x1 + 30, curr_y),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    scale,
                    color,
                    thickness,
                )
            curr_y += 24

        # Nút hướng dẫn đóng ở chân popup
        close_bar_y1 = y2 - 38
        close_bar_y2 = y2 - 8
        cv2.rectangle(frame, (x1 + 20, close_bar_y1), (x2 - 20, close_bar_y2), (40, 40, 50), -1)
        cv2.rectangle(frame, (x1 + 20, close_bar_y1), (x2 - 20, close_bar_y2), self.COLOR_GRAY, 1)
        cv2.putText(
            frame,
            "[ H ]  Nhan phim 'H' tren ban phim de dong bang huong dan nay",
            (x1 + 45, close_bar_y2 - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.45,
            (0, 255, 128),
            1,
        )
