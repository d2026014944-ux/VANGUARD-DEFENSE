import json
import os
import sys

import pytest

sys.path.insert(
    0,
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "research",
        "lab-distillation",
    ),
)

from quantization_pipeline import (
    BenchmarkMetrics,
    INT8QuantizationPipeline,
    QuantizationAcceptanceCriteria,
)


def test_quantization_pipeline_rejects_non_onnx_input(tmp_path):
    criteria = QuantizationAcceptanceCriteria(1.0, 20.0, 10.0)
    pipeline = INT8QuantizationPipeline(criteria)
    not_onnx = tmp_path / "model.pt"
    not_onnx.write_text("weights", encoding="utf-8")

    with pytest.raises(ValueError):
        pipeline.quantize_model(not_onnx, tmp_path, _metrics())


def test_quantization_pipeline_creates_int8_artifacts_and_metadata(tmp_path):
    criteria = QuantizationAcceptanceCriteria(1.0, 20.0, 10.0)
    pipeline = INT8QuantizationPipeline(criteria)
    source = tmp_path / "student.onnx"
    source.write_text("fake-onnx-content", encoding="utf-8")

    result = pipeline.quantize_model(source, tmp_path / "out", _metrics())

    assert result.accepted is True
    assert os.path.exists(result.quantized_model_path)
    assert os.path.exists(result.metadata_path)

    with open(result.metadata_path, "r", encoding="utf-8") as f:
        metadata = json.load(f)
    assert metadata["result"]["accepted"] is True


def _metrics() -> BenchmarkMetrics:
    return BenchmarkMetrics(
        baseline_accuracy=0.95,
        quantized_accuracy=0.945,
        baseline_memory_mb=100.0,
        quantized_memory_mb=70.0,
        baseline_latency_ms=20.0,
        quantized_latency_ms=15.0,
    )
