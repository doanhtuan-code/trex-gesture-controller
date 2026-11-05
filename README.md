# 🦖 Chrome T-Rex Gesture Controller

> Bộ điều khiển trò chơi Khủng long của Google Chrome (**T-Rex Run**) hoàn toàn bằng cử chỉ bàn tay qua Camera sử dụng **OpenCV**, **MediaPipe** và **PyAutoGUI**.

---

## 📖 Giới thiệu

Dự án này sử dụng thị giác máy tính (Computer Vision) để nhận diện bàn tay theo thời gian thực và mô phỏng 2 phím bấm quan trọng nhất để chơi trò chơi khủng long kinh điển của Google Chrome:
- 🚀 **Phím Space**: Nhảy vượt chướng ngại vật (cây xương rồng, chim tầm thấp).
- 🛡️ **Phím Mũi tên xuống (Down Arrow)**: Cúi người né chim bay tầm trung/cao và hạ cánh nhanh khi đang nhảy.

Chương trình được thiết kế đơn giản, phân tách mô-đun rõ ràng, độ trễ cực thấp (phản hồi tức thì) và có giao diện hiển thị (HUD) trực quan trên camera.

---

## 🖐️ Bảng quy ước cử chỉ (Gesture Mapping)

Hệ thống hỗ trợ **2 chế độ điều khiển linh hoạt** (nhấn phím `M` trên bàn phím để chuyển đổi qua lại bất kỳ lúc nào):

### Chế độ 1: Đếm số ngón tay (`FINGERS` - Mặc định & Trực quan nhất)

| Cử chỉ | Hình ảnh mô phỏng | Phím bấm giả lập | Hành động trong Game |
| :--- | :---: | :---: | :--- |
| **Xòe bàn tay** (4 - 5 ngón) | 🖐️ | `Space` | **Nhảy lên (Jump)** |
| **Nắm chặt bàn tay** (0 ngón) | ✊ | `Down Arrow` (Mũi tên xuống) | **Cúi rạp người (Duck / Crouch)** |
| **Thả lỏng / Giơ 1-2 ngón** | ✌️ / ☝️ | *Thả tất cả phím* | **Chạy bình thường (Run)** |

> 💡 **Mẹo:** Khi không đưa tay vào khung hình camera, chương trình sẽ tự động đưa khủng long về trạng thái **Chạy bình thường**, đảm bảo không bị kẹt phím.

---

### Chế độ 2: Vị trí bàn tay (`ZONE`)

Màn hình camera được chia làm 3 phân vùng dọc:
- **Vùng trên (Y < 35%):** Bàn tay giơ lên cao $\rightarrow$ Kích hoạt **Nhảy** (`Space`).
- **Vùng giữa (35% $\le$ Y $\le$ 65%):** Bàn tay ở giữa $\rightarrow$ **Chạy bình thường** (Thả phím).
- **Vùng dưới (Y > 65%):** Bàn tay hạ xuống thấp $\rightarrow$ Kích hoạt **Cúi** (`Down Arrow`).

---

## ⌨️ Phím tắt điều khiển cửa sổ Camera

| Phím tắt | Chức năng |
| :---: | :--- |
| `M` / `m` | Chuyển đổi qua lại giữa chế độ **FINGERS** và **ZONE** |
| `H` / `h` | Bật / tắt bảng hướng dẫn chi tiết ngay trên màn hình |
| `Q` / `q` hoặc `ESC` | Thoát chương trình an toàn (tự động nhả mọi phím bấm) |

---

## 🛠️ Yêu cầu hệ thống & Cài đặt

### 1. Yêu cầu tiên quyết
- **Hệ điều hành:** Windows, macOS hoặc Linux.
- **Python:** Phiên bản 3.10, 3.11 hoặc 3.12 (Khuyến nghị **Python 3.12**).
- **Webcam:** 1 webcam đang hoạt động bình thường.

### 2. Cài đặt môi trường ảo (Khuyến khích)

Mở Terminal hoặc PowerShell tại thư mục dự án và chạy:

