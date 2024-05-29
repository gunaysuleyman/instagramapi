from django.shortcuts import render, redirect
from django.views import View
from .models import Comment
from django.http import JsonResponse
import requests
import re
import datetime
from bs4 import BeautifulSoup
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
import time
from urllib.parse import urlparse
import scrapy
from scrapy.selector import Selector
import instaloader
from dataclasses import dataclass


#Sadece bu views alanında çalışılabilir. Bu view ile yorumları alıp veritabanına aktarabiliriz. lastcomment.html sayfasında render ediyor.
class FetchCommentsLastView(View):
    def post(self, request):
        post_link = request.POST.get('post_link')
        if not post_link:
            return JsonResponse({'error': 'Gönderi bağlantısı gerekli'}, status=400)

        post_shortcode = post_link.split('/')[-2]
        response = requests.get(f'https://www.instagram.com/p/{post_shortcode}/')
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            media_tag = soup.find('meta', property='al:ios:url')
            user_tag = soup.find('meta', property='instapp:owner_user_id')

            media_id = None
            user_id = None

            if media_tag and 'content' in media_tag.attrs:
                media_id = media_tag['content'].split('=')[-1]
                print('media_id', media_id)

            if user_tag and 'content' in user_tag.attrs:
                user_id = user_tag['content']
                print('user_id', user_id)

        else:
            return JsonResponse({'error': 'Instagram gönderisi alınamadı'}, status=500)

        self.media_id = media_id
        self.user_id = user_id

        self.s = requests.Session()
        self.username = "fabianadrumond5016"
        self.password = "ighesapcooM@24"
        self.PROXY = {
            "http": "http://a435a86294b79682842c:e51451e73d65a1dd@gw.dataimpulse.com:823",
            "https": "http://a435a86294b79682842c:e51451e73d65a1dd@gw.dataimpulse.com:823",
        }
        self.csrf_token = None
        self.session_id = None
        self.max_retries = 3
        self.instagram_auth = False

        try:
            self.instagram_login()
            if self.instagram_auth:
                self.get_media_data(post_link)
                return redirect('comments:lastcomment')
            else:
                return JsonResponse({'error': 'Instagram girişi başarısız oldu'}, status=500)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    

    def headers(self):
        return {
            'accept': '*/*',
            'accept-language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
            'cache-control': 'no-cache',
            'pragma': 'no-cache',
            'priority': 'u=1, i',
            'referer': self.post_link,
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
            'x-csrftoken': self.csrf_token,
            'x-ig-app-id': '936619743392459',
            'x-ig-www-claim': 'hmac.AR0cWKMhdpT0PF59NwLdQ50asqG1u0KI_CFCBsNlWzpn-K6M',
            'x-requested-with': 'XMLHttpRequest',
        }

    def instagram_login(self):
        print("insta login", self.username, self.password)
        link = 'https://www.instagram.com/accounts/login/'
        login_url = 'https://www.instagram.com/accounts/login/ajax/'
        payload = {
            'username': self.username,
            'enc_password': f'#PWD_INSTAGRAM_BROWSER:0:{int(time.time())}:{self.password}',
            'queryParams': {},
            'optIntoOneTap': 'false'
        }
        r = self.s.get(link, proxies=self.PROXY)
        csrf = re.findall(r"csrf_token\":\"(.*?)\"", r.text)[0]
        r = self.s.post(login_url, data=payload, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36",
            "X-Requested-With": "XMLHttpRequest",
            "Referer": "https://www.instagram.com/accounts/login/",
            "x-csrftoken": csrf
        })
        if r.status_code == 200:
            cookies = r.cookies
            self.session_id = cookies.get('sessionid')
            self.user_id = cookies.get('ds_user_id')
            self.instagram_auth = True
            print("*INSTAGRAM LOGIN SUCCESSFUL")
        else:
            self.instagram_auth = False
            print("*INSTAGRAM LOGIN FAILED")

    def get_cookies(self):
        response = self.s.get("https://www.instagram.com")
        cookies = response.cookies
        csrftoken = cookies.get('csrftoken')
        print('get_cookies csrftoken:', csrftoken)
        cookies.set('sessionid', self.session_id)
        sessionid = cookies.get('sessionid')
        print('get_cookies sessionid:', sessionid)
        return csrftoken, sessionid

    def create_cookie(self):
        csrf_token, sessionid = self.get_cookies()
        self.csrf_token = csrf_token
        return {
            'csrftoken': csrf_token,
            'sessionid': sessionid,
        }

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

    def get_media_data(self, post_link):
        url = f'https://www.instagram.com/api/v1/media/{self.media_id}/comments/'
        param = {'permalink_enabled': 'false'}
        cookies = self.create_cookie()
        print('get_media_data', self.csrf_token)
        print('get_media_data', cookies)
        print('get_media_data', url)

        while True:
            attempt = 0
            success = False

            while attempt < 3 and not success:
                try:
                    response = self.s.get(
                        url,
                        params=self.params_data(param),
                        cookies=cookies,
                        headers=self.headers(),
                        proxies=self.PROXY,
                        timeout=10
                    )

                    if response.status_code == 200:
                        json_data = response.json()
                        for text in json_data['comments']:
                            Comment.objects.create(
                                username=text['user']['username'],
                                text=text['text'],
                                created_at=datetime.now(),
                                post_link=post_link
                            )
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
                    if attempt < 3:
                        print(f"İstek hatası: {e}. Yeniden denenecek ({attempt}/3)...")
                        time.sleep(5)
                    else:
                        print(f"İstek hatası: {e}. Maksimum deneme sayısına ulaşıldı.")
                        return
                except Exception as e:
                    attempt += 1
                    if attempt < 3:
                        print(f"HATA: {e}. Yeniden denenecek ({attempt}/3)...")
                        time.sleep(5)
                    else:
                        print(f"Hata: {e}. Maksimum deneme sayısına ulaşıldı.")
                        return
    def get(self, request):
        comments = Comment.objects.all()
        return render(request, 'comments/last_comment_list.html', {'comments': comments})                

