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

DROP TABLE IF EXISTS loop_regions;

CREATE TABLE loop_regions (
    id INT IDENTITY(1,1) PRIMARY KEY,
    audio_track_id INT NOT NULL,
    label NVARCHAR(255) NULL,
    [start] FLOAT NOT NULL,
    [end] FLOAT NOT NULL
);

ALTER TABLE loop_regions
ADD CONSTRAINT FK_audiotracks_loopregions FOREIGN KEY (audio_track_id)
REFERENCES audio_tracks (id)
    ON DELETE CASCADE
    ON UPDATE CASCADE;

-- TODO: CREATE TABLE FOR TRACK TIMESTAMPS WITH LOOPS AND OTHER FEATURES