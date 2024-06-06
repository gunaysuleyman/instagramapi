from dotenv import load_dotenv, find_dotenv
import os 
from openai import OpenAI
import pandas as pd 
import json

_ = load_dotenv(find_dotenv())

client = OpenAI(api_key=os.environ.get('OPEN_AI_KEY'))

class NameInfo:
    gender_country_data = []

    def get_name_info_by_openai(self,name_list:list):
        response = client.chat.completions.create(
        model="gpt-3.5-turbo-16k",
        messages=[
            {
            "role": "system",
            "content": [
                {
                "type": "text",
                "text": "Verilen listede yer alan isim ya da kelimenin hangi ülkeye ait olduğunu ve eğer isimse cinsiyetini belirleyip, bunları JSON formatında dışarı aktaran bir asistansın.\nİsim ve Kelime Ayıklama:\nHer öğedeki isim ya da kelime kısmını belirle.\nİsim ya da kelime kısmı bazen gizlenmiş olabilir, bu durumda isim veya kelimeyi tespit edip ayıkla. Örneğin, Hamza_cic3k_1 aslında Hamza çiçek olabilir.\nİsim Tespiti:\nİsimlerin yaygın kullanımına göre cinsiyeti belirle.\nErkek isimleri için gender değeri \"M\", kadın isimleri için \"F\",  uniseks isimler için \"U\" olsun.\nTespit edilemeyen için \"unknown\"  olarak ata.Cinsiyet girildiyse kesinlikle country  de girilmeli BOŞ OLMAMALI.\nKelime Tespiti:\nGelen değer hangi ülkeye ait olduğu anlaşılıyorsa o ülkenin kısaltmasını ekle örnek : [\"US\"]\nGelen değer anlaşılmıyorsa , gender değeri \"unknown\" olarak ata.\nÜlke Tespiti:\nİsmin hangi ülkeye ait olduğu anlaşılıyorsa, o ülkenin kısaltmasını country olarak ata (örneğin [\"TR\"])\nİsimler ve kelimelerin hangi ülkelere ait olduğunu belirle liste olarak ver sadece en popüler iki ülke .\nBir isim birden fazla ülkeye ait olabiliyorsa, ülke bilgilerini liste olarak ver sadece en popüler iki ülke .\nGelen Değer anlaşılmıyorsa country değeri []\nCinsiyet Tespiti : \nGelen öğenin cinsiyet bilgisi tespit edilirse gender uygun çıktı yazılır ve country bilgisi de eklenir.\nGelen öğe bilgisi tespit edilemezse gender \"unknown\" değeri atanır .\nGelen öğenin cinsiyeti yok ama dil tespiti yapılırsa gender \"unknown\" country tespit edilen dil değeri atanır örnek : \"kedi\" gender  \"unknown\"  country [\"TR\"] olarak ata .\nJSON Çıktısı Oluştur:\nHer öğe için name, gender ve country alanlarını içeren JSON nesneleri oluştur.\nÇıktıdaki name değeri girilen full_name değeri olarak kalmalı.\nÖrnek Girdi:[\"Ziya\",\"Dora futbol akademi\",\"Zukanovic\"]\nÖrnek Çıktı:[ {\"name\": \"Ziya\", \"gender\": \"M\", \"country\": [\"TR\"]},{\"name\": \"Dora futbol akademi\", \"gender\": \"M\", \"country\": [\"TR\"]},{\"name\": \"Zukanovic\", \"gender\": \"U\", \"country\": [\"BA\", \"HR\"]}]\nJSON yapısını bozacak işlemlerden kaçın Çıktıyı liste içerisinde JSON olarak ver (tek tırnak yerine çift tırnak kullan) .\n"
                }
            ]
            },
            {
            "role": "user",
            "content": [
                {
                "type": "text",
                "text": f"{name_list}"
                }
            ]
            }
                
        ],
        temperature=1,
        max_tokens=1024,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
        )
        return response.choices[0].message.content
    
    def process_names_from_csv(self, csv_file_path):
        df = pd.read_csv(csv_file_path)
        name_list = df['full_name'].dropna().unique().tolist()
        
        for i in range(0, len(name_list), 10):
            batch = name_list[i:i+10]
            batch_info = self.get_name_info_by_openai(batch)
            print(batch_info)
            print(type(batch_info))
            # batch_info = [{"name": "Ziya", "gender": "M", "country": ["TR"]},{"name": "Dora futbol akademi", "gender": "unknown", "country": ["TR"]},{"name": "Efeftbl10", "gender": "unknown", "country": []},{"name": "Adar", "gender": "U", "country": ["IL"]}]
            batch_info_json = json.loads(batch_info)
            self.gender_country_data.extend(batch_info_json)
        self.update_csv_with_gender_country(df,csv_file_path)
    
    def update_csv_with_gender_country(self, df, csv_file_path):
        if 'gender' not in df.columns:
            df['gender'] = None
        if 'country' not in df.columns:
            df['country'] = None
        print(self.gender_country_data)
        for data in self.gender_country_data:
            name = data['name']
            gender = data['gender']
            country = data['country']
            df.loc[df['full_name'] == name, ['gender', 'country']] = [gender, ','.join(country)]
        df.to_csv(csv_file_path, index=False)


# if __name__ == "__main__":
#     app = NameInfo()
#     app.process_names_from_csv("comments.csv")