"""
VG-CORE Unit Tests — Pytest
Testa a conversão de detecções do VG-VISION em pacotes XML-CoT (padrão ATAK).
Anti-Vibe Coding: testes escritos ANTES ou JUNTO com a implementação (TDD).
Execute com: pytest vanguard/tests/test_vg_core.py -v
"""
import sys
import os
from xml.etree import ElementTree as ET

import pytest

# Garante que o módulo vg-core seja importável ao rodar pytest da raiz
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "services", "vg-core"))

from cot_converter import BoundingBox, CotPacket, VGCoreConverter


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def converter():
    return VGCoreConverter(stale_seconds=30)


@pytest.fixture
def valid_box():
    """BoundingBox válida com coordenadas geográficas."""
    return BoundingBox(
        class_name="person",
        confidence=0.92,
        x=0.5, y=0.5, width=0.1, height=0.2,
        lat=-22.5505,
        lon=-43.1729,
        hae=850.0,
    )


@pytest.fixture
def box_no_coords():
    """BoundingBox sem coordenadas geográficas (deve ser descartada)."""
    return BoundingBox(
        class_name="vehicle",
        confidence=0.75,
        x=0.3, y=0.3, width=0.15, height=0.15,
        lat=None,
        lon=None,
    )


# ---------------------------------------------------------------------------
# Testes: BoundingBox → CotPacket
# ---------------------------------------------------------------------------

class TestDetectionToCotPacket:

    def test_valid_box_returns_packet(self, converter, valid_box):
        packet = converter.detection_to_cot_packet(valid_box)
        assert packet is not None

    def test_packet_has_uid(self, converter, valid_box):
        packet = converter.detection_to_cot_packet(valid_box)
        assert packet.uid.startswith("VANGUARD-")

    def test_packet_cot_type_person(self, converter, valid_box):
        packet = converter.detection_to_cot_packet(valid_box)
        assert packet.cot_type == "a-h-G"

    def test_packet_cot_type_vehicle(self, converter):
        box = BoundingBox("vehicle", 0.8, 0.1, 0.1, 0.1, 0.1, lat=-22.0, lon=-43.0)
        packet = converter.detection_to_cot_packet(box)
        assert packet.cot_type == "a-h-G-E-V"

    def test_packet_cot_type_unknown_class(self, converter):
        box = BoundingBox("dog", 0.6, 0.1, 0.1, 0.1, 0.1, lat=-22.0, lon=-43.0)
        packet = converter.detection_to_cot_packet(box)
        assert packet.cot_type == "a-u-G"

    def test_missing_coords_returns_none(self, converter, box_no_coords):
        packet = converter.detection_to_cot_packet(box_no_coords)
        assert packet is None

    def test_invalid_confidence_returns_none(self, converter):
        box = BoundingBox("person", 1.5, 0.1, 0.1, 0.1, 0.1, lat=-22.0, lon=-43.0)
        packet = converter.detection_to_cot_packet(box)
        assert packet is None

    def test_zero_confidence_is_valid(self, converter):
        box = BoundingBox("person", 0.0, 0.1, 0.1, 0.1, 0.1, lat=-22.0, lon=-43.0)
        packet = converter.detection_to_cot_packet(box)
        assert packet is not None

    def test_packet_contains_lat_lon(self, converter, valid_box):
        packet = converter.detection_to_cot_packet(valid_box)
        assert packet.lat == valid_box.lat
        assert packet.lon == valid_box.lon

    def test_packet_detail_contains_class_and_confidence(self, converter, valid_box):
        packet = converter.detection_to_cot_packet(valid_box)
        assert "person" in packet.detail
        assert "0.92" in packet.detail


# ---------------------------------------------------------------------------
# Testes: CotPacket → XML-CoT
# ---------------------------------------------------------------------------

