# capture_service_daily.py
# 一日一回カメラで撮影し、画像を保存してデータベースに記録するスクリプト

import sqlite3     # SQLiteデータベース操作用
import os          # ファイルやディレクトリの操作用
import cv2         # OpenCV（カメラ操作・画像保存用）
from datetime import datetime  # 撮影時刻を取得するため
import time        # スリープ（待機）処理用
import pathlib     # ディレクトリ作成などの高レベルファイル操作
import sys         # システム終了などの処理用

# --- 設定値 ---
DB_PATH = "captures.db"                 # データベースファイルのパス
IMAGES_DIR = "images"                   # 撮影画像を保存するフォルダ
SLEEP_INTERVAL_SECONDS = 24 * 60 * 60   # 一日ごとの待機時間（86400秒）
CAMERA_INDEX = 0                        # 使用するカメラ番号（通常は0）


def ensure_db_exists():
    """データベースファイルが存在するか確認し、なければ終了する"""
    if not os.path.exists(DB_PATH):
        print(f"Database '{DB_PATH}' not found. Please run 'python init_db.py' first.")
        sys.exit(1)  # ファイルがない場合はエラーメッセージを出して終了


def capture_image(camera_index=CAMERA_INDEX):
    """カメラを起動して1枚撮影し、画像データ（frame）を返す"""
    cap = cv2.VideoCapture(camera_index)     # カメラデバイスを開く
    if not cap.isOpened():                   # カメラが開けなければエラー
        cap.release()
        raise RuntimeError(f"Cannot open camera index {camera_index}")
    time.sleep(0.2)                          # カメラ起動の安定化待ち
    ret, frame = cap.read()                  # 映像を1フレーム取得
    cap.release()                            # カメラを解放
    if not ret or frame is None:             # 撮影に失敗した場合
        raise RuntimeError("Failed to read frame from camera")
    return frame                             # 撮影した画像データを返す


def save_image(frame):
    """撮影した画像をファイルに保存し、その絶対パスを返す"""
    pathlib.Path(IMAGES_DIR).mkdir(parents=True, exist_ok=True)  # 保存先フォルダを作成（なければ自動作成）
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")                # 現在時刻をファイル名用にフォーマット
    filename = f"{ts}.jpg"                                       # 例: "20251105_090001.jpg"
    path = os.path.join(IMAGES_DIR, filename)                    # 保存先パスを生成
    success = cv2.imwrite(path, frame)                           # 画像をJPEG形式で保存
    if not success:                                              # 保存失敗時のエラーチェック
        raise RuntimeError(f"Failed to write image to {path}")
    return os.path.abspath(path)                                 # 保存先の絶対パスを返す


def record_to_db(conn, image_path):
    """撮影した画像の情報をデータベースに記録する"""
    captured_at = datetime.now().isoformat(timespec='seconds')   # 撮影時刻をISO形式で取得
    cur = conn.cursor()
    # capturesテーブルに新しいレコードを追加（is_on=0は完了済みを意味する）
    cur.execute("""INSERT INTO captures (is_on, image_path, captured_at)
                   VALUES (0, ?, ?)""", (image_path, captured_at))
    conn.commit()                                                # データベースへ反映
    print(f"[OK] Captured -> {image_path} at {captured_at}")     # 成功メッセージを出力


def main_loop():
    """メイン処理：毎日1回撮影・保存・記録を行い、その後24時間待機する"""
    ensure_db_exists()   # データベースが存在するか確認
    print("Starting daily capture service (1 photo per day).")

    # 無限ループ（毎日1回撮影）
    while True:
        conn = sqlite3.connect(DB_PATH, timeout=10)  # データベースに接続
        try:
            frame = capture_image()                   # カメラで画像を1枚撮影
            image_path = save_image(frame)            # 撮影画像を保存
            record_to_db(conn, image_path)            # 撮影記録をDBに登録
        except Exception as e:
            print("[ERROR]", e)                       # 何か問題があれば表示
        finally:
            conn.close()                              # DB接続を閉じる

        # 次の撮影まで24時間待機
        print(f"Sleeping for {SLEEP_INTERVAL_SECONDS / 3600:.1f} hours...")
        time.sleep(SLEEP_INTERVAL_SECONDS)


