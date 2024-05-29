from django.shortcuts import render, redirect
from django.views import View
from .models import Comment
import requests
import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
import time
from urllib.parse import urlparse


class FetchCommentsView(View):
    def post(self, request):
        post_link = request.POST.get('post_link')
        instagram_username = 'suleymanhype'
        instagram_password = 'hidemyass123'
        
        options = webdriver.ChromeOptions()
        #options.add_argument('--headless')  # Headless modda çalıştırma (isteğe bağlı)
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

        #js ile veri çekme
        #var comments = document.querySelectorAll('.x9f619.xjbqb8w.x78zum5.x168nmei.x13lgxp2.x5pf9jr.xo71vjh.x1uhb9sk.x1plvlek.xryxfnj.x1c4vz4f.x2lah0s.xdt5ytf.xqjyukv.x1qjc9v5.x1oa3qoh.x1nhvcw1');
        # comments.forEach(function(comment) {
        # console.log(comment.innerText);
        # });
        


        try:
            driver.get('https://www.instagram.com/accounts/login/')
            time.sleep(4)
            
            # Giriş yap
            username_input = driver.find_element(By.NAME, 'username')
            password_input = driver.find_element(By.NAME, 'password')
            username_input.send_keys(instagram_username)
            password_input.send_keys(instagram_password)
            password_input.send_keys(Keys.RETURN)
            time.sleep(5)
            
            # Gönderi linkine git
            driver.get(post_link)
            time.sleep(5)
            
            # Yorumlar alanını bul
            comments_section = driver.find_element(By.CLASS_NAME, 'x5yr21d.xw2csxc.x1odjw0f.x1n2onr6')
            per_comments = driver.find_element(By.CLASS_NAME, 'x9f619.xjbqb8w.x78zum5.x168nmei.x13lgxp2.x5pf9jr.xo71vjh.x1uhb9sk.x1plvlek.xryxfnj.x1c4vz4f.x2lah0s.xdt5ytf.xqjyukv.x1qjc9v5.x1oa3qoh.x1nhvcw1')


            last_height = driver.execute_script("return arguments[0].scrollHeight", comments_section)
            while True:
                # Yorumları kaydır
                driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", comments_section)
                time.sleep(3)
                
                # Yorumları ve kullanıcı isimlerini bul
                comments = per_comments.find_elements(By.CSS_SELECTOR, 'li div div div span')
                print("comments: ", comments)
                usernames = per_comments.find_elements(By.CSS_SELECTOR, 'li div div div a')
                created_ats = per_comments.find_elements(By.CSS_SELECTOR, 'li div div div time')
                
                for username, comment, created_at in zip(usernames, comments, created_ats):
                    created_at_str = created_at.get_attribute('datetime')
                    Comment.objects.create(
                        username=username.text,
                        text=comment.text,
                        created_at=created_at_str,
                        post_link=post_link
                    )
                
                new_height = driver.execute_script("return arguments[0].scrollHeight", comments_section)
                if new_height == last_height:
                    break
                last_height = new_height
                
                # Yüklenmiş daha fazla yorum varsa yüklemeye devam et
                try:
                    load_more_comments = driver.find_element(By.CSS_SELECTOR, '.dCJp8')
                    load_more_comments.click()
                    time.sleep(2)
                except:
                    break
        finally:
            driver.quit()

        return redirect('comments:list')

    def get(self, request):
        comments = Comment.objects.all()
        return render(request, 'comments/selenium_comment_list.html', {'comments': comments})
    


# from django.shortcuts import render, redirect
# from django.views import View
# from .models import Comment
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.chrome.service import Service as ChromeService
# from webdriver_manager.chrome import ChromeDriverManager
# from selenium import webdriver
# import time

# class FetchCommentsView(View):
#     def post(self, request):
#         post_link = request.POST.get('post_link')
#         instagram_username = 'suleymanhype'
#         instagram_password = 'hidemyass123'
        
