# VG-VISION — Edge Inference Module

**Responsabilidade:** Inferência de modelos destilados (TFLite/ONNX) em dispositivos de borda.

## Contrato de Interface
- **Input:** Stream de câmera (frames RGB)
- **Output:** `List[BoundingBox(class, confidence, location)]` serializado em JSON → VG-CORE

## Hardware Alvo
- Android (NPU via TensorFlow Lite)
- Raspberry Pi (ONNX Runtime)

## Restrição
O modelo deve estar no formato `.tflite` ou `.onnx`. Nenhum modelo PyTorch bruto roda na ponta.
