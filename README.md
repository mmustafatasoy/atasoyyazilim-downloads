# Atasoy Yazılım — Uygulama İndirme Dosyaları

Burası **sadece Android uygulamalarının yayımlanmış APK dosyaları** için herkese açık indirme alanıdır. Uygulamaların kaynak kodu ve geliştirici depoları burada paylaşılmaz.

**Uygulama kataloğu:** https://atasoyyazilim.com/indirmeler/  
**EYMEN TV indirme sayfası:** https://atasoyyazilim.com/indir/eymen-tv/  
**NUR Kur’an indirme sayfası:** https://atasoyyazilim.com/indir/nur-kuran/

## Sürüm yayınlama (manuel)

Atasoy Yazılım sitesinin indirme sistemi hazırdır. APK dosyaları **bu deponun Releases bölümüne manuel yüklendiğinde** ilgili uygulamanın **Güncel sürüm / Eski sürümler** düğmelerine otomatik yansır. Bu yalnızca sürüm listesini okumaktır; kaynak depolardan dosya aktarımı veya otomatik APK yayımlama yapılmaz. **API anahtarı veya depo erişim tokenı gerekmez.**

EYMEN TV için beklenen Release etiket örnekleri:

| Sürüm | GitHub Releases etiketi | APK dosya adı |
| --- | --- | --- |
| 0.12 | `eymen-tv-v0.12` | `EYMEN-TV-Kanal-Listesi-v0.12.apk` |
| 0.11 | `eymen-tv-v0.11` | `EYMEN-TV-Kanal-Listesi-v0.11.apk` |
| 0.10 | `eymen-tv-v0.10` | `EYMEN-TV-Kanal-Listesi-v0.10.apk` |
| 0.9 | `eymen-tv-v0.9` | `EYMEN-TV-Kanal-Listesi-v0.9.apk` |

Daha eski sürümler de aynı etiket düzeniyle ayrı tutulabilir. Sürüm etiketleri mevcut release'lerle çakışmamalı; eski bir APK yerine farklı içerikli yeni dosya yazılmamalıdır. Yayınlanan sürümün ilk paylaşıldığı tarihi koruyun.

Tekno Play için beklenen **manuel APK yayın etiketleri**:

| Sürüm | GitHub Releases etiketi | APK dosya adı |
| --- | --- | --- |
| 0.3.1 | `tekno-play-v0.3.1` | `TeknoPlay-0.3.1-debug.apk` |
| 0.3.0 | `tekno-play-v0.3.0` | `TeknoPlay-0.3.0-debug.apk` |

**Tekno Play APK'ları özel geliştirme deposundadır ve henüz bu Public indirme deposuna aktarılmamıştır.** Otomatik aktarım yapılmaz. Her sürümün gerçek debug APK dosyasını manuel Releases varlığına ekleyin; kaynak kodu, özel proje URL'sini veya API anahtarını paylaşmayın. Debug dosyaları `prerelease` olarak işaretlenmelidir.

NUR Kur’an için örnek etiket: `nur-v0.9.0-test`. Sürüm içeriklerinin gerçek imzalama durumuna göre `prerelease` / TEST bilgisi doğru işaretlenmelidir.

### Manual yayın sırası

1. [Releases](https://github.com/mmustafatasoy/atasoyyazilim-downloads/releases) → **Draft a new release**.
2. Uygulama için yukarıdaki formata uyan yeni bir tag oluşturun.
3. İlgili, gerçekten derlenmiş APK dosyasını asset olarak ekleyin; sürüm notlarını ve cihaz uyumluluğunu yazın.
4. İmza durumu test ise **Set as a pre-release** seçin. Dosya boyutu ve varsa SHA-256 kontrolünü yapın.
5. **Publish release** ile yayımlayın. Sitenin indirme sayfası gerçek APK'yı, sürümü ve boyutu kendiliğinden görüntüler; site kodunu her sürüm için değiştirmeye gerek yoktur.

## Güvenlik

- **Özel geliştirme deposu bağlantılarını** yayın açıklamalarına eklemeyin.
- Bu depoda API token, kişisel erişim anahtarı, parolalar veya uygulama kaynak kodu bulunmamalıdır.
- APK sürümleri arasında farklı Android imzası kullanılmışsa eski sürümün üzerine yükleme yapılamayabilir.
- Public depodaki dosyalar herkes tarafından indirilebilir; telif ve lisans hakları kontrol edilmeden hiçbir APK dosyası yayımlanmamalıdır.