#         options = webdriver.ChromeOptions()
#         #options.add_argument('--headless')  # Headless modda çalıştırma (isteğe bağlı)
#         options.add_argument('--no-sandbox')
#         options.add_argument('--disable-dev-shm-usage')
#         driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
        
#         try:
#             driver.get('https://www.instagram.com/accounts/login/')
#             time.sleep(4)
            
#             # Giriş yap
#             username_input = driver.find_element(By.NAME, 'username')
#             password_input = driver.find_element(By.NAME, 'password')
#             username_input.send_keys(instagram_username)
#             password_input.send_keys(instagram_password)
#             password_input.send_keys(Keys.RETURN)
#             time.sleep(5)
            
#             # Gönderi linkine git
#             driver.get(post_link)
#             time.sleep(5)
            
#             # Yorumlar alanını bul
#             comments_section = driver.find_element(By.CLASS_NAME, 'x5yr21d.xw2csxc.x1odjw0f.x1n2onr6')
#             per_comments = driver.find_element(By.CLASS_NAME, 'x9f619.xjbqb8w.x78zum5.x168nmei.x13lgxp2.x5pf9jr.xo71vjh.x1uhb9sk.x1plvlek.xryxfnj.x1c4vz4f.x2lah0s.xdt5ytf.xqjyukv.x1qjc9v5.x1oa3qoh.x1nhvcw1')


#             last_height = driver.execute_script("return arguments[0].scrollHeight", comments_section)
#             while True:
#                 # Yorumları kaydır
#                 driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", comments_section)
#                 time.sleep(3)
                
#                 # Yorumları ve kullanıcı isimlerini bul
#                 comments = per_comments.find_elements(By.CSS_SELECTOR, 'li div div div span')
#                 print("comments: ", comments)
#                 usernames = per_comments.find_elements(By.CSS_SELECTOR, 'li div div div a')
#                 created_ats = per_comments.find_elements(By.CSS_SELECTOR, 'li div div div time')
                
#                 for username, comment, created_at in zip(usernames, comments, created_ats):
#                     created_at_str = created_at.get_attribute('datetime')
#                     Comment.objects.create(
#                         username=username.text,
#                         text=comment.text,
#                         created_at=created_at_str,
#                         post_link=post_link
#                     )
                
#                 new_height = driver.execute_script("return arguments[0].scrollHeight", comments_section)
#                 if new_height == last_height:
#                     break
#                 last_height = new_height
                
#                 # Yüklenmiş daha fazla yorum varsa yüklemeye devam et
#                 try:
#                     load_more_comments = driver.find_element(By.CSS_SELECTOR, '.dCJp8')
#                     load_more_comments.click()
#                     time.sleep(2)
#                 except:
#                     break
#         finally:
#             driver.quit()

#         return redirect('comments:list')

#     def get(self, request):
#         comments = Comment.objects.all()
#         return render(request, 'comments/selenium_comment_list.html', {'comments': comments})
    
# # instagram api ile çalışma
# # class FetchCommentsView(View):
# #     print("FetchCommentsView")
# #     def post(self, request):
# #         post_link = request.POST.get('post_link')
# #         post_id = urlparse(post_link).path.split('/p/')[1].rstrip('/')
# #         print(post_id)
# #         print(post_link)
# #         api_key = '38a5af809fmsh352e7fbc93a3e8fp1492c4jsn82b1ff48bd68'
# #         api_url = f"https://100-success-instagram-api-scalable-robust.p.rapidapi.com/instagram/v1/media/{post_id}/comments"  

# #         querystring = {"min_id":"{}","max_id":"{}"}

# #         headers = {
# #             'x-rapidapi-host': '100-success-instagram-api-scalable-robust.p.rapidapi.com',
# #             'x-rapidapi-key': api_key
# #         }
       
# #         response = requests.get(api_url, headers=headers, params=querystring)
# #         print(response.json())

