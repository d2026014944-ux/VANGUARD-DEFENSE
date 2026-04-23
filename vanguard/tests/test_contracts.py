import json
import os
from xml.etree import ElementTree as ET


def _repo_root() -> str:
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def test_detection_schema_exists_and_is_valid_json():
    schema_path = os.path.join(_repo_root(), "vanguard", "contracts", "detection.schema.json")
    with open(schema_path, "r", encoding="utf-8") as f:
        schema = json.load(f)
    assert schema["type"] == "object"
    assert "required" in schema
    assert "location" in schema["properties"]


def test_cot_xsd_exists_and_is_well_formed_xml():
    xsd_path = os.path.join(_repo_root(), "vanguard", "contracts", "cot-event.xsd")
    tree = ET.parse(xsd_path)
    root = tree.getroot()
    assert root.tag.endswith("schema")
