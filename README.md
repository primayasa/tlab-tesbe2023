# API Resep Makanan
API Resep Makanan adalah api untuk mencatat resep dengan fungsi utama resep makanan, bahan makanan dan kategori makanan.

Proyek ini ditujukan sebagai Tes Teknis Backend Engineer di TLab 2023

Oleh : Wahyu Primayasa

## Requirements
- Flask==2.3.3
- psycopg2-binary==2.9.7
- SQLAlchemy==2.0.20
- requests==2.31.0
- python-dotenv==1.0.0

## Instalasi
- Clone repository ini
- Masuk ke directory project
- Jalankan perintah
```docker compose up```

## Uji Coba
Untuk menjalankan unit test project ini disarankan menggunakan venv python. Berikut langkahnya.
- Masuk ke directory project
- Buat python virtual env baru

    ```python3.9 -m venv venv```

- Jalankan virtual env baru

    ```source venv/bin/activate```

- Install semua requirements pada virtual enviroment

    ```python3.9 -m pip install -r requirements.txt```

- Jalankan unit test dengan perintah.

    ```python3.9 unit_test.py```

Catatan : 
- Ketika menjalankan unit test ini, pastikan bahwa aplikasi sudah running.
- Test ini akan menghapus semua tabel pada database yang digunakan pada project dan membuatnya kembali dengan tujuan mengosongkan data pada tabel.