# #         if response.status_code == 200:
# #             comments_data = response.json()
# #             print(comments_data)
# #             for comment in comments_data['comments']:
# #                 timestamp = comment['created_at']
# #                 created_at_datetime = datetime.datetime.utcfromtimestamp(timestamp)
# #                 formatted_created_at = created_at_datetime.strftime('%Y-%m-%d %H:%M:%S')
# #                 Comment.objects.create(
# #                     username=comment['user_id'],
# #                     text=comment['text'],
# #                     created_at=formatted_created_at,
# #                     post_link=post_link
# #                 )

# #         return redirect('comments:list')

# #     def get(self, request):
# #         print("Get request")
# #         comments = Comment.objects.all()
# #         return render(request, 'comments/comment_list.html', {'comments': comments})







# class FetchCommentsView(View):
#     def post(self, request):
#         post_link = request.POST.get('post_link')
#         instagram_username = 'suleymanhype'
#         instagram_password = 'hidemyass123'
        
#         options = webdriver.ChromeOptions()
#         #options.add_argument('--headless')
#         options.add_argument('--no-sandbox')
#         options.add_argument('--disable-dev-shm-usage')
#         driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
        
#         try:
#             driver.get('https://www.instagram.com/accounts/login/')
#             time.sleep(4)  
            
#             username_input = driver.find_element(By.NAME, 'username')
#             password_input = driver.find_element(By.NAME, 'password')
#             username_input.send_keys(instagram_username)
#             password_input.send_keys(instagram_password)
#             password_input.send_keys(Keys.RETURN)
#             time.sleep(5)  
            
#             driver.get(post_link)
#             time.sleep(5)  
            
#             # Locate the comments container
#             comments_container = driver.find_element(By.CSS_SELECTOR, 'ul.XQXOT')

#             while True:
#                 driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", comments_container)
#                 time.sleep(3)  
                
#                 comments = driver.find_elements(By.CSS_SELECTOR, 'ul.XQXOT li div div div span')
#                 usernames = driver.find_elements(By.CSS_SELECTOR, 'ul.XQXOT li div div div a')
#                 created_ats = driver.find_elements(By.CSS_SELECTOR, 'ul.XQXOT li div div div time')
                
#                 for username, comment, created_at in zip(usernames, comments, created_ats):
#                     created_at_str = created_at.get_attribute('datetime')
#                     Comment.objects.create(
#                         username=username.text,
#                         text=comment.text,
#                         created_at=created_at_str,
#                         post_link=post_link
#                     )
                
#                 if len(driver.find_elements(By.CSS_SELECTOR, '.dCJp8')) == 0:
#                     break
#                 else:
#                     load_more_comments = driver.find_element(By.CSS_SELECTOR, '.dCJp8')
#                     load_more_comments.click()
#                     time.sleep(2)
#         finally:
#             driver.quit()

#         return redirect('comments:list')

#     def get(self, request):
#         comments = Comment.objects.all()
#         return render(request, 'comments/selenium_comment_list.html', {'comments': comments})



# # Yorum konteynerini bul
# comments_container = None

# try:
#     comments_container = driver.find_element(By.CSS_SELECTOR, 'div._a9zr')  # İlk seçenek
# except:
#     pass

# if not comments_container:
#     try:
#         comments_container = driver.find_element(By.CSS_SELECTOR, 'div[role="dialog"] ul')  # Alternatif seçenek
#     except:
#         pass

# if not comments_container:
#     try:
#         comments_container = driver.find_element(By.CSS_SELECTOR, 'article div[role="presentation"] ul')  # Başka bir alternatif
#     except:
#         pass

# if not comments_container:
#     raise Exception("Yorum konteyneri bulunamadı")

# while True:
#     # Yorumları kaydır
#     driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", comments_container)
#     time.sleep(3)
    
#     # Yorumları ve kullanıcı isimlerini bul
#     comments = comments_container.find_elements(By.CSS_SELECTOR, 'li div div div span')
#     usernames = comments_container.find_elements(By.CSS_SELECTOR, 'li div div div a')
#     created_ats = comments_container.find_elements(By.CSS_SELECTOR, 'li div div div time')
    
