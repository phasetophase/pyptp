"""Tests for THomeLS class."""

from __future__ import annotations

import unittest
from uuid import uuid4

from pyptp.elements.element_utils import NIL_GUID, Guid
from pyptp.elements.lv.connection import ConnectionLV
from pyptp.elements.lv.presentations import ElementPresentation
from pyptp.elements.lv.shared import CableType, FuseType
from pyptp.elements.mixins import Extra, Note
from pyptp.network_lv import NetworkLV


class TestTHomeLS(unittest.TestCase):
    """Test THomeLS registration and serialization behavior."""

    def setUp(self) -> None:
        """Create fresh network and dependencies for isolated testing."""
        self.network = NetworkLV()
        self.test_guid = Guid(uuid4())
        self.node_guid = Guid(uuid4())
        self.profile_guid = Guid(uuid4())

    def test_home_registration_works(self) -> None:
        """Verify basic home registration in network."""
        general = ConnectionLV.General(
            guid=self.test_guid, node=self.node_guid, name="Test Home"
        )
        home = ConnectionLV(general=general, presentations=[], gms=[])

        # Verify network starts empty
        self.assertEqual(len(self.network.homes), 0)

        # Register home
        home.register(self.network)

        # Verify home was added
        self.assertEqual(len(self.network.homes), 1)
        self.assertEqual(self.network.homes[self.test_guid], home)

    def test_home_with_minimal_properties_serializes_correctly(self) -> None:
        """Test serialization with minimal properties."""
        general = ConnectionLV.General(
            guid=self.test_guid, node=self.node_guid, name="Minimal Home"
        )
        home = ConnectionLV(general=general, presentations=[], gms=[])

        result = home.serialize()

        # Should contain general line
        self.assertIn("#General", result)
        self.assertIn(f"Node:'{{{str(self.node_guid).upper()}}}'", result)
        self.assertIn(f"GUID:'{{{str(self.test_guid).upper()}}}'", result)
        self.assertIn("Name:'Minimal Home'", result)

        # Default boolean values (True) appear in output (skip=False by default)
        self.assertIn("s_L1:True", result)
        self.assertIn("s_L2:True", result)
        self.assertIn("s_L3:True", result)
        self.assertIn("s_N:True", result)
        self.assertIn("s_PE:True", result)

        # Should not contain optional sections
        self.assertNotIn("#ConnectionCableType", result)
        self.assertNotIn("#FuseType", result)
        self.assertNotIn("#Load", result)
        self.assertNotIn("#PV", result)
        self.assertNotIn("#Battery", result)

    def test_home_with_full_properties_serializes_correctly(self) -> None:
        """Test serialization with all properties set."""
        general = ConnectionLV.General(
            guid=self.test_guid,
            node=self.node_guid,
            creation_time=1234567890.5,
            mutation_date=20240101,
            revision_date=1234567891.0,
            name="Full Home",
            s_L1=True,
            s_L2=False,
            s_L3=True,
            s_N=True,
            field_name="Field1",
            s_PE=False,
            k_L1=2,
            k_L2=3,
            k_L3=4,
            length=50.5,
            cable_type="YMVK 4x6",
            earthing_configuration="TT",
            s_Nh_PEh=True,
            s_PEh_PEh=False,
            s_PEh_e=True,
            re=10.5,
            s_Hh=False,
            s_h1_h3=True,
            s_h2_h4=True,
            phases=3,
            sort="Residential",
            connection_value="25A",
            i_earthleak=0.03,
            risk=True,
            geo_x_coord=123456.789,
            geo_y_coord=654321.123,
            address="123 Test Street",
            postal_code="12345",
            city="Test City",
        )

        # Add various subsections
        connection_cable = CableType(short_name="YMVK 4x6", unom=230, Inom0=25)

        fuse_type = FuseType(short_name="25A", unom=230, inom=25)

        load = ConnectionLV.Load(
            p1=2.5,
            q1=0.8,
            pa=0.8,
            qa=0.3,
            pb=0.9,
            qb=0.3,
            pc=0.8,
            qc=0.2,
            behaviour_sort="Constant",
            profile=self.profile_guid,
        )

        gm = ConnectionLV.GM(
            gm_type_number=2,
            p=3.5,
            cos=0.95,
            small_appliance_phases=3,
            net_aware_charging=True,
            adjustable=True,
        )

        pv = ConnectionLV.PV(
            scaling=1000,
            panel1_pnom=5000,
            panel1_orientation=180,
            panel1_slope=30,
            inverter_snom=5000,
            efficiency_type="High",
            phases=3,
            profile=self.profile_guid,
        )

        battery = ConnectionLV.Battery(
            pref=3000,
            state_of_charge=80,
            capacity=10000,
            crate=0.5,
            sort=1,
            inverter_snom=3000,
            charge_efficiency_type="Standard",
            discharge_efficiency_type="Standard",
            profile=self.profile_guid,
        )

        presentation = ElementPresentation(sheet=self.test_guid, x=100, y=200)

        home = ConnectionLV(
            general=general,
            presentations=[presentation],
            gms=[gm],
            connection_cable=connection_cable,
            fuse_type=fuse_type,
            load=load,
            pv=pv,
            battery=battery,
        )

        # Add extras and notes
        home.extras = [Extra(text="key1=value1")]
        home.notes = [Note(text="Test note")]

        result = home.serialize()

        # Verify general section
        self.assertIn("#General", result)
        self.assertIn(f"Node:'{{{str(self.node_guid).upper()}}}'", result)
        self.assertIn(f"GUID:'{{{str(self.test_guid).upper()}}}'", result)
        self.assertIn("CreationTime:1234567890.5", result)
        self.assertIn("MutationDate:20240101", result)
        self.assertIn("RevisionDate:1234567891", result)
        self.assertIn("Name:'Full Home'", result)
        self.assertNotIn("s_L2:", result)  # False values are skipped
        self.assertIn("FieldName:'Field1'", result)
        self.assertNotIn("s_PE:", result)  # False values are skipped
        self.assertIn("k_L1:2", result)
        self.assertIn("k_L2:3", result)
        self.assertIn("k_L3:4", result)
        self.assertIn("Length:50.5", result)
        self.assertIn("CableType:'YMVK 4x6'", result)
        self.assertIn("EarthingConfiguration:'TT'", result)
        self.assertIn("s_Nh_PEh:True", result)
        self.assertNotIn("s_PEh_PEh:", result)  # False values are skipped
        self.assertIn("s_PEh_e:True", result)
        self.assertIn("Re:10.5", result)
        self.assertNotIn("s_Hh:", result)  # False values are skipped
        self.assertIn("s_h1_h3:True", result)
        self.assertIn("s_h2_h4:True", result)
        self.assertIn("Phases:3", result)
        self.assertIn("Sort:'Residential'", result)
        self.assertIn("ConnectionValue:'25A'", result)
        self.assertIn("Iearthleak:0.03", result)
        self.assertIn("Risk:True", result)
        self.assertIn("GX:123456.789", result)
        self.assertIn("GY:654321.123", result)
        self.assertIn("Address:'123 Test Street'", result)
        self.assertIn("PostalCode:'12345'", result)
        self.assertIn("City:'Test City'", result)
        self.assertIn("ProtectionType:'25A'", result)

        # Verify subsections
        self.assertIn("#ConnectionCableType", result)
        self.assertIn("#FuseType", result)
        self.assertIn("#Load", result)
        self.assertIn("#GM", result)
        self.assertIn("#PV", result)
        self.assertIn("#Battery", result)
        self.assertIn("#Presentation", result)
        self.assertIn("#Extra Text:key1=value1", result)
        self.assertIn("#Note Text:Test note", result)

        # Verify load properties
        self.assertIn("P1:2.5", result)
        self.assertIn("Q1:0.8", result)
        self.assertIn("Pa:0.8", result)
        self.assertIn("Qa:0.3", result)
        self.assertIn("BehaviourSort:'Constant'", result)
        self.assertIn(f"Profile:'{{{str(self.profile_guid).upper()}}}'", result)

        # Verify GM properties
        self.assertIn("GMTypeNumber:2", result)
        self.assertIn("P:3.5", result)
        self.assertIn("Cos:0.95", result)
        self.assertIn("SmallAppliancePhases:3", result)
        self.assertIn("NetAwareCharging:True", result)
        self.assertIn("DownTuning:True", result)

        # Verify PV properties
        self.assertIn("Panel1Pnom:5000", result)
        self.assertIn("InverterSnom:5000", result)
        self.assertIn("EfficiencyType:'High'", result)

        # Verify battery properties
        self.assertIn("Pref:3000", result)
        self.assertIn("StateOfCharge:80", result)
        self.assertIn("Capacity:10000", result)
        self.assertIn("ChargeEfficiencyType:'Standard'", result)
        self.assertIn("DischargeEfficiencyType:'Standard'", result)

    def test_home_deserialization_works(self) -> None:
        """Test deserialization from GNF format data."""
        data = {
            "general": [
                {
                    "GUID": str(self.test_guid),
                    "Node": str(self.node_guid),
                    "Name": "Deserialized Home",
                    "CreationTime": 1234567890.0,
                    "Length": 25.5,
                    "CableType": "YMVK 4x6",
                    "Phases": 3,
                }
            ],
            "connection_cable": {"ShortName": "YMVK 4x6", "Unom": 230, "Inom0": 25},
            "fuse_type": {"ShortName": "25A", "Unom": 230, "Inom": 25},
            "load": {
                "P1": 2.5,
                "Q1": 0.8,
                "BehaviourSort": "Constant",
                "Profile": str(self.profile_guid),
            },
            "gms": [{"GMTypeNumber": 2, "P": 3.5, "Cos": 0.95}],
            "pv": {"Panel1Pnom": 5000, "InverterSnom": 5000, "EfficiencyType": "High"},
            "presentations": [
                {"Sheet": str(self.test_guid), "X": 100, "Y": 200, "Symbol": 12}
            ],
        }

        home = ConnectionLV.deserialize(data)

        # Verify general properties
        self.assertEqual(home.general.guid, self.test_guid)
        self.assertEqual(home.general.node, self.node_guid)
        self.assertEqual(home.general.name, "Deserialized Home")
        self.assertEqual(home.general.creation_time, 1234567890.0)
        self.assertEqual(home.general.length, 25.5)
        self.assertEqual(home.general.cable_type, "YMVK 4x6")
        self.assertEqual(home.general.phases, 3)

        # Verify connection cable
        self.assertIsNotNone(home.connection_cable)
        if home.connection_cable:
            self.assertEqual(home.connection_cable.short_name, "YMVK 4x6")
            self.assertEqual(home.connection_cable.unom, 230)
            self.assertEqual(home.connection_cable.Inom0, 25)

        # Verify fuse type
        self.assertIsNotNone(home.fuse_type)
        if home.fuse_type:
            self.assertEqual(home.fuse_type.short_name, "25A")
            self.assertEqual(home.fuse_type.unom, 230)
            self.assertEqual(home.fuse_type.inom, 25)

        # Verify load
        self.assertIsNotNone(home.load)
        if home.load:
            self.assertEqual(home.load.p1, 2.5)
            self.assertEqual(home.load.q1, 0.8)
            self.assertEqual(home.load.behaviour_sort, "Constant")
            self.assertEqual(home.load.profile, self.profile_guid)

        # Verify GM
        self.assertEqual(len(home.gms), 1)
        self.assertEqual(home.gms[0].gm_type_number, 2)
        self.assertEqual(home.gms[0].p, 3.5)
        self.assertEqual(home.gms[0].cos, 0.95)

        # Verify PV
        self.assertIsNotNone(home.pv)
        if home.pv:
            self.assertEqual(home.pv.panel1_pnom, 5000)
            self.assertEqual(home.pv.inverter_snom, 5000)
            self.assertEqual(home.pv.efficiency_type, "High")

        # Verify presentations
        self.assertEqual(len(home.presentations), 1)
        self.assertEqual(home.presentations[0].sheet, self.test_guid)
        self.assertEqual(home.presentations[0].x, 100)
        self.assertEqual(home.presentations[0].y, 200)

    def test_home_deserialization_with_empty_data(self) -> None:
        """Test deserialization with empty data."""
        data = {}

        home = ConnectionLV.deserialize(data)

        # Should have default general properties
        self.assertIsNotNone(home.general)
        self.assertEqual(home.general.name, "")
        self.assertEqual(home.general.creation_time, 0)
        self.assertEqual(home.general.node, NIL_GUID)
        self.assertEqual(home.general.s_L1, True)
        self.assertEqual(home.general.s_L2, True)
        self.assertEqual(home.general.s_L3, True)
        self.assertEqual(home.general.s_N, True)
        self.assertEqual(home.general.s_PE, True)
        self.assertEqual(home.general.k_L1, 1)
        self.assertEqual(home.general.k_L2, 2)
        self.assertEqual(home.general.k_L3, 3)
        self.assertEqual(home.general.length, 0.0)
        self.assertEqual(home.general.phases, 4)

        # Optional sections should be None or empty
        self.assertIsNone(home.connection_cable)
        self.assertIsNone(home.fuse_type)
        self.assertIsNone(home.load)
        self.assertIsNone(home.pv)
        self.assertIsNone(home.battery)
        self.assertEqual(len(home.gms), 0)
        self.assertEqual(len(home.presentations), 0)

    def test_duplicate_home_registration_overwrites(self) -> None:
        """Test GUID collision handling with proper logging verification."""
        general1 = ConnectionLV.General(guid=self.test_guid, name="Home 1")
        general2 = ConnectionLV.General(guid=self.test_guid, name="Home 2")

        home1 = ConnectionLV(general=general1, presentations=[], gms=[])
        home2 = ConnectionLV(general=general2, presentations=[], gms=[])

        # Register first home
        home1.register(self.network)
        self.assertEqual(self.network.homes[self.test_guid].general.name, "Home 1")

        # Register second home with same GUID should overwrite
        home2.register(self.network)
        # Verify home was overwritten
        self.assertEqual(self.network.homes[self.test_guid].general.name, "Home 2")

    def test_home_general_serialize_with_defaults(self) -> None:
        """Test General class serialization with default values."""
        general = ConnectionLV.General(
            guid=self.test_guid, node=self.node_guid, name="Test Home"
        )

        result = general.serialize()

        # Should include required fields
        self.assertIn(f"Node:'{{{str(self.node_guid).upper()}}}'", result)
        self.assertIn(f"GUID:'{{{str(self.test_guid).upper()}}}'", result)
        self.assertIn("Name:'Test Home'", result)

        # CreationTime uses no_skip so it always appears
        self.assertIn("CreationTime:", result)

        # Should skip default values
        self.assertNotIn("MutationDate:", result)
        self.assertNotIn("RevisionDate:", result)
        self.assertIn("s_L1:True", result)  # True values appear
        self.assertIn("s_L2:True", result)  # True values appear
        self.assertIn("s_L3:True", result)  # True values appear
        self.assertIn("s_N:True", result)  # True values appear
        self.assertIn("s_PE:True", result)  # True values appear
        self.assertNotIn("k_L1:", result)  # 1 is default
        self.assertNotIn("k_L2:", result)  # 2 is default
        self.assertNotIn("k_L3:", result)  # 3 is default
        self.assertNotIn("Length:", result)  # 0.0 is default
        self.assertNotIn("Phases:", result)  # 4 is default

    def test_home_load_serialize_with_defaults(self) -> None:
        """Test Load class serialization with default values."""
        load = ConnectionLV.Load()

        result = load.serialize()

        # Should skip default values (all 0.0)
        self.assertNotIn("P1:", result)
        self.assertNotIn("Q1:", result)
        self.assertNotIn("Pa:", result)
        self.assertNotIn("Qa:", result)
        self.assertNotIn("Profile:", result)  # DEFAULT_PROFILE_GUID should be skipped

    def test_home_load_serialize_with_values(self) -> None:
        """Test Load class serialization with values."""
        load = ConnectionLV.Load(
            p1=2.5, q1=0.8, behaviour_sort="Constant", profile=self.profile_guid
        )

        result = load.serialize()

        self.assertIn("P1:2.5", result)
        self.assertIn("Q1:0.8", result)
        self.assertIn("BehaviourSort:'Constant'", result)
        self.assertIn(f"Profile:'{{{str(self.profile_guid).upper()}}}'", result)

    def test_home_gm_serialize_with_defaults(self) -> None:
        """Test GM class serialization with default values."""
        gm = ConnectionLV.GM()

        result = gm.serialize()

        # Should skip default values
        self.assertNotIn("GMTypeNumber:", result)  # 1 is default
        self.assertNotIn("P:", result)  # 0.0 is default
        self.assertNotIn("Cos:", result)  # 1.0 is default
        self.assertNotIn("SmallAppliancePhases:", result)  # 1 is default
        self.assertNotIn("NetAwareCharging:", result)  # False is default
        self.assertNotIn("DownTuning:", result)  # False is default

    def test_home_pv_serialize_with_defaults(self) -> None:
        """Test PV class serialization with default values."""
        pv = ConnectionLV.PV()

        result = pv.serialize()

        # Should skip default values
        self.assertNotIn("Scaling:", result)  # 1000 is default
        self.assertNotIn("Panel1Pnom:", result)  # 0 is default
        self.assertNotIn("Panel1Orientation:", result)  # 180 is default
        self.assertNotIn("Panel1Slope:", result)  # 30 is default
        self.assertNotIn("InverterSnom:", result)  # 30 is default
        self.assertNotIn("Phases:", result)  # 1 is default
        self.assertNotIn("Profile:", result)  # DEFAULT_PROFILE_GUID should be skipped

    def test_home_battery_serialize_with_defaults(self) -> None:
        """Test Battery class serialization with default values."""
        battery = ConnectionLV.Battery()

        result = battery.serialize()

        # Should skip default values
        self.assertNotIn("Pref:", result)  # 0.0 is default
        self.assertNotIn("StateOfCharge:", result)  # 50 is default
        self.assertNotIn("Capacity:", result)  # 0 is default
        self.assertNotIn("Crate:", result)  # 0.5 is default
        self.assertNotIn("Sort:", result)  # 0 is default
        self.assertNotIn("Profile:", result)  # DEFAULT_PROFILE_GUID should be skipped

    def test_home_geography_serialize_with_empty_coordinates(self) -> None:
        """Test Geography class serialization with empty coordinates."""
        geo = ConnectionLV.Geography()

        result = geo.serialize()

        # Should be empty string for empty coordinates
        self.assertEqual(result, "")

    def test_home_geography_serialize_with_coordinates(self) -> None:
        """Test Geography class serialization with coordinates."""
        geo = ConnectionLV.Geography(coordinates=[(100.0, 200.0), (300.0, 400.0)])

        result = geo.serialize()

        self.assertEqual(result, "Coordinates:'{(100,0 200,0) (300,0 400,0) }'")

    def test_home_round_trip_serialization(self) -> None:
        """Test that serialization and deserialization are consistent."""
        original_general = ConnectionLV.General(
            guid=self.test_guid,
            node=self.node_guid,
            name="Round Trip Home",
            creation_time=1234567890.0,
            length=25.5,
            cable_type="YMVK 4x6",
            phases=3,
        )

        original_load = ConnectionLV.Load(p1=2.5, q1=0.8, behaviour_sort="Constant")

        original_gm = ConnectionLV.GM(gm_type_number=2, p=3.5, cos=0.95)

        original_home = ConnectionLV(
            general=original_general,
            presentations=[],
            gms=[original_gm],
            load=original_load,
        )

        original_home.serialize()

        # Simulate parsing back from GNF format
        data = {
            "general": [
                {
                    "GUID": str(self.test_guid),
                    "Node": str(self.node_guid),
                    "Name": "Round Trip Home",
                    "CreationTime": 1234567890.0,
                    "Length": 25.5,
                    "CableType": "YMVK 4x6",
                    "Phases": 3,
                }
            ],
            "load": {"P1": 2.5, "Q1": 0.8, "BehaviourSort": "Constant"},
            "gms": [{"GMTypeNumber": 2, "P": 3.5, "Cos": 0.95}],
        }

        deserialized = ConnectionLV.deserialize(data)

        # Verify key properties match
        self.assertEqual(deserialized.general.guid, original_home.general.guid)
        self.assertEqual(deserialized.general.node, original_home.general.node)
        self.assertEqual(deserialized.general.name, original_home.general.name)
        self.assertEqual(
            deserialized.general.creation_time, original_home.general.creation_time
        )
        self.assertEqual(deserialized.general.length, original_home.general.length)
        self.assertEqual(
            deserialized.general.cable_type, original_home.general.cable_type
        )
        self.assertEqual(deserialized.general.phases, original_home.general.phases)

        # Verify load properties
        if deserialized.load and original_home.load:
            self.assertEqual(deserialized.load.p1, original_home.load.p1)
            self.assertEqual(deserialized.load.q1, original_home.load.q1)
            self.assertEqual(
                deserialized.load.behaviour_sort, original_home.load.behaviour_sort
            )

        # Verify GM properties
        self.assertEqual(len(deserialized.gms), len(original_home.gms))
        self.assertEqual(
            deserialized.gms[0].gm_type_number, original_home.gms[0].gm_type_number
        )
        self.assertEqual(deserialized.gms[0].p, original_home.gms[0].p)
        self.assertEqual(deserialized.gms[0].cos, original_home.gms[0].cos)


if __name__ == "__main__":
    unittest.main()