class TestCotPacketToXml:

    def _make_packet(self):
        return CotPacket(
            uid="VANGUARD-test-uid-001",
            cot_type="a-h-G",
            lat=-22.5505,
            lon=-43.1729,
            hae=850.0,
            time="2026-03-26T12:00:00.000Z",
            start="2026-03-26T12:00:00.000Z",
            stale="2026-03-26T12:00:30.000Z",
            detail="person conf=0.92",
        )

    def test_xml_is_parseable(self, converter):
        xml_str = converter.cot_packet_to_xml(self._make_packet())
        root = ET.fromstring(xml_str)
        assert root is not None

    def test_xml_root_tag_is_event(self, converter):
        xml_str = converter.cot_packet_to_xml(self._make_packet())
        root = ET.fromstring(xml_str)
        assert root.tag == "event"

    def test_xml_version_is_2_0(self, converter):
        xml_str = converter.cot_packet_to_xml(self._make_packet())
        root = ET.fromstring(xml_str)
        assert root.get("version") == "2.0"

    def test_xml_uid_matches(self, converter):
        xml_str = converter.cot_packet_to_xml(self._make_packet())
        root = ET.fromstring(xml_str)
        assert root.get("uid") == "VANGUARD-test-uid-001"

    def test_xml_type_matches(self, converter):
        xml_str = converter.cot_packet_to_xml(self._make_packet())
        root = ET.fromstring(xml_str)
        assert root.get("type") == "a-h-G"

    def test_xml_has_point_element(self, converter):
        xml_str = converter.cot_packet_to_xml(self._make_packet())
        root = ET.fromstring(xml_str)
        point = root.find("point")
        assert point is not None

    def test_xml_point_lat_lon(self, converter):
        xml_str = converter.cot_packet_to_xml(self._make_packet())
        root = ET.fromstring(xml_str)
        point = root.find("point")
        assert float(point.get("lat")) == pytest.approx(-22.5505, abs=1e-4)
        assert float(point.get("lon")) == pytest.approx(-43.1729, abs=1e-4)

    def test_xml_has_detail_element(self, converter):
        xml_str = converter.cot_packet_to_xml(self._make_packet())
        root = ET.fromstring(xml_str)
        detail = root.find("detail")
        assert detail is not None

    def test_xml_detail_has_remarks(self, converter):
        xml_str = converter.cot_packet_to_xml(self._make_packet())
        root = ET.fromstring(xml_str)
        remarks = root.find("detail/remarks")
        assert remarks is not None
        assert "person" in remarks.text

    def test_xml_detail_has_contact_callsign(self, converter):
        xml_str = converter.cot_packet_to_xml(self._make_packet())
        root = ET.fromstring(xml_str)
        contact = root.find("detail/contact")
        assert contact is not None
        assert contact.get("callsign") == "VANGUARD"

    def test_xml_how_is_machine_generated(self, converter):
        xml_str = converter.cot_packet_to_xml(self._make_packet())
        root = ET.fromstring(xml_str)
        assert root.get("how") == "m-g"

    def test_invalid_packet_raises_value_error(self, converter):
        bad_packet = CotPacket(
            uid="",
            cot_type="",
            lat=0.0, lon=0.0, hae=0.0,
            time="", start="", stale="", detail="",
        )
        with pytest.raises(ValueError):
            converter.cot_packet_to_xml(bad_packet)


# ---------------------------------------------------------------------------
# Testes: Pipeline completo convert() e convert_batch()
# ---------------------------------------------------------------------------

class TestConvertPipeline:

    def test_convert_valid_box_returns_xml_string(self, converter, valid_box):
        result = converter.convert(valid_box)
        assert result is not None
        assert isinstance(result, str)
        assert "<event" in result

    def test_convert_no_coords_returns_none(self, converter, box_no_coords):
        result = converter.convert(box_no_coords)
        assert result is None

    def test_convert_batch_filters_invalid(self, converter, valid_box, box_no_coords):
        boxes = [valid_box, box_no_coords, valid_box]
        results = converter.convert_batch(boxes)
        assert len(results) == 2
        for r in results:
            assert "<event" in r

    def test_convert_batch_empty_list(self, converter):
        results = converter.convert_batch([])
        assert results == []

    def test_convert_batch_all_invalid_returns_empty(self, converter, box_no_coords):
        results = converter.convert_batch([box_no_coords, box_no_coords])
        assert results == []

    def test_convert_aircraft_type(self, converter):
        box = BoundingBox("aircraft", 0.88, 0.5, 0.5, 0.1, 0.1, lat=-22.5, lon=-43.2)
        xml_str = converter.convert(box)
        root = ET.fromstring(xml_str)
        assert root.get("type") == "a-h-A"

    def test_each_converted_packet_has_unique_uid(self, converter, valid_box):
        xml1 = converter.convert(valid_box)
        xml2 = converter.convert(valid_box)
        root1 = ET.fromstring(xml1)
        root2 = ET.fromstring(xml2)
        assert root1.get("uid") != root2.get("uid")
