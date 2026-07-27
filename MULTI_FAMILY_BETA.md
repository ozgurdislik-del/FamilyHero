# FamilyHero 4.30.0 Beta — Multi Family

- Aile kayıt ekranı: `/register-family`
- Yönetici girişi aile üyeliğine göre yapılır.
- Çocuk girişi aile kodu + kullanıcı anahtarı + şifre ile yapılır.
- Admin, rapor, istatistik, yapılandırma, liderlik ve oylama verileri aile bazında filtrelenir.
- Mevcut veriler `default-family` ailesine otomatik bağlanır.

## Test
1. `/register-family` üzerinden test ailesi oluşturun.
2. Yönetici girişi yapın.
3. Çocuk ekleyin.
4. Başka aile yöneticisinin çocuklarını göremediğini doğrulayın.
5. Çocuk girişinde doğru aile kodunu kullanın.
