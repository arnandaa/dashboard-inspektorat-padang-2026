# -*- coding: utf-8 -*-
"""
YOUTUBE DATA API V3 INGESTOR - INSPEKTORAT KOTA PADANG
Skrip otomatis untuk memproses hasil tarikan komentar YouTube API v3
dan mengintegrasikannya langsung ke dalam dataset sentimen pembangunan Kota Padang.
"""

import sys
import json
import csv
import re
import html
from pathlib import Path
import pandas as pd

# Kamus Normalisasi Minang
MINANG_NORMALIZATION = {
    r'\bindak\b': 'tidak',
    r'\bndak\b': 'tidak',
    r'\balun\b': 'belum',
    r'\bjan\b': 'jangan',
    r'\brancak bana\b': 'sangat bagus',
    r'\brancak\b': 'bagus',
    r'\btasumbek\b': 'tersumbat',
    r'\btabangkalai\b': 'mangkrak',
    r'\bsarok\b': 'sampah',
    r'\bbuek\b': 'buat',
    r'\baia\b': 'air',
    r'\bmambana\b': 'memohon',
    r'\bpabaelok\b': 'perbaiki',
    r'\bcapek\b': 'cepat',
    r'\bmokasi\b': 'terima kasih',
    r'\bbarasiah\b': 'bersih',
    r'\blalok\b': 'tidur',
    r'\bmanumpuak\b': 'menumpuk',
    r'\bko\b': 'ini',
    r'\btu\b': 'itu',
    r'\bse\b': 'saja',
    r'\btiok\b': 'setiap'
}

def clean_text(text):
    text = html.unescape(str(text)).lower()
    text = re.sub(r'https?://\S+|www\.\S+', ' ', text)
    text = re.sub(r'@\w+', ' ', text)
    text = re.sub(r'#(\w+)', r'\1', text)
    text = re.sub(r'<[^>]+>', ' ', text)
    for pattern, replacement in MINANG_NORMALIZATION.items():
        text = re.sub(pattern, replacement, text)
    return re.sub(r'\s+', ' ', text).strip()

def auto_label_sentiment(text):
    lower = text.lower()
    neg_words = ['sepi', 'rusak', 'mati', 'turun', 'anjlok', 'sulit', 'macet', 'gembok', 'bau', 'tasumbek', 'banjir', 'pungli', 'tacampan', 'parah', 'kumuah']
    pos_words = ['bagus', 'rancak', 'mantap', 'nyaman', 'murah', 'bersih', 'barasiah', 'alhamdulillah', 'bangga', 'tertib', 'tarimo kasih']
    
    has_neg = any(w in lower for w in neg_words)
    has_pos = any(w in lower for w in pos_words)
    
    if has_neg and has_pos:
        return 'campuran', 'mendukung_dengan_catatan'
    elif has_neg:
        return 'negatif', 'meminta_perbaikan'
    elif has_pos:
        return 'positif', 'mendukung'
    else:
        return 'netral', 'tidak_menyatakan_sikap'

