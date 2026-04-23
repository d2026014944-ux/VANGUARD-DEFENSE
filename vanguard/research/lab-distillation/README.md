# VG-LAB — Knowledge Distillation Pipeline

**Responsabilidade:** Pipeline de destilação de conhecimento Teacher → Student e auto-labeling de dados brutos.

## Estratégia Teacher-Student
- **Modelo Professor:** Grounding DINO (open-source, larga escala) — roda em servidor GPU via NVIDIA Docker.
- **Modelo Estudante:** YOLOv11-Nano / MobileNet — otimizado para Edge deployment.

## Banco de Dados
- **Layer 0 (LTM):** SQLite — persistência offline em cada nó.
- **Layer 1 (FTS-Core):** PostgreSQL — telemetria em tempo real e histórico.
- **Layer 2 (Feature Store):** JSONB (PostgreSQL) — labels do Professor vinculados às imagens brutas.

## Infraestrutura
- NVIDIA CUDA Toolkit / CUDA-Q
- NVIDIA Docker (`--runtime nvidia`)
- [NVIDIA CUDA-Q Starter Kits](https://developer.nvidia.com/cuda-q#section-starter-kits)

## AI-Jail
Todo treinamento ocorre dentro de Docker Containers isolados. **Proibido instalar CUDA diretamente no SO principal.**

## Output
Modelo Estudante convertido para `.tflite` / `.onnx`, pronto para deploy Edge via VG-VISION.

## Artefatos iniciais do pipeline
- `quantization_pipeline.py`: trilha de quantização INT8 com critérios de aceitação e benchmark metadata.
- `auto_labeling.py`: auto-labeling Teacher + persistência no PostgreSQL com PostGIS.
