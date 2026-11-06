# ATASOY STORE — Yeni Uygulama Ekleme (Telefondan)

Yeni uygulama yayımlamak için mağazanın Android kaynak kodunu değiştirmene gerek yok.

## 1. GitHub'a tek yayınla APK ve görselleri ekle

1. GitHub’da `mmustafatasoy/atasoyyazilim-downloads` deposuna gir.
2. **Releases → Draft a new release** bölümünü aç.
3. Yeni etiketi `store-uygulama-kimligi-v1.0.0` şeklinde oluştur.
   - Örneğin: `store-eymen-hava-v1.0.0`
   - Kimlikte küçük harf, rakam ve tire kullanılmalı.
   - Sürüm etiketi **APK'nın gerçek versionName değeriyle aynı** olmalı.
4. **Release title:** Uygulamanın görünen adı (ör. EYMEN Hava).
5. **Description:** Mağazada gösterilecek kısa uygulama açıklaması.
6. Bu yayına dosyaları ekle:
   - `app-release.apk` — **zorunlu**, Android imzalı gerçek APK.
   - `icon.png` — uygulamanın logosu; `icon.webp` de olur.
   - `01.png`, `02.jpg`, `03.mp4` — fotoğraf ve videolar.
7. **Publish release** seç.

`ATASOY STORE - automatic app registration` GitHub Actions işi otomatik
olarak APK'yı inceler, paket adını, sürüm adını, Android versionCode bilgisini
ve imza sertifikasını kontrol eder. GitHub SHA-256 varsa ayrıca karşılaştırır.
Başarılıysa `store/catalog.json` güncellenir ve görsel/video bağlantıları
uygulamanın kaydına eklenir. Mağazada **Yenile** ile görünür.

**Görsel/video dosyaları GitHub Release eki olarak kalır.** URL'leri katalogda
bağlanır, elle link yazmak gerekmez. Video yoksa boş video kutusu görünmez.
Görselleri ayrı olarak `store/media/<kimlik>/` klasörüne yüklemek de
desteklenir. Medya ilk sürümde yüklendiğinde sonraki sürümlerde tekrar
yüklemene gerek yoktur.

## 2. Yeni sürüm yüklemek

Aynı uygulama kimliğiyle yeni Release oluştur:
`store-eymen-hava-v1.0.1`.
Yeni APK'nın **packageName ve imza sertifikası eskisiyle aynı**, Android
`versionCode` ise bir önceki sürümden büyük/eşit olmalıdır.
`versionName` yeni etiketin `1.0.1` bölümüyle eşleşmelidir.
Yalnızca yeni `app-release.apk` ekleyebilirsin. Eski logo ve görseller
kalır. Yeni ekran görüntüsü eklersen önceki görsel listesi değiştirilir.

## 3. İsteğe bağlı zengin katalog bilgileri

Yeni uygulamanın kategorisi varsayılan `Uygulama`, platformu
`Android Telefon` olarak alınır. İstersen ilk yayın öncesinde
`store/submissions/<kimlik>.json` dosyası ekleyebilirsin:

```json
{
  "name": "EYMEN Hava",
  "description": "Güncel hava durumu, günlük ve saatlik tahminler",
  "category": "Araçlar",
  "platform": "Android Telefon",
  "icon": "EH",
  "accent": "#2F5BFF",
  "pageUrl": "https://atasoyyazilim.com",
  "featured": false
}
```

Bu dosya isteğe bağlıdır. APK **paket kimliği**, **sürümü** ve **imza
sertifikası** elle girilmez, Android APK'sından doğrulanır.

## 4. Eğer otomasyon kendiliğinden başlamazsa

Depo → **Actions → ATASOY STORE - automatic app registration → Run workflow**
seç. `tag` alanına tam yayın etiketini yaz. Özellikle GitHub Actions
içinden GITHUB_TOKEN ile oluşturulmuş Release yayınları, güvenlik sebebiyle
başka workflow'ları otomatik başlatmayabilir.

Başarısız kayıt denemelerinde var olan katalog korunur. Hata nedenini
Actions kayıtlarında görebilirsin. Yanlış paket adı, sürüm etiketi veya
farklı imza sertifikasıyla mevcut uygulama otomatik güncellenmez.

## Güvenlik ve cihaz algılama sınırları

Yalnızca sahibi `mmustafatasoy` olan bu **herkese açık** indirme deposundaki
`store-...` yayınları kaydedilir. Gizli proje kodları yayımlanmaz.
Android uygulama görünürlüğü için yalnızca ana ekran başlatıcısı bulunan
telefon ve TV uygulamaları sorgulanabilir; `QUERY_ALL_PACKAGES` kullanılmaz.
Bağımsız başlatıcısı bulunmayan APK'larda "Yüklü" tespiti için ayrıca
Android manifestinde özel paket sorgusu gerekebilir. Android kaldırma ve
kurulum işlemleri kullanıcının sistem onayına bağlıdır.
