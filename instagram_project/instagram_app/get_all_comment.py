from dataclasses import dataclass
import requests
from datetime import datetime
from pytz import timezone
import re
import time
import unicodedata
import json
import os
from fake_useragent import UserAgent

@dataclass
class GetComments:
    username: str
    password: str
    post_url: str
    PROXY: dict
    

    def __post_init__(self):
        self.s = requests.Session()
        self.user_id = ""
        self.csrf_token = None
        self.session_id = None
        self.max_retries = 3
        self.instagram_auth = False

    def headers(self):
        ua = UserAgent()
        headers = {
            'User-Agent': str(ua.chrome),
            'x-csrftoken': f'{self.csrf_token}',
            'x-ig-app-id': '936619743392459',
            'x-asbd-id': '129477',
        }
        return headers

    def save_session_data(self, session_id, user_id, user_agent, instagram_auth):
        data = {
            'session_id': session_id,
            'user_id': user_id,
            'user_agent': user_agent,
            'instagram_auth': instagram_auth
        }
        print("save_session_data", data)
        with open('session_data.json', 'w') as f:
            json.dump(data, f)
        print("*save_session_data", data)

    def load_session_data(self):
        file_path = os.path.join(os.path.dirname(__file__), 'session_data.json')
        print("load_session_data", file_path)
        if os.path.exists(file_path):
            print("session_data.json dosyası bulundu.")
            with open(file_path, 'r') as f:
                try:
                    data = json.load(f)
                    print("load_session_data", data)  # Debug
                    session_id = data.get('session_id')
                    user_id = data.get('user_id')
                    user_agent = data.get('user_agent')
                    instagram_auth = data.get('instagram_auth')

                    # Debug
                    print(f"session_id: {session_id}")
                    print(f"user_id: {user_id}")
                    print(f"user_agent: {user_agent}")
                    print(f"instagram_auth: {instagram_auth}")

                    return session_id, user_id, user_agent, instagram_auth
                except json.JSONDecodeError:
                    print("JSONDecodeError: session_data.json dosyası düzgün biçimlendirilmemiş.")
                    return None, None, None, False
        else:
            print("session_data.json dosyası bulunamadı.")  # Debug: dosya bulunamadı
        return None, None, None, False

    def is_session_valid(self):
        check_url = "https://www.instagram.com/"
        with requests.Session() as s:
            s.cookies.set('sessionid', self.session_id)
            s.cookies.set('ds_user_id', self.user_id)
            r = s.get(check_url, headers={"User-Agent": self.user_agent})
            if r.status_code == 200 and self.user_id in r.text:
                return True
        return False

    def instagram_login(self):
        self.session_id, self.user_id, self.user_agent, self.instagram_auth = self.load_session_data()
        print("*load_session_data", self.session_id, self.user_id, self.user_agent, self.instagram_auth)
        if self.session_id and self.user_id and self.is_session_valid():
            self.instagram_auth = True
            print(" - USING SAVED SESSION - ")
            return
        
        link = 'https://www.instagram.com/accounts/login/'
        login_url = 'https://www.instagram.com/accounts/login/ajax/'
        time = int(datetime.now().timestamp())
        
        payload = {
            'username': self.username,
            'enc_password': f'#PWD_INSTAGRAM_BROWSER:0:{time}:{self.password}',
            'queryParams': {},
            'optIntoOneTap': 'false'
        }
        print("instagram_login", self.session_id, self.user_id, self.username, self.password)
        with requests.Session() as s:
            try:
                r = s.get(link)
                csrf = re.findall(r"csrf_token\":\"(.*?)\"", r.text)[0]

                ua = UserAgent()
                self.user_agent = str(ua.chrome)
                r = s.post(login_url, data=payload, headers={
                    "User-Agent": self.user_agent,
                    "X-Requested-With": "XMLHttpRequest",
                    "Referer": "https://www.instagram.com/accounts/login/",
                    "x-csrftoken": csrf
                })

                if r.status_code == 200:
                    cookies = s.cookies
                    print("kurabiye", cookies)
                    # self.csrf_token = csrf
                    # self.session_id = cookies.get('sessionid')
                    # self.user_id = cookies.get('ds_user_id')
                    if cookies.get('sessionid') is not None and cookies.get('ds_user_id') is not None:
                        self.session_id = cookies.get('sessionid')
                        print(self.session_id)
                        self.user_id = cookies.get('ds_user_id')
                        print(self.user_id)
                        self.instagram_auth = True
                        print(" - INSTAGRAM LOGIN SUCCESSFUL - ")
                        self.save_session_data(self.session_id, self.user_id, self.user_agent, self.instagram_auth)
                    else:
                        print("*FAILED TO RETRIEVE SESSION ID INFORMATION")
                else:
                    self.instagram_auth = False
                    print("*INSTAGRAM LOGIN FAILED")
            except requests.exceptions.ConnectionError as e:
                print("*ConnectionError  - ( CHECK YOUR INTERNET )\n\n", e)
    
    def get_cookies(self):
        response = self.s.get("https://www.instagram.com")
        cookies = response.cookies
        csrftoken = cookies.get('csrftoken')
        cookies.set('sessionid', self.session_id)
        sessionid = cookies.get('sessionid')
        return csrftoken, sessionid
    
    def create_cookie(self):
        csrf_token, sessionid = self.get_cookies()
        cookies = {
            'csrftoken': f'{csrf_token}',
            'sessionid': f'{sessionid}',
        }
        return cookies

    def params_data(self, data):
        params = {
            'can_support_threading': 'true',
            'sort_order': 'popular',
        }
        if 'permalink_enabled' in data and data['permalink_enabled'] is not None:
            params['permalink_enabled'] = data['permalink_enabled']
        elif 'min_id' in data and data['min_id'] is not None:
            params['min_id'] = data['min_id']
        return params

    def get_post_media_id(self):
        alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_'
        parts = self.post_url.split("/")
        short_code = parts[-2] if parts[-1] == '' else parts[-1]
        media_id = 0
        for letter in short_code:
            media_id = (media_id * 64) + alphabet.index(letter)
        return media_id
    
    def normalize_text(self, text):
        normalized_text = unicodedata.normalize('NFKD', text)
        ascii_text = normalized_text.encode('ASCII', 'ignore').decode('ASCII')
        result_text = ascii_text.capitalize()
        return result_text

    
    def get_media_data(self):
        LOCAL_TIMEZONE = timezone('Europe/Istanbul')
        comments_data = []
        if self.instagram_auth:
            media_id = self.get_post_media_id()
            url = f'https://www.instagram.com/api/v1/media/{media_id}/comments/'
            param = {'permalink_enabled': 'false'}
            while True:
                attempt = 0
                success = False
                while attempt < self.max_retries and not success:
                    try:
                        response = self.s.get(
                            url,
                            params=self.params_data(param),
                            cookies=self.create_cookie(),
                            headers=self.headers(),
                            proxies=self.PROXY,
                            timeout=30
                        )
                        if response.status_code == 200:
                            json_data = response.json()
                            for text in json_data['comments']:
                                full_name = self.normalize_text(text['user']['full_name'])
                                created_at_naive = datetime.fromtimestamp(text['created_at'])
                                created_at_aware = LOCAL_TIMEZONE.localize(created_at_naive)
                                comments_data.append({
                                    'user_id': text['user_id'],
                                    'username': text['user']['username'],
                                    'full_name': full_name,
                                    'is_verified': text['user']['is_verified'],
                                    'is_private': text['user']['is_private'],
                                    'comment_like_count': text['comment_like_count'],
                                    'text': text['text'],
                                    'created_at': created_at_aware #datetime.fromtimestamp(text['created_at']) #
                                })
                            if 'next_min_id' in json_data:
                                param = {'min_id': json_data['next_min_id']}
                            else:
                                return comments_data
                            success = True
                        else:
                            attempt += 1
                            if attempt < self.max_retries:
                                print(f"API isteği başarısız. Durum kodu: {response.status_code}")
                                self.instagram_auth = False
                                time.sleep(5)
                                self.instagram_login()
                            else:
                                print(f"Hesap hatası - Maksimum deneme sayısına ulaşıldı.")
                                return comments_data
                    except requests.exceptions.RequestException as e:
                        attempt += 1
                        if attempt < self.max_retries:
                            print(f"İstek hatası: {e}. Yeniden denenecek ({attempt}/{self.max_retries})...")
                            time.sleep(5)
                        else:
                            print(f"İstek hatası: {e}. Maksimum deneme sayısına ulaşıldı.")
                            return comments_data
                    except Exception as e:
                        attempt += 1
                        if attempt < self.max_retries:
                            print(f"HATA: {e}. Yeniden denenecek ({attempt}/{self.max_retries})...")
                            time.sleep(5)
                        else:
                            print(f"Hata: {e}. Maksimum deneme sayısına ulaşıldı.")
                            return comments_data
        else:
            print("*INSTAGRAM AUTH FAILED")
        return comments_data
