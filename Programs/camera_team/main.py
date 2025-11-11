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

CREATE_SQL = """CREATE TABLE IF NOT EXISTS captures (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  is_on INTEGER DEFAULT 0,
  image_path TEXT,
  captured_at TEXT
);"""

def create_db():
        conn = sqlite3.connect(DB_PATH, timeout=10)
        try:
            cur = conn.cursor()
            cur.execute(CREATE_SQL)
            conn.commit()
            cur.execute("INSERT INTO captures (is_on) VALUES (1)")
            conn.commit()
            print("Database created (or existed) and a capture job was added. Job id =", cur.lastrowid)
        finally:
            conn.close()

def ensure_db_exists():
    """データベースファイルが存在するか確認し、なければ終了する"""
    if not os.path.exists(DB_PATH):
        print(f"Database '{DB_PATH}' not found. The database will be created.")
        create_db()


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
