CREATE TABLE visual_identities (
 conversation_id TEXT PRIMARY KEY REFERENCES conversations(id) ON DELETE CASCADE,
 revision INTEGER NOT NULL DEFAULT 1 CHECK(revision > 0),
 configuration TEXT,
 approved_portrait_asset TEXT REFERENCES visual_assets(id) ON DELETE SET NULL
);
CREATE TABLE scene_policies (
 conversation_id TEXT PRIMARY KEY REFERENCES conversations(id) ON DELETE CASCADE,
 revision INTEGER NOT NULL DEFAULT 1 CHECK(revision > 0),
 enabled INTEGER NOT NULL DEFAULT 0 CHECK(enabled IN (0,1)),
 cooldown_seconds INTEGER NOT NULL DEFAULT 300 CHECK(cooldown_seconds BETWEEN 60 AND 3600),
 last_enqueue REAL
);
CREATE TABLE render_jobs (
 sequence INTEGER PRIMARY KEY AUTOINCREMENT,
 id TEXT NOT NULL UNIQUE,
 conversation_id TEXT NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
 request_id TEXT NOT NULL,
 kind TEXT NOT NULL CHECK(kind IN ('portrait','manual','automatic')),
 description TEXT NOT NULL CHECK(length(description) BETWEEN 1 AND 2000),
 settings_revision INTEGER NOT NULL,
 context_revision INTEGER NOT NULL,
 identity_revision INTEGER NOT NULL,
 workflow_digest TEXT NOT NULL,
 output_node TEXT NOT NULL,
 renderer_key TEXT NOT NULL,
 originating_turn TEXT REFERENCES turns(id) ON DELETE CASCADE,
 renderer_id TEXT UNIQUE,
 discard_reason TEXT,
 state TEXT NOT NULL CHECK(state IN ('queued','submitting','running','cancel_requested','succeeded','failed','cancelled','uncertain')),
 error TEXT,
 created_at TEXT NOT NULL,
 updated_at TEXT NOT NULL,
 UNIQUE(conversation_id, request_id),
 UNIQUE(conversation_id, id)
);
CREATE UNIQUE INDEX render_one_active ON render_jobs ((1))
 WHERE state IN ('submitting','running','cancel_requested','uncertain');
CREATE UNIQUE INDEX render_one_auto_queued ON render_jobs (conversation_id)
 WHERE state='queued' AND kind='automatic';
CREATE INDEX render_conversation_history ON render_jobs (conversation_id, sequence);
CREATE TABLE visual_assets (
 id TEXT PRIMARY KEY,
 conversation_id TEXT NOT NULL,
 job_id TEXT NOT NULL UNIQUE,
 media_type TEXT NOT NULL CHECK(media_type IN ('image/png','image/jpeg','image/webp')),
 bytes INTEGER NOT NULL CHECK(bytes BETWEEN 1 AND 20971520),
 width INTEGER NOT NULL CHECK(width BETWEEN 1 AND 8192),
 height INTEGER NOT NULL CHECK(height BETWEEN 1 AND 8192),
 checksum TEXT NOT NULL,
 rejected INTEGER NOT NULL DEFAULT 0 CHECK(rejected IN (0,1)),
 FOREIGN KEY(conversation_id, job_id) REFERENCES render_jobs(conversation_id,id) ON DELETE CASCADE
);
CREATE TABLE render_handoff (
 singleton INTEGER PRIMARY KEY CHECK(singleton=1),
 renderer_key TEXT NOT NULL,
 barrier_id TEXT,
 phase INTEGER NOT NULL DEFAULT 0 CHECK(phase BETWEEN 0 AND 2)
);
PRAGMA user_version=2;
