"""
Test suite for autofig/db/database.py
Phase 2.0 — Database CRUD + round-trip
"""

import pytest
import sqlite3
import json
import tempfile
from pathlib import Path
from unittest.mock import patch

# Import from autofig.db
from autofig.db.database import (
    init_db, import_topology, hydrate_topology, 
    list_topologies, delete_topology, update_topology, DB_PATH
)


@pytest.fixture
def temp_db():
    """Use temp database for tests"""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / 'test.db'
        
        # Patch DB_PATH globally
        with patch('autofig.db.database.DB_PATH', db_path):
            init_db()
            yield db_path


@pytest.fixture
def sample_topology():
    """Sample topology dict"""
    return {
        'name': 'test_lab',
        'vendor': 'Cisco',
        'routing_protocol': 'ospf',
        'ssh': {
            'enabled': True,
            'username': 'admin',
            'enable_secret': 'test123',
            'generate_rsa_bits': 2048,
            'domain_name': 'lab.local'
        },
        'dns_servers': ['8.8.8.8', '8.8.4.4'],
        'ntp_servers': ['pool.ntp.org'],
        'devices': [
            {
                'name': 'router_1',
                'hostname': 'R1',
                'type': 'router',
                'interfaces': [
                    {'name': 'Gi0/0', 'ip': '10.0.1.1/24', 'vlan': 10}
                ]
            }
        ]
    }