```bash
# Tạo môi trường ảo
python -m venv venv

# Kích hoạt môi trường ảo:
# Trên Windows PowerShell:
.\venv\Scripts\Activate.ps1

# Trên Windows CMD:
.\venv\Scripts\activate.bat

# Trên Linux / macOS:
source venv/bin/activate
```

### 3. Cài đặt các thư viện cần thiết

```bash
pip install -r requirements.txt
```

Các thư viện chính bao gồm:
- `opencv-contrib-python`: Xử lý hình ảnh từ webcam và hiển thị giao diện.
- `mediapipe`: Nhận diện 21 điểm khớp bàn tay (Hand Landmarks).
- `pyautogui`: Giả lập phím bấm bàn phím thời gian thực.
- `numpy`: Xử lý mảng hình ảnh.

---

## 🎮 Hướng dẫn chơi Game

1. **Khởi chạy chương trình:**
   ```bash
   python main.py
   ```
2. **Mở trò chơi Khủng long:**
   - Trên trình duyệt **Google Chrome**: Mở một tab mới và nhập địa chỉ:
     ```text
     chrome://dino
     ```
   - *Nếu không dùng Chrome hoặc muốn chơi trực tuyến*, bạn có thể vào: [https://elgoog.im/t-rex/](https://elgoog.im/t-rex/)
3. **Bắt đầu chơi:**
   - Đặt cửa sổ game Chrome và cửa sổ camera song song nhau.
   - Click chuột vào trang game Chrome để trang nhận tiêu điểm (focus).
   - Xòe bàn tay trước camera $\rightarrow$ Khủng long sẽ nhảy lên để bắt đầu trò chơi!
   - Nắm đấm để cúi né các chú chim bay tầm thấp.

---

## 📁 Cấu trúc thư mục dự án

```text
trex-gesture-controller/
├── src/
│   ├── __init__.py           # Khởi tạo gói module
│   ├── hand_detector.py      # Module bọc MediaPipe: nhận diện 21 điểm mốc & đếm ngón tay
│   ├── controller.py         # Module điều khiển bàn phím (PyAutoGUI) & quản lý trạng thái
│   └── ui.py                 # Module vẽ giao diện HUD (trạng thái, FPS, vạch ranh giới, bảng trợ giúp)
├── .gitignore                # Bỏ qua các file rác, cache, virtualenv khi commit git
├── main.py                   # Điểm khởi chạy chương trình chính (Camera loop)
├── README.md                 # Tài liệu hướng dẫn sử dụng chi tiết
└── requirements.txt          # Danh sách thư viện và phiên bản phụ thuộc
```

---

## 🚀 Hướng dẫn Git: Commit từng phần & Push lên GitHub

Dưới đây là các bước commit chuẩn hóa theo từng phần tính năng và đẩy code lên kho lưu trữ GitHub của bạn:

### Bước 1: Kiểm tra trạng thái hiện tại
```bash
git status
```

### Bước 2: Commit từng phần theo tính năng

```bash
# 1. Commit cấu hình dự án (.gitignore và requirements.txt)
git add .gitignore requirements.txt
git commit -m "chore: setup project configuration and dependencies"

# 2. Commit module nhận diện bàn tay MediaPipe
git add src/__init__.py src/hand_detector.py
git commit -m "feat: implement hand detection and finger counting using mediapipe"

# 3. Commit module điều khiển bàn phím PyAutoGUI
git add src/controller.py
git commit -m "feat: implement keyboard controller for Space and Down Arrow"

# 4. Commit module giao diện HUD và chương trình chính main.py
git add src/ui.py main.py
git commit -m "feat: complete main camera loop with real-time HUD interface"

# 5. Commit tài liệu hướng dẫn README.md
git add README.md
git commit -m "docs: add comprehensive documentation and usage guide"
```

### Bước 3: Đẩy (Push) lên GitHub
```bash
git push -u origin main
```

*(Nếu gặp yêu cầu đăng nhập, hãy đăng nhập qua trình duyệt hoặc Personal Access Token của GitHub).*
