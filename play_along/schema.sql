PRAGMA foreign_keys = ON;  -- must be set per connection for FKs/cascades to work

DROP TABLE IF EXISTS loop_regions;
DROP TABLE IF EXISTS audio_tracks;

CREATE TABLE audio_tracks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    youtube_id TEXT NOT NULL UNIQUE,
    artist TEXT NOT NULL,
    track_name TEXT NOT NULL,
    track_album TEXT NULL,
    thumbnail TEXT NULL,
    duration_sec INTEGER,
    blob_name TEXT NOT NULL UNIQUE,
    container TEXT NOT NULL DEFAULT 'play-along-app-audio-files',
    content_type TEXT DEFAULT 'audio/mpeg',
    uploaded_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE loop_regions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    audio_track_id INTEGER NOT NULL,
    label TEXT NULL,
    "start" REAL NOT NULL,
    "end" REAL NOT NULL,
    color TEXT NULL,
    CONSTRAINT FK_audiotracks_loopregions FOREIGN KEY (audio_track_id)
        REFERENCES audio_tracks (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- UNIQUE constraint for (audio_track_id, label)
CREATE UNIQUE INDEX IF NOT EXISTS idx_loop_regions_track_label
    ON loop_regions (audio_track_id, label);

-- Index the FK column for faster lookups/cascades
CREATE INDEX idx_loop_regions_audio_track_id ON loop_regions (audio_track_id);