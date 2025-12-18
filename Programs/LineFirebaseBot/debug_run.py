# debug_run.py
import main
import time

# ▼▼ ここにあなたのUser ID (Uから始まるやつ) を貼り付けてください ▼▼
MY_USER_ID = 'U03b8136028e9a0e600ec4e4ca959f1ae'
# ▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲

# ケース1: ステータスが変わった場合（成功パターン）
dummy_event_success = {
    'before_data': {'user_id': MY_USER_ID, 'status': '準備中'},
    'after_data':  {'user_id': MY_USER_ID, 'status': '発送完了'}
}

# ケース2: ステータスが変わっていない場合
dummy_event_no_change = {
    'before_data': {'user_id': MY_USER_ID, 'status': '準備中'},
    'after_data':  {'user_id': MY_USER_ID, 'status': '準備中'}
}

def run_test():
    print("=== テスト1: 通知が来るはず ===")
    main.on_document_updated_handler(dummy_event_success)
    
    print("\n" + "="*30 + "\n")
    time.sleep(1)
    
    print("=== テスト2: 通知が来ないはず ===")
    main.on_document_updated_handler(dummy_event_no_change)
    print("\n=== テスト終了 ===")

if __name__ == "__main__":
    run_test()
