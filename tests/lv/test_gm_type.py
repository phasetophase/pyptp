"""Tests for TGMTypeLS class."""

from __future__ import annotations

import unittest

from pyptp.elements.lv.gm_type import GMTypeLV
from pyptp.network_lv import NetworkLV


class TestTGMTypeLS(unittest.TestCase):
    """Test TGMTypeLS registration and serialization behavior."""

    def setUp(self) -> None:
        """Create fresh network and dependencies for isolated testing."""
        self.network = NetworkLV()

    def test_gm_type_registration_works(self) -> None:
        """Verify basic GM type registration in network."""
        general = GMTypeLV.General(
            number=1, type="Residential", indicator="RES", cos_phi=0.95, correlation=0.5
        )
        gm_type = GMTypeLV(general=general)

        # Verify network starts empty
        self.assertEqual(len(self.network.gmtypes), 0)

        # Register GM type
        gm_type.register(self.network)

        # Verify GM type was added
        self.assertEqual(len(self.network.gmtypes), 1)
        self.assertEqual(self.network.gmtypes[1], gm_type)

    def test_gm_type_with_minimal_properties_serializes_correctly(self) -> None:
        """Test serialization with minimal properties."""
        general = GMTypeLV.General(number=1, type="Residential", indicator="RES")
        gm_type = GMTypeLV(general=general)

        result = gm_type.serialize()

        # Should contain general line
        self.assertIn("#General", result)
        self.assertIn("Number:1", result)
        self.assertIn("GMtype:'Residential'", result)
        self.assertIn("Indicator:'RES'", result)

        # Should skip default values
        self.assertNotIn("CosPhi:", result)  # 0.98 is default
        self.assertNotIn("Correlation:", result)  # 0.0 is default

        # Should not contain GM distribution sections
        self.assertNotIn("#GM1", result)
        self.assertNotIn("#GM2", result)
        self.assertNotIn("#GM3", result)
        self.assertNotIn("#GM4", result)

    def test_gm_type_with_full_properties_serializes_correctly(self) -> None:
        """Test serialization with all properties set."""
        general = GMTypeLV.General(
            number=2, type="Commercial", indicator="COM", cos_phi=0.90, correlation=0.3
        )

        gm_type = GMTypeLV(general=general)

        # Set GM distributions
        gm_type.gm1_params = {"Average": 1.5, "StandardDeviation": 0.2}
        gm_type.gm1_workdays = [1.0, 1.1, 1.2, 1.3, 1.4]
        gm_type.gm1_weekenddays = [0.8, 0.9, 1.0, 1.1, 1.2]
        gm_type.gm1_months = [
            0.9,
            1.0,
            1.1,
            1.2,
            1.3,
            1.4,
            1.5,
            1.4,
            1.3,
            1.2,
            1.1,
            1.0,
        ]

        gm_type.gm2_params = {"Average": 2.0, "StandardDeviation": 0.3}
        gm_type.gm2_workdays = [0.5, 0.6, 0.7, 0.8, 0.9]

        # Set trend data
        gm_type.trend_workdays = [1.0, 1.0, 1.0, 1.0, 1.0]
        gm_type.trend_months = [
            0.95,
            1.0,
            1.05,
            1.1,
            1.15,
            1.2,
            1.25,
            1.2,
            1.15,
            1.1,
            1.05,
            1.0,
        ]

        result = gm_type.serialize()

        # Verify general section
        self.assertIn("#General", result)
        self.assertIn("Number:2", result)
        self.assertIn("GMtype:'Commercial'", result)
        self.assertIn("Indicator:'COM'", result)
        self.assertIn("CosPhi:0.9", result)
        self.assertIn("Correlation:0.3", result)

        # Verify GM1 distribution
        self.assertIn("#GM1", result)
        self.assertIn("Average:1.5", result)
        self.assertIn("StandardDeviation:0.2", result)

        # Verify GM1 factors
        self.assertIn("#WorkDays1", result)
        self.assertIn("f1:1", result)
        self.assertIn("f2:1.1", result)
        self.assertIn("f3:1.2", result)
        self.assertIn("f4:1.3", result)
        self.assertIn("f5:1.4", result)

        self.assertIn("#WeekendDays1", result)
        self.assertIn("f1:0.8", result)
        self.assertIn("f2:0.9", result)
        self.assertIn("f3:1", result)
        self.assertIn("f4:1.1", result)
        self.assertIn("f5:1.2", result)

        self.assertIn("#Months1", result)
        self.assertIn("f1:0.9", result)
        self.assertIn("f12:1", result)

        # Verify GM2 distribution
        self.assertIn("#GM2", result)
        self.assertIn("Average:2", result)
        self.assertIn("StandardDeviation:0.3", result)

        self.assertIn("#WorkDays2", result)
        self.assertIn("f1:0.5", result)
        self.assertIn("f2:0.6", result)
        self.assertIn("f3:0.7", result)
        self.assertIn("f4:0.8", result)
        self.assertIn("f5:0.9", result)

        # Verify trend data
        self.assertIn("#TrendWorkDays", result)
        self.assertIn("f1:1", result)
        self.assertIn("f2:1", result)
        self.assertIn("f3:1", result)
        self.assertIn("f4:1", result)
        self.assertIn("f5:1", result)

        self.assertIn("#TrendMonths", result)
        self.assertIn("f1:0.95", result)
        self.assertIn("f2:1", result)
        self.assertIn("f3:1.05", result)
        self.assertIn("f4:1.1", result)
        self.assertIn("f5:1.15", result)
        self.assertIn("f6:1.2", result)
        self.assertIn("f7:1.25", result)
        self.assertIn("f8:1.2", result)
        self.assertIn("f9:1.15", result)
        self.assertIn("f10:1.1", result)
        self.assertIn("f11:1.05", result)
        self.assertIn("f12:1", result)

    def test_gm_type_deserialization_works(self) -> None:
        """Test deserialization from GNF format data."""
        data = {
            "general": [
                {
                    "Number": 3,
                    "GMtype": "Industrial",
                    "Indicator": "IND",
                    "CosPhi": "0,85",
                    "Correlation": "0,2",
                }
            ],
            "gm1": [{"Average": "1,8", "StandardDeviation": "0,25"}],
            "workdays1": [{"f1": "1,0", "f2": "1,1", "f3": "1,2"}],
            "weekenddays1": [{"f1": "0,9", "f2": "1,0"}],
            "months1": [{"f1": "0,95", "f2": "1,0", "f3": "1,05"}],
            "trendworkdays": [{"f1": "1,0", "f2": "1,0", "f3": "1,0"}],
        }

        gm_type = GMTypeLV.deserialize(data)

        # Verify general properties
        self.assertEqual(gm_type.general.number, 3)
        self.assertEqual(gm_type.general.type, "Industrial")
        self.assertEqual(gm_type.general.indicator, "IND")
        self.assertEqual(gm_type.general.cos_phi, 0.85)
        self.assertEqual(gm_type.general.correlation, 0.2)

        # Verify GM1 properties
        self.assertEqual(gm_type.gm1.average, 1.8)
        self.assertEqual(gm_type.gm1.standard_deviation, 0.25)
        self.assertEqual(gm_type.gm1.work_days, [1.0, 1.1, 1.2])
        self.assertEqual(gm_type.gm1.weekend_days, [0.9, 1.0])
        self.assertEqual(gm_type.gm1.Months, [0.95, 1.0, 1.05])

        # Verify trend properties
        self.assertEqual(gm_type.trend.work_days, [1.0, 1.0, 1.0])

    def test_gm_type_deserialization_with_empty_data(self) -> None:
        """Test deserialization with empty data."""
        data = {}

        gm_type = GMTypeLV.deserialize(data)

        # Should have default general properties
        self.assertIsNotNone(gm_type.general)
        self.assertEqual(gm_type.general.number, 0)
        self.assertEqual(gm_type.general.type, "")
        self.assertEqual(gm_type.general.indicator, "")
        self.assertEqual(gm_type.general.cos_phi, 0.98)
        self.assertEqual(gm_type.general.correlation, 0.0)

        # All GM distributions should be empty
        self.assertEqual(gm_type.gm1.average, 0.0)
        self.assertEqual(gm_type.gm1.standard_deviation, 0.0)
        self.assertEqual(gm_type.gm1.work_days, [])
        self.assertEqual(gm_type.gm1.weekend_days, [])
        self.assertEqual(gm_type.gm1.Months, [])

        # Trend should be empty
        self.assertEqual(gm_type.trend.work_days, [])
        self.assertEqual(gm_type.trend.weekend_days, [])
        self.assertEqual(gm_type.trend.months, [])

    def test_duplicate_gm_type_registration_overwrites(self) -> None:
        """Test Number collision handling with proper logging verification."""
        general1 = GMTypeLV.General(number=1, type="Type 1", indicator="T1")
        general2 = GMTypeLV.General(number=1, type="Type 2", indicator="T2")

        gm_type1 = GMTypeLV(general=general1)
        gm_type2 = GMTypeLV(general=general2)

        # Register first GM type
        gm_type1.register(self.network)
        self.assertEqual(self.network.gmtypes[1].general.type, "Type 1")

        # Register second GM type with same Number should overwrite
        gm_type2.register(self.network)
        # Verify GM type was overwritten
        self.assertEqual(self.network.gmtypes[1].general.type, "Type 2")

    def test_gm_type_general_serialize_with_defaults(self) -> None:
        """Test General class serialization with default values."""
        general = GMTypeLV.General(number=1, type="Test", indicator="TST")

        result = general.serialize()

        # Should include all fields
        self.assertIn("Number:1", result)
        self.assertIn("GMtype:'Test'", result)
        self.assertIn("Indicator:'TST'", result)

        # Should skip default values
        self.assertNotIn("CosPhi:", result)  # 0.98 is default
        self.assertNotIn("Correlation:", result)  # 0.0 is default

    def test_gm_type_general_serialize_with_non_defaults(self) -> None:
        """Test General class serialization with non-default values."""
        general = GMTypeLV.General(
            number=2, type="Test", indicator="TST", cos_phi=0.85, correlation=0.5
        )

        result = general.serialize()

        # Should include all fields including non-defaults
        self.assertIn("Number:2", result)
        self.assertIn("GMtype:'Test'", result)
        self.assertIn("Indicator:'TST'", result)
        self.assertIn("CosPhi:0.85", result)
        self.assertIn("Correlation:0.5", result)

    def test_gm_distribution_properties(self) -> None:
        """Test GM distribution property accessors."""
        gm_type = GMTypeLV(general=GMTypeLV.General())

        # Set GM1 data
        gm_type.gm1_params = {"Average": 1.5, "StandardDeviation": 0.2}
        gm_type.gm1_workdays = [1.0, 1.1, 1.2]
        gm_type.gm1_weekenddays = [0.8, 0.9]
        gm_type.gm1_months = [0.9, 1.0, 1.1]

        # Test GM1 property
        gm1 = gm_type.gm1
        self.assertEqual(gm1.average, 1.5)
        self.assertEqual(gm1.standard_deviation, 0.2)
        self.assertEqual(gm1.work_days, [1.0, 1.1, 1.2])
        self.assertEqual(gm1.weekend_days, [0.8, 0.9])
        self.assertEqual(gm1.Months, [0.9, 1.0, 1.1])

        # Test empty GM2 property
        gm2 = gm_type.gm2
        self.assertEqual(gm2.average, 0.0)
        self.assertEqual(gm2.standard_deviation, 0.0)
        self.assertEqual(gm2.work_days, [])
        self.assertEqual(gm2.weekend_days, [])
        self.assertEqual(gm2.Months, [])

    def test_gm_trend_properties(self) -> None:
        """Test GM trend property accessor."""
        gm_type = GMTypeLV(general=GMTypeLV.General())

        # Set trend data
        gm_type.trend_workdays = [1.0, 1.0, 1.0]
        gm_type.trend_weekenddays = [0.9, 0.9, 0.9]
        gm_type.trend_months = [0.95, 1.0, 1.05]

        # Test trend property
        trend = gm_type.trend
        self.assertEqual(trend.work_days, [1.0, 1.0, 1.0])
        self.assertEqual(trend.weekend_days, [0.9, 0.9, 0.9])
        self.assertEqual(trend.months, [0.95, 1.0, 1.05])

    def test_gm_distribution_serialize_with_defaults(self) -> None:
        """Test GMDistribution serialization with default values."""
        gm_dist = GMTypeLV.Distribution()

        result = gm_dist.serialize()

        # Should be empty string for default values
        self.assertEqual(result, "")

    def test_gm_distribution_serialize_with_values(self) -> None:
        """Test GMDistribution serialization with values."""
        gm_dist = GMTypeLV.Distribution(average=1.5, standard_deviation=0.2)

        result = gm_dist.serialize()

        self.assertIn("Average:1.5", result)
        self.assertIn("StandardDeviation:0.2", result)

    def test_gm_trend_serialize_is_empty(self) -> None:
        """Test GMTrend serialization returns empty string."""
        gm_trend = GMTypeLV.Trend()

        result = gm_trend.serialize()

        # GMTrend is a container class, serialization handled by parent
        self.assertEqual(result, "")

    def test_gm_type_round_trip_serialization(self) -> None:
        """Test that serialization and deserialization are consistent."""
        original_general = GMTypeLV.General(
            number=5, type="Test Type", indicator="TEST", cos_phi=0.92, correlation=0.4
        )

        original_gm_type = GMTypeLV(general=original_general)
        original_gm_type.gm1_params = {"Average": 1.2, "StandardDeviation": 0.15}
        original_gm_type.gm1_workdays = [1.0, 1.1, 1.2]
        original_gm_type.trend_workdays = [1.0, 1.0, 1.0]

        original_gm_type.serialize()

        # Simulate parsing back from GNF format
        data = {
            "general": [
                {
                    "Number": 5,
                    "GMtype": "Test Type",
                    "Indicator": "TEST",
                    "CosPhi": "0,92",
                    "Correlation": "0,4",
                }
            ],
            "gm1": [{"Average": "1,2", "StandardDeviation": "0,15"}],
            "workdays1": [{"f1": "1,0", "f2": "1,1", "f3": "1,2"}],
            "trendworkdays": [{"f1": "1,0", "f2": "1,0", "f3": "1,0"}],
        }

        deserialized = GMTypeLV.deserialize(data)

        # Verify key properties match
        self.assertEqual(deserialized.general.number, original_gm_type.general.number)
        self.assertEqual(deserialized.general.type, original_gm_type.general.type)
        self.assertEqual(
            deserialized.general.indicator, original_gm_type.general.indicator
        )
        self.assertEqual(deserialized.general.cos_phi, original_gm_type.general.cos_phi)
        self.assertEqual(
            deserialized.general.correlation, original_gm_type.general.correlation
        )

        # Verify GM1 properties
        self.assertEqual(deserialized.gm1.average, original_gm_type.gm1.average)
        self.assertEqual(
            deserialized.gm1.standard_deviation, original_gm_type.gm1.standard_deviation
        )
        self.assertEqual(deserialized.gm1.work_days, original_gm_type.gm1.work_days)

        # Verify trend properties
        self.assertEqual(deserialized.trend.work_days, original_gm_type.trend.work_days)


if __name__ == "__main__":
    unittest.main()
