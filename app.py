<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HedefAVM Online Satış İstatistik Paneli</title> <!-- Sayfa başlığı güncellendi -->
    <!-- Tailwind CSS CDN -->
    <script src="https://cdn.tailwindcss.com"></script>
    <!-- Chart.js CDN (Veri Görselleştirmesi için) -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <!-- Font Awesome (İkonlar için) -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
    <style>
        /* Genel stil ayarları */
        body {
            font-family: 'Inter', sans-serif;
            background: linear-gradient(135deg, #6a0dad 0%, #00008b 100%); /* Mor ve lacivert tonlarında degrade arka plan */
            min-height: 100vh;
            margin: 0;
            padding: 20px;
            box-sizing: border-box;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            color: #ffffff;
        }
        /* Ana içerik sarmalayıcı */
        .main-content-wrapper {
            display: flex;
            flex-direction: column;
            align-items: center;
            width: 100%;
            max-width: 800px;
            margin-top: 20px;
            background-color: rgba(0, 0, 0, 0.2); /* Hafif şeffaf siyah arka plan */
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 15px 40px rgba(0, 0, 0, 0.3); /* Büyük gölge */
        }
        /* İstatistik kapsayıcısı */
        .stats-container {
            background-color: rgba(0, 0, 0, 0.4); /* Daha koyu şeffaf siyah */
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2); /* Orta boy gölge */
            width: 100%;
            text-align: center;
            color: #ffffff;
        }
        /* Başlık stili */
        .section-title {
            color: #ffffff;
            margin-bottom: 15px;
            font-size: 2.5rem;
            font-weight: 800;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.5); /* Metin gölgesi */
        }
        /* Dönem göstergesi */
        .period-display {
            font-size: 1rem;
            color: #e0e0e0;
        }
        /* Logo kapsayıcısı */
        .logo-container {
            margin-bottom: 30px;
            width: 100%;
            display: flex;
            justify-content: center;
            align-items: center;
      