if __name__ == "__main__":
    main_loop()  # スクリプトが直接実行されたときにメイン処理を開始


# capture_service_daily.py
# A script that captures one image per day from a camera,
# saves it to the 'images' folder, and records it in the SQLite database.

import sqlite3      # For SQLite database operations
import os           # For file and directory handling
import cv2          # OpenCV for camera capture and image saving
from datetime import datetime  # For timestamps
import time         # For sleep intervals
import pathlib      # For file/directory management
import sys          # For exiting the program when needed

# --- Configuration ---
DB_PATH = "captures.db"                 # Path to SQLite database file
IMAGES_DIR = "images"                   # Directory to save captured images
SLEEP_INTERVAL_SECONDS = 24 * 60 * 60   # 1 day = 86400 seconds
CAMERA_INDEX = 0                        # Camera index (usually 0 for the default camera)


def ensure_db_exists():
    """Check if the database exists. If not, print an error and exit."""
    if not os.path.exists(DB_PATH):
        print(f"Database '{DB_PATH}' not found. Please run 'python init_db.py' first.")
        sys.exit(1)  # Stop the program if the DB file is missing


def capture_image(camera_index=CAMERA_INDEX):
    """Open the camera, capture one frame, and return the image."""
    cap = cv2.VideoCapture(camera_index)       # Open camera device
    if not cap.isOpened():                     # Check if camera opened successfully
        cap.release()
        raise RuntimeError(f"Cannot open camera index {camera_index}")
    time.sleep(0.2)                            # Wait briefly for camera to stabilize
    ret, frame = cap.read()                    # Read one frame
    cap.release()                              # Release the camera
    if not ret or frame is None:               # Check for capture failure
        raise RuntimeError("Failed to read frame from camera")
    return frame                               # Return captured image frame


def save_image(frame):
    """Save the captured frame as a JPEG image and return its absolute path."""
    pathlib.Path(IMAGES_DIR).mkdir(parents=True, exist_ok=True)  # Create folder if it doesn't exist
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")                # Timestamp for filename
    filename = f"{ts}.jpg"                                       # Example: "20251105_090001.jpg"
    path = os.path.join(IMAGES_DIR, filename)                    # Construct save path
    success = cv2.imwrite(path, frame)                           # Save the image as JPEG
    if not success:                                              # Check if save succeeded
        raise RuntimeError(f"Failed to write image to {path}")
    return os.path.abspath(path)                                 # Return absolute path of saved file


def record_to_db(conn, image_path):
    """Insert a record into the database with image path and capture timestamp."""
    captured_at = datetime.now().isoformat(timespec='seconds')   # Get current time in ISO format
    cur = conn.cursor()
    # Insert a new record; is_on=0 means the capture is completed
    cur.execute("""INSERT INTO captures (is_on, image_path, captured_at)
                   VALUES (0, ?, ?)""", (image_path, captured_at))
    conn.commit()                                                # Commit changes to the database
    print(f"[OK] Captured -> {image_path} at {captured_at}")     # Print success message


def main_loop():
    """Main loop: capture once per day, save, record, then sleep for 24 hours."""
    ensure_db_exists()   # Ensure the database is ready
    print("Starting daily capture service (1 photo per day).")

    # Infinite loop: capture once every 24 hours
    while True:
        conn = sqlite3.connect(DB_PATH, timeout=10)  # Connect to the database
        try:
            frame = capture_image()                   # Capture one image from the camera
            image_path = save_image(frame)            # Save the captured image
            record_to_db(conn, image_path)            # Record info into the database
        except Exception as e:
            print("[ERROR]", e)                       # Print error message if something fails
        finally:
            conn.close()                              # Close the database connection safely

        # Sleep for one day before next capture
        print(f"Sleeping for {SLEEP_INTERVAL_SECONDS / 3600:.1f} hours...")
        time.sleep(SLEEP_INTERVAL_SECONDS)


if __name__ == "__main__":
    main_loop()  # Start the main loop when the script is executed directly
