"""
Autofig Database Layer
Phase 2.0 — Topology persistence via SQLite
"""

import sqlite3
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)

# Database location: ~/.autofig/topologies.db
DB_PATH = Path.home() / '.autofig' / 'topologies.db'


def init_db():
    """Initialize database from schema.sql"""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    
    # Load and execute schema
    schema_path = Path(__file__).parent / 'schema.sql'
    with open(schema_path) as f:
        conn.executescript(f.read())
    
    # Seed device_types from YAML files
    seed_device_types(conn)
    
    conn.commit()
    conn.close()
    logger.info(f"Database initialized at {DB_PATH}")


def seed_device_types(conn):
    """Seed device_types table from autofig/data/devices/*.yaml"""
    # This is a placeholder — in real implementation, scan data/devices/ folder
    # and insert device_type rows. For now, manually add the three we know about:
    
    device_types = [
        ('cisco', 'router_cisco', 'router', 'router.j2', 'data/devices/router_cisco.yaml'),
        ('cisco', 'switch_cisco', 'switch', 'switch.j2', 'data/devices/switch_cisco.yaml'),
        ('cisco', 'multilayer_switch_cisco', 'multilayer_switch', 'multilayer_switch.j2', 'data/devices/multilayer_switch_cisco.yaml'),
    ]
    
    cursor = conn.cursor()
    for vendor, slug, role, template, path in device_types:
        cursor.execute("""
            INSERT OR IGNORE INTO device_types (vendor, slug, role, template_file, defaults_path)
            VALUES (?, ?, ?, ?, ?)
        """, (vendor, slug, role, template, path))


def import_topology(topology_dict: Dict[str, Any]) -> int:
    """
    Save topology to database.
    
    Extracts scalar fields (name, vendor, routing_protocol, enable_password)
    to columns, puts the rest in global_config_json blob.
    
    Returns: topology ID
    """
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    
    try:
        # Extract scalar fields
        name = topology_dict.get('name', 'untitled')
        vendor = topology_dict.get('vendor', 'cisco').lower()
        routing_protocol = topology_dict.get('routing_protocol', 'static')
        enable_password = topology_dict.get('ssh', {}).get('enable_secret', '')
        
        # Prepare global_config_json (everything else)
        global_config = {
            k: v for k, v in topology_dict.items()
            if k not in ['name', 'vendor', 'routing_protocol']
        }
        global_config_json = json.dumps(global_config)
        
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO topologies 
            (name, vendor, routing_protocol, enable_password, global_config_json, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            name, vendor, routing_protocol, enable_password, 
            global_config_json,
            datetime.now().isoformat(),
            datetime.now().isoformat()
        ))
        
        topology_id = cursor.lastrowid
        conn.commit()
        logger.info(f"Topology '{name}' (ID {topology_id}) imported")
        return topology_id
        
    except sqlite3.Error as e:
        conn.rollback()
        logger.error(f"Failed to import topology: {e}")
        raise
    finally:
        conn.close()


def hydrate_topology(topology_id: int) -> Dict[str, Any]:
    """
    Load topology from database, return as dict.
    
    Reconstructs the exact shape that load_yaml() produces by combining
    scalar columns with the global_config_json blob.
    
    Returns: topology dict
    Raises: ValueError if topology not found
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM topologies WHERE id = ?", (topology_id,))
        row = cursor.fetchone()
        
        if not row:
            raise ValueError(f"Topology {topology_id} not found")
        
        # Reconstruct dict
        topology_dict = json.loads(row['global_config_json'])
        topology_dict['name'] = row['name']
        topology_dict['vendor'] = row['vendor']
        topology_dict['routing_protocol'] = row['routing_protocol']
        
        if row['enable_password']:
            if 'ssh' not in topology_dict:
                topology_dict['ssh'] = {}
            topology_dict['ssh']['enable_secret'] = row['enable_password']
        
        logger.info(f"Topology '{row['name']}' (ID {topology_id}) hydrated")
        return topology_dict
        
    finally:
        conn.close()


def list_topologies() -> List[Dict[str, Any]]:
    """
    List all saved topologies.
    
    Returns: List of dicts with id, name, vendor, routing_protocol, created_at
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, name, vendor, routing_protocol, created_at 
            FROM topologies 
            ORDER BY created_at DESC
        """)
        
        return [dict(row) for row in cursor.fetchall()]
        
    finally:
        conn.close()


def delete_topology(topology_id: int) -> bool:
    """
    Delete topology and all cascading data.
    
    Returns: True if deleted, False if not found
    """
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM topologies WHERE id = ?", (topology_id,))
        conn.commit()
        
        if cursor.rowcount == 0:
            logger.warning(f"Topology {topology_id} not found")
            return False
        
        logger.info(f"Topology {topology_id} deleted (cascading)")
        return True
        
    except sqlite3.Error as e:
        conn.rollback()
        logger.error(f"Failed to delete topology: {e}")
        raise
    finally:
        conn.close()


def update_topology(topology_id: int, topology_dict: Dict[str, Any]) -> bool:
    """
    Update an existing topology.
    
    Deletes and re-inserts (simpler than partial updates).
    
    Returns: True if updated, False if not found
    """
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    
    try:
        # Get original name for reference
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM topologies WHERE id = ?", (topology_id,))
        row = cursor.fetchone()
        
        if not row:
            return False
        
        # Delete old
        cursor.execute("DELETE FROM topologies WHERE id = ?", (topology_id,))
        
        # Re-insert with updated data
        name = topology_dict.get('name', row[0])
        vendor = topology_dict.get('vendor', 'cisco').lower()
        routing_protocol = topology_dict.get('routing_protocol', 'static')
        enable_password = topology_dict.get('ssh', {}).get('enable_secret', '')
        
        global_config = {
            k: v for k, v in topology_dict.items()
            if k not in ['name', 'vendor', 'routing_protocol']
        }
        
        cursor.execute("""
            INSERT INTO topologies 
            (id, name, vendor, routing_protocol, enable_password, global_config_json, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            topology_id, name, vendor, routing_protocol, enable_password,
            json.dumps(global_config),
            row[0] if row else datetime.now().isoformat(),
            datetime.now().isoformat()
        ))
        
        conn.commit()
        logger.info(f"Topology {topology_id} updated")
        return True
        
    except sqlite3.Error as e:
        conn.rollback()
        logger.error(f"Failed to update topology: {e}")
        raise
    finally:
        conn.close()


def get_topology(topology_id: int) -> Optional[Dict[str, Any]]:
    """Get topology metadata (not hydrated dict)."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM topologies WHERE id = ?", (topology_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()