class FetchCommentsView(View):
    def post(self, request):
        post_link = request.POST.get('post_link')
        instagram_username = 'fabianadrumond5016'
        instagram_password = 'ighesapcooM@24'
        
        options = webdriver.ChromeOptions()
        #options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

        try:
            driver.get('https://www.instagram.com/accounts/login/')
            time.sleep(4)
            
            username_input = driver.find_element(By.NAME, 'username')
            password_input = driver.find_element(By.NAME, 'password')
            username_input.send_keys(instagram_username)
            password_input.send_keys(instagram_password)
            password_input.send_keys(Keys.RETURN)
            time.sleep(5)
            
            driver.get(post_link)
            time.sleep(5)

            comments_section = driver.find_element(By.CLASS_NAME, 'x5yr21d.xw2csxc.x1odjw0f.x1n2onr6')
            #html_content = comments_section.get_attribute('outerHTML')
            last_height = driver.execute_script("return arguments[0].scrollHeight", comments_section)
            new_comments_loaded = True

            #response = Selector(text=html_content)
            #comments = response.css('ul.x5yr21d.xw2csxc.x1odjw0f > li')
            #print(comments)
            
            while new_comments_loaded:
                try:
                    driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", comments_section)
                    time.sleep(3)
                    new_height = driver.execute_script("return arguments[0].scrollHeight", comments_section)
                    if new_height == last_height:
                        new_comments_loaded = False
                    else:
                        last_height = new_height                    
                except Exception as e:
                    print("Kaydırma hatası:", e)
                    break
     
            comment_elements = driver.find_elements(By.CSS_SELECTOR, 'ul.XQXOT p')
            username_elements = driver.find_elements(By.CSS_SELECTOR, 'ul.XQXOT h3')
            time_elements = driver.find_elements(By.CSS_SELECTOR, 'ul.XQXOT time')

            for username_element, comment_element, time_element in zip(username_elements, comment_elements, time_elements):
                username = username_element.text
                comment = comment_element.text
                created_at = time_element.get_attribute('datetime')
                
                Comment.objects.create(
                    username=username,
                    text=comment,
                    created_at=created_at,
                    post_link=post_link
                )

        finally:
            driver.quit()

        return redirect('comments:selencomment')

    def get(self, request):
        comments = Comment.objects.all()
        return render(request, 'comments/selenium_comment_list.html', {'comments': comments})
    
