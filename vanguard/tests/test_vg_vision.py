import os
import sys

import pytest

sys.path.insert(
    0,
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "services",
        "vg-vision",
    ),
)

from inference_engine import BoundingBox, HardwareCompatibilityPolicy, ONNXEdgeDetector


def test_runtime_policy_prefers_onnx_for_nvidia_intel_snapdragon():
    assert HardwareCompatibilityPolicy.runtime_for_target("nvidia") == "onnxruntime"
    assert HardwareCompatibilityPolicy.runtime_for_target("intel") == "onnxruntime"
    assert HardwareCompatibilityPolicy.runtime_for_target("snapdragon") == "onnxruntime"


def test_detector_requires_onnx_model():
    with pytest.raises(ValueError):
        ONNXEdgeDetector("student_model.tflite")


def test_contract_json_shape_is_stable():
    detection = BoundingBox(
        class_name="person",
        confidence=0.9,
        x=0.1,
        y=0.2,
        width=0.3,
        height=0.4,
        lat=-22.0,
        lon=-43.0,
        hae=10.0,
    )
    payload = detection.to_contract_dict()
    assert sorted(payload.keys()) == ["class", "confidence", "hae", "lat", "location", "lon"]
    assert payload["location"] == [0.1, 0.2, 0.3, 0.4]


def test_normalize_raw_detection_clips_values_to_valid_range():
    detector = ONNXEdgeDetector("student.onnx")
    normalized = detector.normalize_raw_detection(
        {
            "class": "vehicle",
            "confidence": 1.7,
            "x": -0.2,
            "y": 0.5,
            "width": 2.0,
            "height": 0.4,
            "lat": -22.1,
            "lon": -43.2,
        }
    )
    assert normalized.confidence == 1.0
    assert normalized.x == 0.0
    assert normalized.width == 1.0


def test_infer_uses_onnx_session_and_normalizes_raw_output():
    detector = ONNXEdgeDetector("student.onnx")

    class _Input:
        name = "input_0"

    class _FakeSession:
        def get_inputs(self):
            return [_Input()]

        def run(self, _, __):
            return [[
                {
                    "class": "person",
                    "confidence": 0.8,
                    "x": 0.1,
                    "y": 0.2,
                    "width": 0.3,
                    "height": 0.4,
                    "lat": -22.1,
                    "lon": -43.2,
                }
            ]]

    detector._session = _FakeSession()
    detections = detector.infer(frame="fake-frame")
    assert len(detections) == 1
    assert detections[0].class_name == "person"
