DROP TABLE IF EXISTS audio_tracks;

CREATE TABLE audio_tracks (
    id INT IDENTITY(1,1) PRIMARY KEY,
    youtube_id NVARCHAR(255) NOT NULL,
    artist NVARCHAR(255) NOT NULL,
    track_name NVARCHAR(255) NOT NULL,
    track_album NVARCHAR(255) NULL,
    thumbnail NVARCHAR(MAX) NULL,
    duration_sec INT,
    blob_name NVARCHAR(512) NOT NULL UNIQUE,
    container NVARCHAR(63) NOT NULL DEFAULT 'play-along-app-audio-files',
    content_type NVARCHAR(100) DEFAULT 'audio/mpeg',
    uploaded_at DATETIME2 DEFAULT SYSUTCDATETIME()
);

ALTER TABLE audio_tracks
ADD CONSTRAINT AK_youtube_id UNIQUE(youtube_id);

-- TODO: CREATE TABLE FOR TRACK TIMESTAMPS WITH LOOPS AND OTHER FEATURES