#     for username, comment, created_at in zip(usernames, comments, created_ats):
#         created_at_str = created_at.get_attribute('datetime')
#         Comment.objects.create(
#             username=username.text,
#             text=comment.text,
#             created_at=created_at_str,
#             post_link=post_link
#         )
    
#     # Yüklenmiş daha fazla yorum varsa yüklemeye devam et
#     load_more_buttons = comments_container.find_elements(By.CSS_SELECTOR, 'button._abl-')
#     if not load_more_buttons:
#         break
#     else:
#         load_more_buttons[0].click()
#         time.sleep(2)

# # instagram api ile çalışma
# # class FetchCommentsView(View):
# #     print("FetchCommentsView")
# #     def post(self, request):
# #         post_link = request.POST.get('post_link')
# #         post_id = urlparse(post_link).path.split('/p/')[1].rstrip('/')
# #         print(post_id)
# #         print(post_link)
# #         api_key = '38a5af809fmsh352e7fbc93a3e8fp1492c4jsn82b1ff48bd68'
# #         api_url = f"https://100-success-instagram-api-scalable-robust.p.rapidapi.com/instagram/v1/media/{post_id}/comments"  

# #         querystring = {"min_id":"{}","max_id":"{}"}

# #         headers = {
# #             'x-rapidapi-host': '100-success-instagram-api-scalable-robust.p.rapidapi.com',
# #             'x-rapidapi-key': api_key
# #         }
       
# #         response = requests.get(api_url, headers=headers, params=querystring)
# #         print(response.json())

# #         if response.status_code == 200:
# #             comments_data = response.json()
# #             print(comments_data)
# #             for comment in comments_data['comments']:
# #                 timestamp = comment['created_at']
# #                 created_at_datetime = datetime.datetime.utcfromtimestamp(timestamp)
# #                 formatted_created_at = created_at_datetime.strftime('%Y-%m-%d %H:%M:%S')
# #                 Comment.objects.create(
# #                     username=comment['user_id'],
# #                     text=comment['text'],
# #                     created_at=formatted_created_at,
# #                     post_link=post_link
# #                 )

# #         return redirect('comments:list')

# #     def get(self, request):
# #         print("Get request")
# #         comments = Comment.objects.all()
# #         return render(request, 'comments/comment_list.html', {'comments': comments})



# --------
# # instagram api ile çalışma
# # class FetchCommentsView(View):
# #     print("FetchCommentsView")
# #     def post(self, request):
# #         post_link = request.POST.get('post_link')
# #         post_id = urlparse(post_link).path.split('/p/')[1].rstrip('/')
# #         print(post_id)
# #         print(post_link)
# #         api_key = '38a5af809fmsh352e7fbc93a3e8fp1492c4jsn82b1ff48bd68'
# #         api_url = f"https://100-success-instagram-api-scalable-robust.p.rapidapi.com/instagram/v1/media/{post_id}/comments"  

# #         querystring = {"min_id":"{}","max_id":"{}"}

# #         headers = {
# #             'x-rapidapi-host': '100-success-instagram-api-scalable-robust.p.rapidapi.com',
# #             'x-rapidapi-key': api_key
# #         }
       
# #         response = requests.get(api_url, headers=headers, params=querystring)
# #         print(response.json())

# #         if response.status_code == 200:
# #             comments_data = response.json()
# #             print(comments_data)
# #             for comment in comments_data['comments']:
# #                 timestamp = comment['created_at']
# #                 created_at_datetime = datetime.datetime.utcfromtimestamp(timestamp)
# #                 formatted_created_at = created_at_datetime.strftime('%Y-%m-%d %H:%M:%S')
# #                 Comment.objects.create(
# #                     username=comment['user_id'],
# #                     text=comment['text'],
# #                     created_at=formatted_created_at,
# #                     post_link=post_link
# #                 )

# #         return redirect('comments:list')

# #     def get(self, request):
# #         print("Get request")
# #         comments = Comment.objects.all()
# #         return render(request, 'comments/comment_list.html', {'comments': comments})
