# main.py
import os
from linebot import LineBotApi
from linebot.models import TextSendMessage
from linebot.exceptions import LineBotApiError

# ▼▼ 先ほど設定したトークンをここに貼り直してください ▼▼
CHANNEL_ACCESS_TOKEN = '0NlUvkSkTkCIecpx/XhUK1NLXRE2l36srzPrcsFzPaPE0dIwqz0CQHV16F7r7QIeXGkCoYzWAIAMpF0APG3ieOWEPxwN6fy5+XtkWB3kB+hkz6vo5zpv1txotvwCUHx3QWQc4cAOGqxavzjQOv8p9AdB04t89/1O/w1cDnyilFU='
# ▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲

# 引数から user_id を削除しました
def send_line_notification(message_text):
    if not CHANNEL_ACCESS_TOKEN:
        print(">> [エラー] LINEアクセストークン未設定")
        return

    line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
    try:
        # ★ここが変更点：push_message ではなく broadcast を使います
        line_bot_api.broadcast(TextSendMessage(text=message_text))
        print(f">> [LINE一斉送信成功] 内容: {message_text}")
    except LineBotApiError as e:
        print(f">> [LINE送信失敗] {e}")

def on_document_updated_handler(event_data):
    print(">> [処理開始] データ変更検知")
    
    before_data = event_data.get('before_data', {})
    after_data = event_data.get('after_data', {})
    
    # ★変更点：User IDのチェックを削除しました（IDがなくても送るため）

    old_status = before_data.get('status')
    new_status = after_data.get('status')

    print(f">> [比較] 旧: {old_status} -> 新: {new_status}")

    if old_status != new_status:
        msg = f"ステータスが更新されました！\n{old_status} → {new_status}"
        # ★変更点：user_id を渡さずに呼び出します
        send_line_notification(msg)
    else:
        print(">> [スキップ] 変更なし")