class FetchCommentsApiView(View):
    def post(self, request):
        post_link = request.POST.get('post_link')
        
        headers = {
            'X-RapidAPI-Host': 'instagram-scraper-api2.p.rapidapi.com',
            'X-RapidAPI-Key': "38a5af809fmsh352e7fbc93a3e8fp1492c4jsn82b1ff48bd68"
        }
        
        
        post_id = post_link.split('/')[-2]
        
        url = "https://instagram-scraper-api2.p.rapidapi.com/v1/comments"

        querystring = {"code_or_id_or_url":post_id}
        
        try:
            response = requests.get(url, headers=headers, params=querystring)
            #print(response.json())
            response.raise_for_status()
            comments_data = response.json().get('data', [])
            #print("comments_data:", comments_data)
            
            for comment_data in comments_data['items']:
                username = comment_data['user']['username']
                #print(username)
                text = comment_data['text']
                #print(text)
                created_at = datetime.datetime.fromtimestamp(comment_data['created_at'])
                #print(created_at)
                
                Comment.objects.create(
                    username=username,
                    text=text,
                    created_at=created_at,
                    post_link=post_link
                )
        except Exception as e:
            print(f"Error: {e}")
        
        return redirect('comments:apicomment')

    def get(self, request):
        comments = Comment.objects.all()
        return render(request, 'comments/api_comment_list.html', {'comments': comments})
    
class FetchCommentsLoaderView(View):
    def post(self, request):
        post_link = request.POST.get('post_link')
        if not post_link:
            return JsonResponse({'error': 'Post link is required'}, status=400)
        
        
        L = instaloader.Instaloader()

        
        instagram_username = 'fabianadrumond5016'
        instagram_password = 'ighesapcooM@24'
        try:
            L.login(instagram_username, instagram_password)
            print("Logged in!")
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

       
        post_shortcode = post_link.split('/')[-2]
        print("post_shortcode:", post_shortcode)

        try:
            post = instaloader.Post.from_shortcode(L.context, post_shortcode)
            for comment in post.get_comments():
                Comment.objects.create(
                    username=comment.owner.username,
                    text=comment.text,
                    created_at=datetime.fromtimestamp(comment.created_at_utc.timestamp()),
                    post_link=post_link
                )
            return redirect('comments:loadercomment')
        except instaloader.exceptions.PrivateProfileNotFollowedException:
            return JsonResponse({'error': 'Cannot access comments of a private profile without following'}, status=403)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
        
        # try:
        #     post = instaloader.Post.from_shortcode(L.context, post_shortcode)
        #     print("post:", post)
        #     comments = []
        #     for comment in post.get_comments():
        #         Comment.objects.create(
        #             username=comment.owner.username,
        #             text=comment.text,
        #             created_at=datetime.fromtimestamp(comment.created_at_utc.timestamp()),
        #             post_link=post_link
        #         )
        #     return redirect('comments:selencomment')
        # except Exception as e:
        #     return JsonResponse({'error': str(e)}, status=500)

    def get(self, request):
        comments = Comment.objects.all()
        return render(request, 'comments/loader_comment_list.html', {'comments': comments}) 

# instagram api ile çalışma
# class FetchCommentsView(View):
#     print("FetchCommentsView")
#     def post(self, request):
#         post_link = request.POST.get('post_link')
#         post_id = urlparse(post_link).path.split('/p/')[1].rstrip('/')
#         print(post_id)
#         print(post_link)
#         api_key = '38a5af809fmsh352e7fbc93a3e8fp1492c4jsn82b1ff48bd68'
#         api_url = f"https://100-success-instagram-api-scalable-robust.p.rapidapi.com/instagram/v1/media/{post_id}/comments"  

#         querystring = {"min_id":"{}","max_id":"{}"}

#         headers = {
#             'x-rapidapi-host': '100-success-instagram-api-scalable-robust.p.rapidapi.com',
#             'x-rapidapi-key': api_key
#         }
       
#         response = requests.get(api_url, headers=headers, params=querystring)
#         print(response.json())

#         if response.status_code == 200:
#             comments_data = response.json()
#             print(comments_data)
#             for comment in comments_data['comments']:
#                 timestamp = comment['created_at']
#                 created_at_datetime = datetime.datetime.utcfromtimestamp(timestamp)
#                 formatted_created_at = created_at_datetime.strftime('%Y-%m-%d %H:%M:%S')
#                 Comment.objects.create(
#                     username=comment['user_id'],
#                     text=comment['text'],
#                     created_at=formatted_created_at,
#                     post_link=post_link
#                 )

#         return redirect('comments:list')

#     def get(self, request):
#         print("Get request")
#         comments = Comment.objects.all()
#         return render(request, 'comments/comment_list.html', {'comments': comments})
