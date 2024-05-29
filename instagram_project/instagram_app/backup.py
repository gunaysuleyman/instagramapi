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

            self.media_id = None
            self.user_id = None

            if media_tag and 'content' in media_tag.attrs:
                media_id = media_tag['content'].split('=')[-1]
                print('media_id', media_id)

            if user_tag and 'content' in user_tag.attrs:    
                user_id = user_tag['content']
                print('user_id', user_id)

        else:
            return JsonResponse({'error': 'Instagram gönderisi alınamadı'}, status=500)

        self.s = requests.Session()
        self.username = "fabianadrumond5016"
        self.password = "ighesapcooM@24"
        self.user_id = user_id
        print("self.user_id",self.user_id)
        self.csrf_token = ""
        self.session_id = ""
        self.media_id = media_id
        print("self.media_id",self.media_id)
        self.max_retries = 3
        self.instagram_auth = False

        self.PROXY = {
            "http": "http://a435a86294b79682842c:e51451e73d65a1dd@gw.dataimpulse.com:823",
            "https": "http://a435a86294b79682842c:e51451e73d65a1dd@gw.dataimpulse.com:823",
        }

        def instagram_login():
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
            }, proxies=self.PROXY)
            if r.status_code == 200:
                cookies = r.cookies
                print("cookies", cookies)
                self.session_id = cookies.get('sessionid')
                self.instagram_auth = True
                print("instagram_login", self.session_id, self.user_id)
                print("*INSTAGRAM LOGIN SUCCESSFUL")

            else:
                self.instagram_auth = False

        def get_cookies():
            response = self.s.get("https://www.instagram.com")
            cookies = response.cookies
            csrftoken = cookies.get('csrftoken')
            print('get_cookies csrftoken:', csrftoken)
            cookies.set('sessionid', self.session_id)
            sessionid = cookies.get('sessionid')
            print('get_cookies sessionid:', sessionid)
            return csrftoken, sessionid

        def create_cookie():
            csrf_token, sessionid = get_cookies()
            cookies = {
                'csrftoken': f'{csrf_token}',
                'sessionid': f'{sessionid}',
            }
            print(cookies)
            return cookies

        def headers(csrf_token):
            headers = {
                'accept': '*/*',
                'accept-language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
                'referer': f'https://www.instagram.com/p/{post_shortcode}/',
                'sec-ch-prefers-color-scheme': 'dark',
                'sec-ch-ua': '"Opera";v="109", "Not:A-Brand";v="8", "Chromium";v="123"',
                'sec-ch-ua-full-version-list': '"Opera";v="109.0.5097.80", "Not:A-Brand";v="8.0.0.0", "Chromium";v="123.0.6312.124"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-model': '""',
                'sec-ch-ua-platform': '"Windows"',
                'sec-ch-ua-platform-version': '"15.0.0"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-origin',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 OPR/109.0.0.0',
                'x-asbd-id': '129477',
                'x-csrftoken': f'{csrf_token}',
                'x-ig-app-id': '936619743392459',
                'x-ig-www-claim': 'hmac.AR030rMZiT25aQ2nwbs09hTLMukLakTXghswDPgDbRw2xm32',
                'x-requested-with': 'XMLHttpRequest',
            }
            return headers

        def params_data(data):
            params = {
                'can_support_threading': 'true',
                'sort_order': 'popular',
            }
            if 'permalink_enabled' in data and data['permalink_enabled'] is not None:
                params['permalink_enabled'] = data['permalink_enabled']
            elif 'min_id' in data and data['min_id'] is not None:
                params['min_id'] = data['min_id']
            return params

        def get_media_data():
            url = f'https://www.instagram.com/api/v1/media/{media_id}/comments/'
            param = {'permalink_enabled': 'false'}
            csrf_token, cookies = create_cookie()
            print('get_media_data', csrf_token)
            print('get_media_data', cookies)
            print('get_media_data', url)

            while True:
                attempt = 0
                success = False

                while attempt < 3 and not success:
                    try:
                        response = self.s.get(
                            url,
                            params=params_data(param),
                            cookies=cookies,
                            headers=headers(csrf_token),
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

        try:
            instagram_login()
            if self.instagram_auth:
                get_media_data()
                return redirect('comments:lastcomment')
            else:
                return JsonResponse({'error': 'Instagram girişi başarısız oldu'}, status=500)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    def get(self, request):
        comments = Comment.objects.all()
        return render(request, 'comments/last_comment_list.html', {'comments': comments})