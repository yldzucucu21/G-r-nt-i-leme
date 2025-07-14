# Cave Emergency Guidance System

Bu proje, mağara gibi karmaşık ortamlarda acil durumlarda yönlendirme yapmak için geliştirilmiş bir masaüstü uygulamasıdır.

## Özellikler
- Gerçek zamanlı kamera görüntüsü ile işaret algılama
- Roboflow API ile şekil tanıma
- Tanınan şekle göre sesli ve görsel yönlendirme (sağa, sola, düz, geri)
- Kullanıcı dostu grafik arayüz (Tkinter)

## Kullanım
1. Uygulamayı başlatın.
2. "Start Camera" butonuna tıklayın.
3. Yönlendirme işaretlerini kameraya gösterin.
4. Uygulama, algılanan şekle göre sizi sesli ve ekranda yönlendirsin.

## Gereksinimler
- Python 3.x
- Gerekli kütüphaneler: `tkinter`, `Pillow`, `opencv-python`, `pyttsx3`, `inference_sdk`

## Kurulum
```bash
pip install pillow opencv-python pyttsx3 inference-sdk
```

## Notlar
- Roboflow API anahtarınızı ve model bilgilerinizi kendi hesabınıza göre güncelleyebilirsiniz.
- Arayüzdeki görseller ve gif dosyaları proje klasöründe olmalıdır.

