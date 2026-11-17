BEGIN IMMEDIATE;
CREATE TABLE conversations (
 id TEXT PRIMARY KEY, title TEXT NOT NULL, personality TEXT NOT NULL,
 relationship TEXT NOT NULL, boundaries TEXT NOT NULL,
 settings_revision INTEGER NOT NULL CHECK(settings_revision>0),
 context_revision INTEGER NOT NULL CHECK(context_revision>0),
 gauges TEXT NOT NULL, emotion TEXT NOT NULL, created_at TEXT NOT NULL, updated_at TEXT NOT NULL
);
CREATE TABLE turns (
 sequence INTEGER PRIMARY KEY AUTOINCREMENT, id TEXT NOT NULL UNIQUE,
 conversation_id TEXT NOT NULL REFERENCES conversations(id), request_id TEXT NOT NULL,
 input TEXT NOT NULL, response TEXT NOT NULL, timestamp TEXT NOT NULL,
 settings_revision INTEGER NOT NULL, context_revision INTEGER NOT NULL,
 gauges TEXT NOT NULL, emotion TEXT NOT NULL, UNIQUE(conversation_id,request_id)
);
CREATE INDEX turns_conversation ON turns(conversation_id,sequence);
CREATE TABLE facts (
 id TEXT PRIMARY KEY, source_conversation_id TEXT NOT NULL REFERENCES conversations(id),
 source_turn_id TEXT REFERENCES turns(id), content TEXT,
 revision INTEGER NOT NULL CHECK(revision>0), created_at TEXT NOT NULL, updated_at TEXT NOT NULL
);
CREATE TABLE fact_grants (
 fact_id TEXT NOT NULL REFERENCES facts(id), conversation_id TEXT NOT NULL REFERENCES conversations(id),
 PRIMARY KEY(fact_id,conversation_id)
);
CREATE TABLE imports (
 checksum TEXT PRIMARY KEY, conversation_id TEXT NOT NULL REFERENCES conversations(id),
 schema_version INTEGER NOT NULL, completed_at TEXT NOT NULL, preserved_file TEXT NOT NULL
);
PRAGMA user_version=1;
COMMIT;
