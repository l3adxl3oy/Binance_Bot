"""
Script: get_chat_id.py
วิธีใช้:
1. สร้าง bot ใน Telegram ผ่าน @BotFather (จะได้ TOKEN)
2. ส่งข้อความไปหา bot ของคุณ
3. รันสคริปต์นี้เพื่อหา chat_id
"""

import requests
import sys

def get_chat_id(bot_token):
    url = f'https://api.telegram.org/bot{bot_token}/getUpdates'
    try:
        response = requests.get(url)
        data = response.json()
        
        if not data['ok']:
            print(f' Error: {data}')
            return
        
        if not data['result']:
            print(' No messages found!')
            print('Please send a message to your bot first, then run this again.')
            return
        
        print('\n Found Chats:\n')
        chats = set()
        for update in data['result']:
            if 'message' in update:
                chat = update['message']['chat']
                chat_id = chat['id']
                first_name = chat.get('first_name', 'N/A')
                username = chat.get('username', 'N/A')
                
                if chat_id not in chats:
                    print(f'Chat ID: {chat_id}')
                    print(f'Name: {first_name}')
                    print(f'Username: @{username}')
                    print('' * 40)
                    chats.add(chat_id)
        
        if chats:
            print(f'\n Copy your Chat ID and paste into config_example.py')
    
    except Exception as e:
        print(f' Error: {e}')

if __name__ == '__main__':
    print(' Enter your Telegram Bot Token (from @BotFather):')
    bot_token = input('Token: ').strip()
    
    if not bot_token:
        print(' Token cannot be empty!')
        sys.exit(1)
    
    get_chat_id(bot_token)
