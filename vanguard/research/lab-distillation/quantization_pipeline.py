from __future__ import annotations

import json
import shutil
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class QuantizationAcceptanceCriteria:
    max_accuracy_drop_pct: float
    min_memory_reduction_pct: float
    min_latency_improvement_pct: float


@dataclass(frozen=True)
class BenchmarkMetrics:
    baseline_accuracy: float
    quantized_accuracy: float
    baseline_memory_mb: float
    quantized_memory_mb: float
    baseline_latency_ms: float
    quantized_latency_ms: float


@dataclass(frozen=True)
class QuantizationResult:
    quantized_model_path: str
    metadata_path: str
    accepted: bool
    accuracy_drop_pct: float
    memory_reduction_pct: float
    latency_improvement_pct: float


class INT8QuantizationPipeline:
    """Pipeline de quantização INT8 para modelos ONNX do estudante."""

    def __init__(self, criteria: QuantizationAcceptanceCriteria):
        self.criteria = criteria

    @staticmethod
    def _pct_delta(before: float, after: float) -> float:
        if before == 0:
            return 0.0
        return ((before - after) / before) * 100.0

    def evaluate(self, metrics: BenchmarkMetrics) -> QuantizationResult:
        accuracy_drop = max(0.0, metrics.baseline_accuracy - metrics.quantized_accuracy)
        memory_reduction = self._pct_delta(metrics.baseline_memory_mb, metrics.quantized_memory_mb)
        latency_improvement = self._pct_delta(metrics.baseline_latency_ms, metrics.quantized_latency_ms)
        accepted = (
            accuracy_drop <= self.criteria.max_accuracy_drop_pct
            and memory_reduction >= self.criteria.min_memory_reduction_pct
            and latency_improvement >= self.criteria.min_latency_improvement_pct
        )
        return QuantizationResult(
            quantized_model_path="",
            metadata_path="",
            accepted=accepted,
            accuracy_drop_pct=accuracy_drop,
            memory_reduction_pct=memory_reduction,
            latency_improvement_pct=latency_improvement,
        )

    def quantize_model(
        self,
        student_model_path: str | Path,
        output_dir: str | Path,
        metrics: BenchmarkMetrics,
    ) -> QuantizationResult:
        source = Path(student_model_path)
        if source.suffix.lower() != ".onnx":
            raise ValueError("Pipeline INT8 exige modelo de entrada .onnx")

        out_dir = Path(output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        quantized_path = out_dir / f"{source.stem}.int8.onnx"
        metadata_path = out_dir / f"{source.stem}.int8.benchmark.json"

        # Placeholder de produção de artefato INT8.
        # Em ambiente de laboratório, substituir por quantização real ORT/TensorRT.
        shutil.copyfile(source, quantized_path)

        evaluated = self.evaluate(metrics)
        metadata = {
            "model": source.name,
            "quantized_model": quantized_path.name,
            "criteria": asdict(self.criteria),
            "metrics": asdict(metrics),
            "result": {
                "accepted": evaluated.accepted,
                "accuracy_drop_pct": evaluated.accuracy_drop_pct,
                "memory_reduction_pct": evaluated.memory_reduction_pct,
                "latency_improvement_pct": evaluated.latency_improvement_pct,
            },
        }
        metadata_path.write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")

        return QuantizationResult(
            quantized_model_path=str(quantized_path),
            metadata_path=str(metadata_path),
            accepted=evaluated.accepted,
            accuracy_drop_pct=evaluated.accuracy_drop_pct,
            memory_reduction_pct=evaluated.memory_reduction_pct,
            latency_improvement_pct=evaluated.latency_improvement_pct,
        )
