-- Initialize DeepGrep PostgreSQL database

-- Create search_history table with indexes
CREATE TABLE IF NOT EXISTS search_history (
    id SERIAL PRIMARY KEY,
    pattern VARCHAR(500) NOT NULL,
    search_type VARCHAR(50) DEFAULT 'regex',
    matches_count INTEGER DEFAULT 0,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    files TEXT
);

CREATE INDEX IF NOT EXISTS idx_pattern_timestamp ON search_history(pattern, timestamp);
CREATE INDEX IF NOT EXISTS idx_search_type_timestamp ON search_history(search_type, timestamp);
CREATE INDEX IF NOT EXISTS idx_timestamp ON search_history(timestamp DESC);

-- Create documents table with indexes
CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    title VARCHAR(500),
    source VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata TEXT
);

CREATE INDEX IF NOT EXISTS idx_title ON documents(title);
CREATE INDEX IF NOT EXISTS idx_source ON documents(source);
CREATE INDEX IF NOT EXISTS idx_created_at ON documents(created_at DESC);

-- Create full-text search index on documents
CREATE INDEX IF NOT EXISTS idx_content_fts ON documents USING gin(to_tsvector('english', content));

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO deepgrep;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO deepgrep;
