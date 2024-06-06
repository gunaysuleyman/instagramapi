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
from .get_all_comment import GetComments
import os


#Sadece bu views alanında çalışılabilir. Bu view ile yorumları alıp veritabanına aktarabiliriz. lastcomment.html sayfasında render ediyor.
class FetchCommentsLastView(View):
    def post(self, request):
        post_link = request.POST.get('post_link')
        if not post_link:
            return JsonResponse({'error': 'Gönderi bağlantısı gerekli'}, status=400)

        proxy_settings = {
            "http": "http://a435a86294b79682842c:3d312e5084024c61@gw.dataimpulse.com:823",
            "https": "http://a435a86294b79682842c:3d312e5084024c61@gw.dataimpulse.com:823",
        }

        post_shortcode = post_link.split('/')[-2]
        response = requests.get(f'https://www.instagram.com/p/{post_shortcode}/')
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            user_tag = soup.find('meta', property='instapp:owner_user_id')
            #print('user_tag', user_tag)

            if user_tag and 'content' in user_tag.attrs:    
                user_id = user_tag['content']
                #print('user_id', user_id)

                app = GetComments(
                    username="fabianadrumond5016",
                    password="ighesapcooM@24",
                    post_url=post_link,
                    PROXY=proxy_settings
                    
                )
                
                app.instagram_login()
                if app.instagram_auth:
                    comments_data = app.get_media_data()
                    for comment in comments_data:
                        Comment.objects.create(
                            username=comment['username'],
                            full_name=comment['full_name'],
                            text=comment['text'],
                            created_at=comment['created_at'],
                            post_link=post_link
                        )
                    return JsonResponse({'status': 'Başarılı'}, status=200)
                else:
                    return JsonResponse({'error': 'Instagram oturumu açma başarısız'}, status=500)
            else:
                return JsonResponse({'error': 'Kullanıcı ID bulunamadı'}, status=400)
        else:
            return JsonResponse({'error': 'Instagram gönderisi bulunamadı'}, status=400)

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
