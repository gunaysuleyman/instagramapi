from django.test import TestCase

import scrapy
from scrapy.selector import Selector
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver

class InstagramCommentsSpider(scrapy.Spider):
    name = 'instagram_comments'
    
    def start_requests(self):
        instagram_username = 'suleymanhype'
        instagram_password = 'hidemyass123'
        post_link = 'https://www.instagram.com/p/C7KPMVuiCg3/'
        
        yield scrapy.Request(
            url='https://www.instagram.com/accounts/login/',
            callback=self.login,
            meta={
                'instagram_username': instagram_username,
                'instagram_password': instagram_password,
                'post_link': post_link
            }
        )

    def login(self, response):
        username_input = response.css('input[name="username"]::attr(name)').get()
        password_input = response.css('input[name="password"]::attr(name)').get()
        
        return scrapy.FormRequest.from_response(
            response,
            formdata={
                username_input: response.meta['instagram_username'],
                password_input: response.meta['instagram_password']
            },
            callback=self.parse_post,
            meta=response.meta
        )

    def parse_post(self, response):
        post_link = response.meta['post_link']
        driver = response.meta['driver']
        driver.get(post_link)
        
        # Yorumların tümünü yüklemek için scroll işlemleri buraya gelecek
        
        comments_section = driver.find_element(By.CLASS_NAME, 'x5yr21d.xw2csxc.x1odjw0f.x1n2onr6')
        html_content = comments_section.get_attribute('outerHTML')

        response = Selector(text=html_content)
        comments = response.css('ul.x5yr21d.xw2csxc.x1odjw0f > li')

        for comment in comments:
            username = comment.css('a.x3a7wzz.xvbytv2.x45n5gt::text').get()
            print(username)
            comment_text = comment.css('span::text').get()
            print(comment_text)
            timestamp = comment.css('time::attr(datetime)').get()
            created_at = datetime.fromisoformat(timestamp)
            
            yield {
                'username': username,
                'text': comment_text,
                'created_at': created_at,
                'post_link': post_link
            }
