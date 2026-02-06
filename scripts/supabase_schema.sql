-- Supabase Schema for UniformMap
-- 在 Supabase SQL Editor 中執行此腳本

CREATE TABLE IF NOT EXISTS images (
    id TEXT PRIMARY KEY,
    title TEXT,
    url TEXT,
    image_url TEXT,
    local_image TEXT,
    prompt TEXT,
    score REAL,
    scraped_at TIMESTAMP,
    scored_at TIMESTAMP
);

-- 建立索引加速查詢
CREATE INDEX IF NOT EXISTS idx_images_score ON images(score);
CREATE INDEX IF NOT EXISTS idx_images_scraped_at ON images(scraped_at);

-- 啟用 Row Level Security（可選，增加安全性）
ALTER TABLE images ENABLE ROW LEVEL SECURITY;

-- 允許匿名讀取（GitHub Actions 需要）
CREATE POLICY "Allow anonymous read" ON images
    FOR SELECT USING (true);
