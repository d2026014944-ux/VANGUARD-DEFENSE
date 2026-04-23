from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class BoundingBox:
    class_name: str
    confidence: float
    x: float
    y: float
    width: float
    height: float
    lat: float | None = None
    lon: float | None = None
    hae: float = 0.0

    def to_contract_dict(self) -> dict[str, Any]:
        payload = {
            "class": self.class_name,
            "confidence": self.confidence,
            "location": [self.x, self.y, self.width, self.height],
            "lat": self.lat,
            "lon": self.lon,
            "hae": self.hae,
        }
        return payload


class HardwareCompatibilityPolicy:
    """Runtime policy by hardware target for Edge inference."""

    TARGET_RUNTIME = {
        "nvidia": "onnxruntime",
        "intel": "onnxruntime",
        "snapdragon": "onnxruntime",
        "android-npu": "tflite",
        "raspberry-pi": "onnxruntime",
    }

    @classmethod
    def runtime_for_target(cls, target: str) -> str:
        return cls.TARGET_RUNTIME.get(target.lower(), "onnxruntime")


class ONNXEdgeDetector:
    """Edge detection with ONNX Runtime as the default path."""

    def __init__(self, model_path: str | Path):
        self.model_path = Path(model_path)
        if self.model_path.suffix.lower() != ".onnx":
            raise ValueError("VG-VISION ONNXEdgeDetector exige modelo .onnx")
        self._session = None

    def _ensure_session(self):
        if self._session is not None:
            return self._session
        try:
            import onnxruntime as ort  # type: ignore
        except ImportError as exc:
            raise RuntimeError(
                "onnxruntime is not installed. Install it for actual inference."
            ) from exc
        self._session = ort.InferenceSession(str(self.model_path), providers=["CPUExecutionProvider"])
        return self._session

    @staticmethod
    def _clip01(value: float) -> float:
        return max(0.0, min(1.0, float(value)))

    def normalize_raw_detection(self, raw: dict[str, Any]) -> BoundingBox:
        return BoundingBox(
            class_name=str(raw["class"]),
            confidence=self._clip01(float(raw["confidence"])),
            x=self._clip01(float(raw["x"])),
            y=self._clip01(float(raw["y"])),
            width=self._clip01(float(raw["width"])),
            height=self._clip01(float(raw["height"])),
            lat=float(raw["lat"]) if raw.get("lat") is not None else None,
            lon=float(raw["lon"]) if raw.get("lon") is not None else None,
            hae=float(raw.get("hae", 0.0)),
        )

    def format_detections_json(self, detections: list[BoundingBox]) -> list[dict[str, Any]]:
        return [d.to_contract_dict() for d in detections]

    def infer(self, frame: Any) -> list[BoundingBox]:
        """
        Executes ONNX Runtime inference path.
        Model-specific post-processing must convert runtime output into raw detections.
        """
        session = self._ensure_session()
        input_name = session.get_inputs()[0].name
        outputs = session.run(None, {input_name: frame})
        raw_detections = outputs[0] if outputs else []
        detections: list[BoundingBox] = []
        for raw in raw_detections:
            if isinstance(raw, dict):
                detections.append(self.normalize_raw_detection(raw))
        return detections


def export_contract_payload(detections: list[BoundingBox]) -> list[dict[str, Any]]:
    return [d.to_contract_dict() for d in detections]
