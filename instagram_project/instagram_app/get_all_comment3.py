import requests
from dataclasses import dataclass
import csv
import time 
import re
@dataclass
class GetComments:
    """
    Instagram yorumlarını çekmek için kullanılan sınıf.

    Instagram hesabına oturum açar, yorumları çeker ve CSV dosyasına yazar.

    Parametreler:
    - s: Requests session nesnesi
    - username: Instagram kullanıcı adı
    - password: Instagram şifre
    - user_id: Kullanıcı ID'si
    - csrf_token: CSRF token 
    - session_id: Oturum ID'si
    - post_url : Gönderi url'si 
    - max_retries: İstek yeniden deneme sayısı (varsayılan olarak 3)
    - instagram_auth: Instagram oturum açma durumu (varsayılan olarak False)
    - PROXY: Proxy ayarları 
    """

    s = requests.Session()
    username: str 
    password: str 
    PROXY : dict 
    user_id : str = ""
    csrf_token : None = ""
    session_id : None = ""
    max_retries :int = 3
    instagram_auth : bool = False
    post_url :  str = "https://www.instagram.com/p/C7M-qDBJapz/"

    def headers(self):
        headers = {
                'accept': '*/*',
                'accept-language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
                'cache-control': 'no-cache',
                'pragma': 'no-cache',
                'priority': 'u=1, i',
                'referer': 'https://www.instagram.com/p/C67h0NHoYfG/?img_index=1',
                'sec-ch-prefers-color-scheme': 'light',
                'sec-ch-ua': '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
                'sec-ch-ua-full-version-list': '"Chromium";v="124.0.6367.208", "Google Chrome";v="124.0.6367.208", "Not-A.Brand";v="99.0.0.0"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-model': '""',
                'sec-ch-ua-platform': '"Windows"',
                'sec-ch-ua-platform-version': '"15.0.0"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-origin',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
                'x-asbd-id': '129477',
                'x-csrftoken': f'"{self.csrf_token}"',
                'x-ig-app-id': '936619743392459',
                'x-ig-www-claim': 'hmac.AR0cWKMhdpT0PF59NwLdQ50asqG1u0KI_CFCBsNlWzpn-K6M',
                'x-requested-with': 'XMLHttpRequest',
            }
        return headers

    def instagram_login(self):
        """
        Instagram'a oturum açmayı sağlayan fonksiyon.

        Kullanıcı adı ve şifre parametreleri kullanılarak Instagram hesabına oturum açar.
        Oturum açma başarılıysa, oturum bilgilerini saklar ve instagram_auth değerini True yapar.
        Oturum açma başarısızsa, instagram_auth değerini False yapar.

        Parametreler:
        - self: Sınıfın örneği.

        """
        link = 'https://www.instagram.com/accounts/login/'
        login_url = 'https://www.instagram.com/accounts/login/ajax/'
        payload = {
            'username': self.username,
            'enc_password': f'#PWD_INSTAGRAM_BROWSER:0:{time}:{self.password}',
            'queryParams': {},
            'optIntoOneTap': 'false'
        }
        r = self.s.get(link,proxies=self.PROXY)
        csrf = re.findall(r"csrf_token\":\"(.*?)\"",r.text)[0]
        r = self.s.post(login_url,data=payload,headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": "https://www.instagram.com/accounts/login/",
        "x-csrftoken":csrf
        })
        if r.status_code == 200 :
            cookies = r.cookies
            self.session_id = cookies.get('sessionid')
            self.user_id    = cookies.get('ds_user_id')  
            self.instagram_auth = True
            print("*INSTAGRAM LOGIN SUCCESSFUL")
        else:
            self.instagram_auth = False
            print("*INSTAGRAM LOGIN FAILED")



    def get_cookies(self):
        """
        Instagram çerezlerini alır.

        Instagram üzerindeki çerezlerden csrftoken ve sessionid değerlerini alır.

        Parametreler:
        - self: Sınıfın örneği.

        Dönen Değerler:
        - csrftoken: CSRF token değeri
        - sessionid: Oturum ID değeri
        """
        response = self.s.get("https://www.instagram.com")
        cookies = response.cookies
        csrftoken = cookies.get('csrftoken')
        cookies.set('sessionid',self.session_id)
        sessionid = cookies.get('sessionid')
        return csrftoken,sessionid
    
    def create_cookie(self):
        """
        CSRF token ve sessionid ile çerez oluşturur.

        CSRF token ve sessionid değerlerini kullanarak çerez oluşturur.

        Parametreler:
        - self: Sınıfın örneği.

        Dönen Değer:
        - cookies: Oluşturulan çerezlerin sözlük formatı
        """
        csrf_token,sessionid = self.get_cookies()
        cookies = {
            
            'csrftoken': f'"{csrf_token}"',
            'sessionid': f'"{sessionid}"',
        }
        return cookies
    



    
    def params_data(self,data):
        """
        Parametre verisini işler ve API istek parametrelerini oluşturur.

        Verilen veriye göre API istek parametrelerini oluşturur.

        Parametreler:
        - self: Sınıfın örneği.
        - data: İşlenecek veri

        Dönen Değer:
        - params: API isteği için oluşturulan parametrelerin sözlük formatı
        """
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
        """
        Verilen bir Instagram gönderisi URL'sinden medya kimliğini çıkarır.

        Returns:
            int: Instagram gönderisi için medya kimliği.
        """
        alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_'
        parts = self.post_url.split("/")
        short_code = parts[-2] if parts[-1] == '' else parts[-1]
        media_id = 0
        for letter in short_code:
            media_id = (media_id * 64) + alphabet.index(letter)

        return media_id

    def get_media_data(self):
        """
        Medya verilerini alır ve CSV dosyasına yazar.

        Instagram üzerindeki bir medyanın yorumlarını alır ve bunları bir CSV dosyasına yazar.

        Parametreler:
        - self: Sınıfın örneği.
        """
        if self.instagram_auth:
            media_id = self.get_post_media_id()
            url = f'https://www.instagram.com/api/v1/media/{media_id}/comments/'
            param = {'permalink_enabled': 'false'}
            print("URL : ",url)
            with open('comments.csv', 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['user_id', 'username','full_name', 'is_verified', 'is_private', 'is_verified', 'comment_like_count', 'comment']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
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
                                    print(text['user_id'],text['user']['username'],text['user']['full_name'],text['user']['is_verified'],text['user']['is_private'],text['user']['is_verified'],text['comment_like_count'], text['text'])
                                    writer.writerow({'user_id': text['user_id'], 'username': text['user']['username'],'full_name':text['user']['full_name'], 'is_verified': text['user']['is_verified'], 'is_private': text['user']['is_private'], 'comment_like_count': text['comment_like_count'], 'comment': text['text']})
                                if 'next_min_id' in json_data:
                                    param = {'min_id': json_data['next_min_id']}
                                else:
                                    return
                                success = True
                            else:
                                print(f"API isteği başarısız. Durum kodu: {response.status_code}")
                                break
                        except requests.exceptions.RequestException as e:
                            attempt += 1
                            if attempt < self.max_retries:
                                print(f"İstek hatası: {e}. Yeniden denenecek ({attempt}/{self.max_retries})...")
                                time.sleep(5)
                            else:
                                print(f"İstek hatası: {e}. Maksimum deneme sayısına ulaşıldı.")
                                return
                        except Exception as e :
                            attempt += 1
                            if attempt < self.max_retries:
                                print(f"HATA: {e}. Yeniden denenecek ({attempt}/{self.max_retries})...")
                                time.sleep(5)
                            else:
                                print(f"Hata: {e}. Maksimum deneme sayısına ulaşıldı.")
                                return
        else:
            print("*INSTAGRAM AUTH FAILED : ",self.instagram_auth)

if __name__ == "__main__":
    proxy_settings  = {
        "http": "http://a435a86294b79682842c:e51451e73d65a1dd@gw.dataimpulse.com:823",
        "https": "http://a435a86294b79682842c:e51451e73d65a1dd@gw.dataimpulse.com:823",
    }
    app = GetComments(username="elzarosa6865",password="ighsapcooM24",post_url="https://www.instagram.com/p/C4qx56pJd_F/",PROXY=proxy_settings)
    app.instagram_login()
    app.get_media_data()

