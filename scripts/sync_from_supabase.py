"""
sync_from_supabase.py
從 Supabase 讀取資料，更新網站的 JSON 文件
用於 GitHub Actions 定時執行
"""
import os
import json
import requests
from datetime import datetime
from collections import Counter

# Supabase 設定（從環境變數讀取）
SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY')

def fetch_images():
    """從 Supabase 取得所有圖片資料"""
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError("請設定 SUPABASE_URL 和 SUPABASE_KEY 環境變數")

    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
    }

    # Supabase REST API - 取得所有資料
    url = f"{SUPABASE_URL}/rest/v1/images?select=*"
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    return response.json()

def generate_stats(images):
    """生成統計資料"""
    total = len(images)
    scored = sum(1 for img in images if img.get('score') is not None)
    with_prompt = sum(1 for img in images if img.get('prompt'))

    # 分數分佈
    score_dist = Counter()
    for img in images:
        if img.get('score') is not None:
            bucket = int(img['score'])
            score_dist[bucket] = score_dist.get(bucket, 0) + 1

    return {
        'total_images': total,
        'scored_images': scored,
        'with_prompt': with_prompt,
        'score_distribution': dict(sorted(score_dist.items())),
        'last_updated': datetime.now().isoformat(),
    }

def update_curated_json(images, output_path='site/data/curated.json'):
    """更新 curated.json（只包含高分圖片）"""
    # 篩選 score >= 6 的圖片
    high_quality = [
        img for img in images
        if img.get('score') is not None and img['score'] >= 6 and img.get('prompt')
    ]

    # 按分數排序
    high_quality.sort(key=lambda x: x['score'], reverse=True)

    # 轉換格式
    examples = []
    for img in high_quality:
        examples.append({
            'id': img['id'],
            'title': img.get('title', ''),
            'prompt': img.get('prompt', ''),
            'score': img.get('score'),
            'image': f"images/{img['id']}.jpg",
            'image_url': img.get('image_url', ''),
        })

    output = {
        'examples': examples,
        'metadata': {
            'total': len(examples),
            'last_updated': datetime.now().isoformat(),
            'source': 'supabase',
        }
    }

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    return len(examples)

def main():
    print("=== Supabase 同步開始 ===")
    print(f"時間: {datetime.now().isoformat()}")

    # 取得資料
    print("正在從 Supabase 取得資料...")
    images = fetch_images()
    print(f"取得 {len(images)} 筆資料")

    # 生成統計
    stats = generate_stats(images)
    print(f"統計: {stats['total_images']} 總圖片, {stats['scored_images']} 已評分")

    # 更新 curated.json
    count = update_curated_json(images)
    print(f"更新 curated.json: {count} 個高分範例")

    # 輸出統計檔案
    with open('site/data/stats.json', 'w', encoding='utf-8') as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
    print("已更新 stats.json")

    print("=== 同步完成 ===")

if __name__ == '__main__':
    main()
