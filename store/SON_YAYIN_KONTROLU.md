# ATASOY STORE — Son yayın kontrolü (7 Kasım 2026)

## Tamamlanan işler

- ATASOY STORE katalog/medya indeks sistemi ve imzalı beta APK.
- Yeni uygulamalarda Release üzerinden APK paket adı, sürüm, imza ve SHA-256 doğrulaması.
- "Yüklü", "Güncelle", "Aç" ve Android onaylı "Cihazdan kaldır" işlemleri.
- TeknoPlay ile EYMEN Launcher'ın eski APK'larını **kendi özel depolarında** doğrulayan
  ve yalnızca APK dosyasını public indirme deposuna aktarabilen GitHub Actions akışı.
- Public katalog sağlamlık testi: özel/izin verilmeyen GitHub depolarından
  doğrudan indirme gösterilmez.

## Yayın için tek seferlik yetki eksikliği

İki özel depo için gereken `ATASOY_DOWNLOADS_TOKEN` henüz tanımlı değil.
GitHub iş akışı kaynak APK'yı ve imzasını doğrulasa da **public yayın yapmaz**.

1. GitHub → Settings → Developer settings → Personal access tokens →
   Fine-grained tokens → Generate new token.
2. Erişim: sadece `mmustafatasoy/atasoyyazilim-downloads`.
3. Repository permissions: **Contents: Read and write**.
   Başka depolara veya hesap geneline erişim vermeyin.
4. Oluşan token'ı sohbet, e-posta veya koda yazmadan **her iki özel repoda**:
   - `mmustafatasoy/TeknoPlay` → Settings → Secrets and variables →
     Actions → New repository secret
   - `mmustafatasoy/EYMENLAUNCHER` → aynı bölüm
   Secret name: `ATASOY_DOWNLOADS_TOKEN`.
5. Her depoda Actions → **Publish verified APK-only test release to ATASOY STORE** →
   Run workflow. Akış yalnızca APK'yı public depo Releases'e yükler.
6. Public `store-auto-register.yml` akışı yeni APK'yı kontrol edip katalog
   açıklamasını, indirilebilir sürümü ve varsa ekli fotoğrafları otomatik oluşturur.

**ÖNEMLİ:** Mevcut TeknoPlay APK'sı debug/test; Launcher APK'sı
`com.eymen.launcher.debug` paketli kısıtlı önizleme sürümüdür.
Bunlar **kararlı sürüm değildir**. Uygulama imzalama anahtarı değişirse
Android eski sürümün üzerine güncellemeye izin vermez. Android korumasını
kapatmayın. Yeni kalıcı imzalı yayın APK'sı üretmek gerekebilir.

## Eymen 101

`mmustafatasoy/Eymen101` kaynak deposu 7 Kasım 2026 son kontrolünde GitHub
API'den **404** dönmeye başladı. `v0.1.1` yayınlanmış APK'sı daha önce
görünse de son kontrolde kaynağına erişilemedi. Kırık bağlantı göstermemek
için mağazada indirme geçici olarak pasif bırakıldı.

Çözüm: kaynak depoyu tekrar erişilebilir hale getirmek veya kullanıma uygun
imzalı APK'yı `mmustafatasoy/atasoyyazilim-downloads` public deposunda
`store-eymen-101-v<gerçek APK versionName>` etiketiyle
`app-release.apk` adı altında yeni bir Release olarak yayımlamak.
`Eymen 101` kataloğunun release kaydı önce merkezi store formatına
geçirilmeli; aksi halde otomasyon mevcut manuel kaydı güvenlik gerekçesiyle
değiştirmez.

## Gerçek ekran görüntüleri

Ekran görüntülerini tahmin ederek, APK içi ikonlardan sahte ekranlar
üreterek veya eski tasarım taslaklarını gerçek uygulama gibi göstererek
katalog doldurmayın. Gerçek Android uygulamasından alınan fotoğrafları
`store/media/<id>/01.png`, `02.png` veya videoyu `03.mp4`
olarak yüklemek yeterlidir. `store-media-index.yml` bunları otomatik
algılar. Android emülatörle gerçek Eymen 101 ekranı yakalama akışı da
hazırlandı; ancak APK kaynağı GitHub'da 404 döndüğü için başarılı olamadı.

## Kararlı v1.0.0 öncesi telefon testi

- İndir → Android kurulum onayı → **Yüklü**.
- Aynı imzayla yeni sürüm yayınlandığında **Güncelle**.
- Kaldırmayı iptal edince uygulama kalıyor, onaylayınca kalkıyor.
- Fotoğraflar kaydırılıyor; video varsa oynuyor, yoksa boş mesaj çıkmıyor.
- Cihazda ve gerekirse Android TV'de gerçek açılış/test.

Bunlar geçmeden **kararlı v1.0.0** ilan etmeyin.
