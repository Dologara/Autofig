-- ============================================================================
-- Autofig Phase 2.0 — Database Schema (hybrid design)
-- ============================================================================
-- 5 tables: device_types, topologies, devices, generation_runs, generated_configs
--
-- Design principle: real columns for anything you'd filter/query/report on
-- independent of one specific topology (name, vendor, routing protocol,
-- generation history); one JSON blob for everything with variable, deeply
-- nested shape that current Autofig has no query use case for yet
-- (interfaces, static routes, SVIs, SSH block, VLAN list).
--
-- hydrate_topology(id) reconstructs the exact dict shape load_yaml() already
-- produces by combining the scalar columns with json.loads() on the blobs.
-- Because the blob already IS most of the topology dict, there is no
-- multi-table JOIN to get subtly wrong — the round-trip is structural, not
-- something a test has to prove.
-- ============================================================================


-- ----------------------------------------------------------------------------
-- 1. device_types — catalog, seeded from autofig/data/devices/*.yaml
-- ----------------------------------------------------------------------------
-- Not user data. init_db() scans data/devices/ at startup and upserts rows
-- here so `devices.device_type_id` has a real FK target instead of a loose
-- string. The YAML files stay the editable source of truth; this table is a
-- queryable mirror of them.
--
-- vendor is CHECK'd lowercase because this exact project has shipped a
-- "Cisco" vs "cisco" bug twice already (vendors.py, then independently
-- processor.py) — this makes the canonical-lowercase rule an enforced
-- invariant instead of a convention someone has to remember.
CREATE TABLE device_types (
    id              INTEGER PRIMARY KEY,
    vendor          TEXT NOT NULL CHECK (vendor = LOWER(vendor)),
    slug            TEXT NOT NULL,          -- 'router_cisco'
    role            TEXT NOT NULL CHECK (role IN ('router', 'switch', 'multilayer_switch')),
    template_file   TEXT NOT NULL,          -- 'router.j2'
    defaults_path   TEXT,                   -- 'data/devices/router_cisco.yaml'
    UNIQUE (vendor, slug)
);
CREATE INDEX idx_device_types_vendor ON device_types (vendor);


-- ----------------------------------------------------------------------------
-- 2. topologies — the top-level container
-- ----------------------------------------------------------------------------
-- Scalars: fields worth a WHERE clause on their own ("which topologies use
-- OSPF", "find by name") or that are simple 1:1 values already sitting at
-- the top of the YAML. enable_password gets a real column — the original
-- NetBox-derived draft omitted it entirely, which would have silently
-- broken round-trip for any topology that sets one.
--
-- global_config_json carries: vlans (topology-level VLAN definitions), the
-- full ssh block (enable/username/password/generate_rsa_bits/domain_name),
-- dns_servers, ntp_servers, syslog_servers — exactly the shape
-- yaml_builder.py already produces for these, no decomposition needed.
CREATE TABLE topologies (
    id                  INTEGER PRIMARY KEY,
    name                TEXT NOT NULL UNIQUE,
    description         TEXT,
    vendor              TEXT NOT NULL DEFAULT 'cisco' CHECK (vendor = LOWER(vendor)),
    routing_protocol    TEXT NOT NULL DEFAULT 'static'
                        CHECK (routing_protocol IN ('static', 'ospf', 'bgp')),
    default_gateway     TEXT,
    domain_name         TEXT,
    enable_password     TEXT,               -- plaintext by design; see note below
    global_config_json  TEXT NOT NULL DEFAULT '{}',
    created_at          TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at          TEXT NOT NULL DEFAULT (datetime('now')),
    CHECK (json_valid(global_config_json))
);

-- updated_at doesn't update itself — a trigger is one less thing every write
-- path has to remember to do correctly.
CREATE TRIGGER trg_topologies_updated_at
AFTER UPDATE ON topologies
FOR EACH ROW
WHEN NEW.updated_at = OLD.updated_at   -- don't fight an explicit caller-set value
BEGIN
    UPDATE topologies SET updated_at = datetime('now') WHERE id = NEW.id;
END;


-- ----------------------------------------------------------------------------
-- 3. devices — one row per device in a topology
-- ----------------------------------------------------------------------------
-- device_type_id gives you vendor + role + which template to render, without
-- devices duplicating a vendor string that could drift from its type.
--
-- config_json carries: interfaces (shape differs for router vs switch vs
-- L3 switch), static_routes (routers), ip_routing + vlans/SVIs (L3
-- switches) — i.e. everything that's genuinely device-type-shaped and that
-- nothing today needs to query across devices.
--
-- Two UNIQUE constraints: name is the internal slug (used for config
-- filenames — "R1_config.txt" comes from device.name), hostname is what
-- ends up in the actual config. Both should be unique per topology; a
-- hostname collision is a real network misconfiguration worth catching at
-- the DB layer, not just a filename collision.
CREATE TABLE devices (
    id              INTEGER PRIMARY KEY,
    topology_id     INTEGER NOT NULL REFERENCES topologies(id) ON DELETE CASCADE,
    device_type_id  INTEGER NOT NULL REFERENCES device_types(id),
    name            TEXT NOT NULL,          -- 'r1' — internal key, used in filenames
    hostname        TEXT NOT NULL,          -- 'R1' — what goes in the config
    sort_order      INTEGER NOT NULL DEFAULT 0,
    config_json     TEXT NOT NULL DEFAULT '{}',
    UNIQUE (topology_id, name),
    UNIQUE (topology_id, hostname),
    CHECK (json_valid(config_json))
);
CREATE INDEX idx_devices_topology ON devices (topology_id, sort_order);

-- ON DELETE CASCADE from topology, but NOT from device_type_id — deleting a
-- device type that's still referenced by devices should fail loudly (SQLite
-- raises a foreign key constraint error), not silently orphan rows.


-- ----------------------------------------------------------------------------
-- 4. generation_runs — one row per `autofig generate` invocation
-- ----------------------------------------------------------------------------
-- Maps directly onto the dict render_topology_with_errors() already
-- returns: status, generated count, total_devices, errors. No new shape
-- to invent — this table just persists what that function already computes.
CREATE TABLE generation_runs (
    id            INTEGER PRIMARY KEY,
    topology_id   INTEGER NOT NULL REFERENCES topologies(id) ON DELETE CASCADE,
    started_at    TEXT NOT NULL DEFAULT (datetime('now')),
    status        TEXT NOT NULL CHECK (status IN ('success', 'partial_success', 'failure')),
    output_dir    TEXT,
    device_count  INTEGER NOT NULL DEFAULT 0,
    error_count   INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX idx_runs_topology ON generation_runs (topology_id, started_at DESC);


-- ----------------------------------------------------------------------------
-- 5. generated_configs — the actual rendered text, one row per device per run
-- ----------------------------------------------------------------------------
-- device_id uses ON DELETE SET NULL (not CASCADE) — if a device is later
-- removed from a topology, its config history should survive; you just lose
-- the FK link back to a live device row.
--
-- checksum (sha256 of config_text) exists for two things: cheap diffing
-- between runs, and — worth actually using this once you write the insert
-- logic — skipping a new row entirely when a device's config is byte-
-- identical to its immediately-previous run, so re-running `generate`
-- repeatedly on an unchanged topology doesn't grow this table forever.
CREATE TABLE generated_configs (
    id           INTEGER PRIMARY KEY,
    run_id       INTEGER NOT NULL REFERENCES generation_runs(id) ON DELETE CASCADE,
    device_id    INTEGER REFERENCES devices(id) ON DELETE SET NULL,
    filename     TEXT NOT NULL,
    config_text  TEXT NOT NULL,
    checksum     TEXT NOT NULL
);
CREATE INDEX idx_configs_run ON generated_configs (run_id);

-- This index is the one the original NetBox-derived draft was missing.
-- "Diff R1's config across runs" — the feature this whole table exists for
-- — filters by device_id, not run_id. Without this, that query table-scans.
CREATE INDEX idx_configs_device ON generated_configs (device_id, run_id DESC);
