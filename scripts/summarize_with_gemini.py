# -*- coding: utf-8 -*-
"""
GEMINI AI SUMMARIZER & AUDIT RECOMMENDATION GENERATOR
Inspektorat Daerah Kota Padang - Sistem Pengawasan Berbasis Risiko 2026

Skrip ini membaca 47 data riil terverifikasi dari data/records_clean.json
dan memanfaatkan Google Gemini API (gemini-1.5-flash / gemini-2.0-flash)
untuk menghasilkan telaah risiko dan matriks rekomendasi strategis 5 OPD secara otomatis.
"""

import os
import sys
import json
import urllib.request
import urllib.error
from pathlib import Path

def generate_gemini_summary(api_key=None, model="gemini-3.1-flash-lite"):
    # Ambil API Key dari argumen atau Environment Variable
    if not api_key:
        api_key = os.environ.get("GEMINI_API_KEY")
    
    if not api_key:
        print("=" * 60)
        print("ERROR: Gemini API Key belum ditentukan!")
        print("Anda dapat memasukkannya melalui:")
        print("1. Parameter perintah: python scripts/summarize_with_gemini.py <YOUR_API_KEY>")
        print("2. Environment variable: set GEMINI_API_KEY=...")
        print("Dapatkan API Key gratis di Google AI Studio: https://aistudio.google.com/")
        print("=" * 60)
        return False

    # Daftar kandidat model aktif
    candidate_models = [model, "gemini-3.5-flash", "gemini-3.7-flash", "gemini-3.8-flash"]

    # Baca dataset riil terverifikasi
    data_path = Path("data/records_clean.json")
    if not data_path.exists():
        data_path = Path("../data/records_clean.json")
    
    if not data_path.exists():
        print(f"Error: {data_path} tidak ditemukan!")
        return False

    with open(data_path, "r", encoding="utf-8") as f:
        records = json.load(f)

    print(f"[*] Berhasil memuat {len(records)} data aduan riil terverifikasi (Jan - Nov 2026).")
    print(f"[*] Menghubungi Google Gemini API ({model})...")

    # Siapkan ringkasan data untuk prompt
    data_context = []
    for r in records:
        data_context.append(
            f"- [{r['tgl']}] [{r['opd']}] [{r['prioritas']}] {r['text']} (Sumber: {r['platform']})"
        )
    data_text = "\n".join(data_context)

    system_prompt = """
Anda adalah Lead Data Analyst & Lead Risk Auditor di Inspektorat Daerah Kota Padang (APIP).
Susunlah ANALISIS MENDALAM (DEEP INVESTIGATIVE AUDIT ANALYSIS) dari kumpulan 47 kejadian riil Kota Padang tahun 2026.
Bukan dalam bentuk nota dinas biasa, melainkan dekomposisi mendalam atas anatomi risiko, akar masalah, matriks kuadran intervensi 2x2, serta tabel kausalitas per OPD.

Format yang diwajibkan:
# 📊 ANALISIS MENDALAM: ANATOMI RISIKO DAN TITIK BOTTLENECK PEMBANGUNAN KOTA PADANG 2026

## 1. DISTRIBUSI KLASTER ISU & TINGKAT KEPARAHAN (METRIK UTAMA)
Tampilkan tabel statistik per klaster isu:
| Klaster Isu | Volume Kasus | % | Severity Index | OPD Penanggung Jawab | Status Realitas |

## 2. ANALISIS AKAR MASALAH SISTEMIK (4 PILAR KEGAGALAN)
Bedah secara tajam mengapa masalah-masalah ini berulang terus:
1. **Pilar Tata Kelola (Silo Mentality):** Gap koordinasi antar-dinas teknis (Dishub vs Satpol PP; Disdag vs Satpol PP).
2. **Pilar Perencanaan (Manajemen Transisi):** Kegagalan alur pembeli di Pasar Raya Fase VII lantai 2 sepi omset.
3. **Pilar Infrastruktur (Preventif):** Reactive maintenance banjir drainase Koto Tangah & krisis TPA Air Dingin 640 ton.
4. **Pilar Penegakan Aturan (Aspek Sosial):** Benturan penertiban tenda ceper vs kebutuhan hidup pedagang pantai.

## 3. MATRIKS KUADRAN PRIORITAS INTERVENSI (2x2)
Tabel kuadran 2x2:
- KUADRAN 1: KRITIS & MENDESAK (High Impact, High Urgency)
- KUADRAN 2: STRATEGIS PRIORITAS TINGGI (High Impact, Low/Medium Urgency)
- KUADRAN 3: OPERASIONAL CEPAT (Medium Impact, High Urgency)
- KUADRAN 4: RUTIN PEMELIHARAAN (Routine / Low Impact)

## 4. MATRIKS KAUSALITAS 360° PER OPD
| OPD | Titik Isu | Akar Masalah | Dampak Kerugian | Aksi Korektif Terukur | KPI |

## 5. REKOMENDASI INTERVENSI STRATEGIS BAGI INSPEKTUR DAERAH
(4 instrumen pengawasan konkret yang harus diterbitkan Inspektorat).

Gunakan gaya bahasa analitis tajam, berbasis data, lugas, tanpa basa-basi, dan berbobot eksekutif tinggi.
"""

    for target_model in candidate_models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{target_model}:generateContent?key={api_key}"
        print(f"[*] Mencoba model {target_model}...")

        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": f"{system_prompt}\n\nBERIKUT ADALAH 47 DATA ADUAN RIIL TERVERIFIKASI TAHUN 2026:\n{data_text}"
                        }
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.2,
                "maxOutputTokens": 3000
            }
        }

        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )

        try:
            with urllib.request.urlopen(req, timeout=40) as response:
                result = json.loads(response.read().decode("utf-8"))
                generated_text = result["candidates"][0]["content"]["parts"][0]["text"]
                
                output_report = Path("reports/ANALISIS_MENDALAM_GEMINI_2026.md")
                with open(output_report, "w", encoding="utf-8") as f:
                    f.write(generated_text)
                    
                print(f"[✓] Berhasil menghasilkan analisis mendalam dengan {target_model}! Laporan disimpan di: {output_report}")
                print("\nPreview Ringkasan Eksekutif:")
                print("-" * 50)
                print(generated_text[:600] + "...\n")
                return True

        except urllib.error.HTTPError as e:
            err_msg = e.read().decode("utf-8", errors="ignore")
            print(f"[-] Gagal pada model {target_model} (HTTP {e.code}). Mencoba alternatif...")
            continue
        except Exception as e:
            print(f"[-] Error pada model {target_model}: {e}")
            continue

    print("Error: Seluruh model kandidat Gemini gagal merespons.")
    return False

if __name__ == "__main__":
    key = sys.argv[1] if len(sys.argv) > 1 else None
    generate_gemini_summary(key)

