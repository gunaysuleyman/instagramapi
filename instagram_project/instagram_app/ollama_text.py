import ollama

print("Ollama komutu alındı")

response = ollama.chat(model ="llama3", messages = [
    {
        'role' : 'user',
        'content': 'instagram yorumlarını analiz ederek hangi dilde yazıldığını ve olumlu mu yoksa olumsuz mu olduğunu analiz edebilir misin?',

    },
])
print("Ollama komutu geri döndü")                       
print(response['message']['content'])