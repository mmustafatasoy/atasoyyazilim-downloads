# ATASOY STORE media yükleme alanı

Her uygulama için katalogdaki ID ile aynı adla klasör açın.
Örnek: store/media/eymen-tv/01.png, 02.webp, 03.mp4

GitHub üzerinden dosya eklemek yeterli: push işlemi
.github/workflows/store-media-index.yml işini çalıştırır.
Bu iş store/media-index.json dosyasını otomatik üretir.
ATASOY STORE katalog yenilemesinde fotoğraf ve videoları algılar.
APK'yı tekrar derlemeye gerek yoktur.

Formatlar: JPG/JPEG, PNG, WebP, GIF, SVG, AVIF, MP4, WebM, M4V.
Görseller ve videolar birlikte, dosya adına göre alfabetik sıralanır.
01, 02, 03 isimleri önerilir. Uygulama başına en çok 30 medya.
Dosya başına en çok 80 MB. Özel verileri ve kişisel fotoğrafları
herkese açık indirme deposuna yüklemeyin.

Video bulunmuyorsa video alanı oluşturulmaz; yalnızca fotoğraflar
gösterilir. Dosya kaldırılırsa indeks güncellenir. Eski bir
medya indeksinin çevrimdışı önbelleği kısa süre gösterilebilir.

Doğrudan sitenin medya deposuna yükleyenler için alternatif:
store/catalog.json uygulama girdisine media/screenshot/videos URL
dizileri eklenebilir. Yalnızca atasoyyazilim.com üzerindeki
HTTPS bağlantıları ve indirme deposunun doğrulanmış ham medya
bağlantıları Android istemcisi tarafından kabul edilir.