def ingest_youtube_file(input_path, output_csv=None):
    p = Path(input_path)
    if not p.exists():
        print(f"Error: File {input_path} tidak ditemukan!")
        return

    # Auto-resolve dataset path if not specified
    if output_csv is None:
        candidates = [
            Path("data/padang_social_media.csv"),
            Path("../data/padang_social_media.csv"),
            Path("padang_social_media.csv")
        ]
        output_csv = next((c for c in candidates if c.exists()), Path("data/padang_social_media.csv"))
    else:
        output_csv = Path(output_csv)

    records = []
    if p.suffix.lower() == '.json':
        with open(p, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Handle Google API commentThreads response or raw list
            items = data.get('items', data) if isinstance(data, dict) else data
            for idx, item in enumerate(items):
                if isinstance(item, dict) and 'snippet' in item:
                    # YouTube API v3 commentThread structure
                    top = item['snippet'].get('topLevelComment', {}).get('snippet', {})
                    comment = top.get('textDisplay', top.get('textOriginal', ''))
                    author = top.get('authorDisplayName', f'YT_User_{idx}')
                    likes = top.get('likeCount', 0)
                    pub_at = top.get('publishedAt', '2026-10-15 12:00:00')[:19].replace('T', ' ')
                    vid_id = item['snippet'].get('videoId', 'YT_VIDEO')
                else:
                    comment = item.get('comment', item.get('text', ''))
                    author = item.get('author', f'YT_User_{idx}')
                    likes = item.get('likeCount', 0)
                    pub_at = item.get('publishedAt', '2026-10-15 12:00:00')
                    vid_id = item.get('videoId', 'YT_VIDEO')
                
                if comment.strip():
                    sent, stance = auto_label_sentiment(comment)
                    records.append({
                        "record_id": f"REC-YT-{idx+1:04d}",
                        "platform": "youtube",
                        "content_type": "comment",
                        "content_id": vid_id,
                        "parent_content_id": "",
                        "published_at": pub_at,
                        "collected_at": "2026-11-05 23:00:00",
                        "keyword": "youtube api pull",
                        "project_id": "EKO-05" if "pasar" in comment.lower() else "INF-01",
                        "project_name": "Revitalisasi Pasar Raya" if "pasar" in comment.lower() else "Pembangunan Kota Padang",
                        "location": "Kota Padang",
                        "text": comment,
                        "like_count": likes,
                        "reply_count": 0,
                        "view_count": 0,
                        "share_count": 0,
                        "url": f"https://www.youtube.com/watch?v={vid_id}",
                        "sentiment": sent,
                        "stance": stance,
                        "issue_theme": "Revitalisasi Pasar & Ekonomi" if "pasar" in comment.lower() else "Infrastruktur Umum",
                        "include": "yes",
                        "annotation_note": f"Penarikan otomatis YouTube Data API v3 ({author})"
                    })
    elif p.suffix.lower() == '.csv':
        df_yt = pd.read_csv(p, encoding='utf-8-sig')
        # Map columns
        col_text = next((c for c in ['textDisplay', 'textOriginal', 'comment', 'text'] if c in df_yt.columns), None)
        if col_text:
            for idx, row in df_yt.iterrows():
                c_text = str(row[col_text])
                if c_text.strip():
                    sent, stance = auto_label_sentiment(c_text)
                    records.append({
                        "record_id": f"REC-YT-CSV-{idx+1:04d}",
                        "platform": "youtube",
                        "content_type": "comment",
                        "content_id": str(row.get('videoId', 'YT_CSV')),
                        "parent_content_id": "",
                        "published_at": str(row.get('publishedAt', '2026-10-15 12:00:00')),
                        "collected_at": "2026-11-05 23:00:00",
                        "keyword": "youtube api csv",
                        "project_id": "EKO-05" if "pasar" in c_text.lower() else "INF-01",
                        "project_name": "Revitalisasi Pasar Raya" if "pasar" in c_text.lower() else "Pembangunan Kota Padang",
                        "location": "Kota Padang",
                        "text": c_text,
                        "like_count": row.get('likeCount', 0),
                        "reply_count": 0,
                        "view_count": 0,
                        "share_count": 0,
                        "url": f"https://www.youtube.com/watch?v={row.get('videoId', '')}",
                        "sentiment": sent,
                        "stance": stance,
                        "issue_theme": "Revitalisasi Pasar & Ekonomi" if "pasar" in c_text.lower() else "Infrastruktur Umum",
                        "include": "yes",
                        "annotation_note": "Import CSV YouTube API v3"
                    })

    if records:
        df_new = pd.DataFrame(records)
        print(f"Berhasil mengonversi {len(df_new)} komentar YouTube!")
        # Append to existing
        if Path(output_csv).exists():
            df_old = pd.read_csv(output_csv, encoding='utf-8-sig')
            df_combined = pd.concat([df_old, df_new], ignore_index=True).drop_duplicates(subset=['text'])
            df_combined.to_csv(output_csv, index=False, encoding='utf-8-sig')
            print(f"Dataset {output_csv} kini memiliki total {len(df_combined)} data terintegrasi.")
        else:
            df_new.to_csv(output_csv, index=False, encoding='utf-8-sig')
    else:
        print("Tidak ada rekaman komentar yang berhasil diekstrak.")

if __name__ == '__main__':
    if len(sys.argv) > 1:
        ingest_youtube_file(sys.argv[1])
    else:
        print("Gunakan: python youtube_api_ingestor.py <file_youtube.json/csv>")