class TestDatabaseInit:
    """Test database initialization"""
    
    def test_init_creates_database(self, temp_db):
        """Database file exists after init"""
        assert temp_db.exists()
    
    def test_init_creates_tables(self, temp_db):
        """All 5 tables created"""
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table'
        """)
        tables = {row[0] for row in cursor.fetchall()}
        
        expected = {'device_types', 'topologies', 'devices', 'generation_runs', 'generated_configs'}
        assert expected.issubset(tables)
        conn.close()
    
    def test_init_seeds_device_types(self, temp_db):
        """device_types table seeded with Cisco types"""
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM device_types WHERE vendor = 'cisco'")
        count = cursor.fetchone()[0]
        assert count >= 3  # router, switch, multilayer_switch
        conn.close()


class TestImportTopology:
    """Test import_topology()"""
    
    def test_import_creates_row(self, temp_db, sample_topology):
        """Topology imported successfully"""
        with patch('autofig.db.database.DB_PATH', temp_db):
            topology_id = import_topology(sample_topology)
            assert topology_id > 0
    
    def test_import_extracts_scalars(self, temp_db, sample_topology):
        """Scalar fields extracted to columns"""
        with patch('autofig.db.database.DB_PATH', temp_db):
            topology_id = import_topology(sample_topology)
            
            conn = sqlite3.connect(temp_db)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM topologies WHERE id = ?", (topology_id,))
            row = cursor.fetchone()
            
            assert row['name'] == 'test_lab'
            assert row['vendor'] == 'cisco'  # Lowercased
            assert row['routing_protocol'] == 'ospf'
            assert row['enable_password'] == 'test123'
            
            conn.close()
    
    def test_import_stores_json_blob(self, temp_db, sample_topology):
        """Nested config stored in JSON blob"""
        with patch('autofig.db.database.DB_PATH', temp_db):
            topology_id = import_topology(sample_topology)
            
            conn = sqlite3.connect(temp_db)
            cursor = conn.cursor()
            cursor.execute("SELECT global_config_json FROM topologies WHERE id = ?", (topology_id,))
            row = cursor.fetchone()
            
            blob = json.loads(row[0])
            assert 'devices' in blob
            assert blob['devices'][0]['name'] == 'router_1'
            
            conn.close()
    
    def test_import_lowercases_vendor(self, temp_db, sample_topology):
        """Vendor stored as lowercase"""
        with patch('autofig.db.database.DB_PATH', temp_db):
            topology_id = import_topology(sample_topology)
            
            conn = sqlite3.connect(temp_db)
            cursor = conn.cursor()
            cursor.execute("SELECT vendor FROM topologies WHERE id = ?", (topology_id,))
            vendor = cursor.fetchone()[0]
            
            assert vendor == 'cisco'
            conn.close()


class TestHydrateTopology:
    """Test hydrate_topology()"""
    
    def test_hydrate_reconstructs_dict(self, temp_db, sample_topology):
        """Hydrated dict reconstructed from DB"""
        with patch('autofig.db.database.DB_PATH', temp_db):
            topology_id = import_topology(sample_topology)
            recovered = hydrate_topology(topology_id)
            
            assert recovered['name'] == sample_topology['name']
            assert recovered['vendor'] == sample_topology['vendor'].lower()
            assert recovered['routing_protocol'] == sample_topology['routing_protocol']
    
    def test_hydrate_restores_ssh_config(self, temp_db, sample_topology):
        """SSH config restored from enable_password + blob"""
        with patch('autofig.db.database.DB_PATH', temp_db):
            topology_id = import_topology(sample_topology)
            recovered = hydrate_topology(topology_id)
            
            assert recovered['ssh']['enable_secret'] == 'test123'
            assert recovered['ssh']['username'] == 'admin'
    
    def test_hydrate_not_found(self, temp_db):
        """Raises error if topology not found"""
        with patch('autofig.db.database.DB_PATH', temp_db):
            with pytest.raises(ValueError):
                hydrate_topology(99999)


class TestRoundTrip:
    """Test round-trip: import → hydrate → equals original"""
    
    def test_round_trip_preserves_data(self, temp_db, sample_topology):
        """Full round-trip: dict → DB → dict"""
        with patch('autofig.db.database.DB_PATH', temp_db):
            # Import
            topology_id = import_topology(sample_topology)
            
            # Hydrate
            recovered = hydrate_topology(topology_id)
            
            # Compare key fields
            assert recovered['name'] == sample_topology['name']
            assert recovered['vendor'].lower() == sample_topology['vendor'].lower()
            assert recovered['routing_protocol'] == sample_topology['routing_protocol']
            assert recovered['devices'] == sample_topology['devices']


class TestListTopologies:
    """Test list_topologies()"""
    
    def test_list_returns_all(self, temp_db, sample_topology):
        """List returns all topologies"""
        with patch('autofig.db.database.DB_PATH', temp_db):
            # Import 3 topologies
            for i in range(3):
                topo = dict(sample_topology)
                topo['name'] = f'topology_{i}'
                import_topology(topo)
            
            topologies = list_topologies()
            assert len(topologies) == 3
    
    def test_list_sorted_descending(self, temp_db, sample_topology):
        """List sorted by created_at descending"""
        with patch('autofig.db.database.DB_PATH', temp_db):
            import_topology(dict(sample_topology, name='topo1'))
            import_topology(dict(sample_topology, name='topo2'))
            
            topologies = list_topologies()
            assert topologies[0]['name'] == 'topo2'  # Most recent first


class TestDeleteTopology:
    """Test delete_topology()"""
    
    def test_delete_removes_topology(self, temp_db, sample_topology):
        """Topology deleted"""
        with patch('autofig.db.database.DB_PATH', temp_db):
            topology_id = import_topology(sample_topology)
            assert delete_topology(topology_id)
            
            # Verify gone
            with pytest.raises(ValueError):
                hydrate_topology(topology_id)
    
    def test_delete_not_found(self, temp_db):
        """Delete returns False if not found"""
        with patch('autofig.db.database.DB_PATH', temp_db):
            assert not delete_topology(99999)


class TestUpdateTopology:
    """Test update_topology()"""
    
    def test_update_modifies_topology(self, temp_db, sample_topology):
        """Topology updated"""
        with patch('autofig.db.database.DB_PATH', temp_db):
            topology_id = import_topology(sample_topology)
            
            # Modify
            updated = dict(sample_topology)
            updated['name'] = 'modified_lab'
            updated['routing_protocol'] = 'bgp'
            
            assert update_topology(topology_id, updated)
            
            # Verify changed
            recovered = hydrate_topology(topology_id)
            assert recovered['name'] == 'modified_lab'
            assert recovered['routing_protocol'] == 'bgp'
    
    def test_update_not_found(self, temp_db, sample_topology):
        """Update returns False if not found"""
        with patch('autofig.db.database.DB_PATH', temp_db):
            assert not update_topology(99999, sample_topology)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
