# CLAUDE.md — VANGUARD: Especificação Técnica Ativa (V.1.0)

> **ATENÇÃO:** Este arquivo é a **Lei do Projeto**. Toda sugestão de IA, refatoração ou nova feature deve ser validada contra este documento **antes** de entrar na branch `main`. Qualquer mudança arquitetural deve ser refletida aqui **antes** de qualquer alteração no código (Anti-Vibe Coding — Akita Way).

---

## Identidade do Projeto

- **Nome:** VANGUARD — *Vision, Analytics & Next-Generation Units for Reconnaissance and Defense*
- **Domínio:** Ciência de Dados Aplicada à Defesa e Consciência Situacional
- **Vínculo Institucional:** UNIFEI — Iniciação Científica
- **Repositório:** `d2026014944-ux/VANGUARD-DEFENSE`

---

## Módulos e Contratos de Interface

### VG-VISION
- **Responsabilidade:** Inferência TFLite/ONNX em dispositivos de borda (Edge).
- **Input:** Stream de câmera (frames RGB).
- **Output:** `List[BoundingBox(class: str, confidence: float, location: Tuple[x, y, w, h])]` serializado em JSON.
- **Hardware:** Android (NPU via TFLite) / Raspberry Pi (ONNX Runtime).
- **Restrição:** O modelo deve ser `.tflite` ou `.onnx`. **Nenhum** modelo PyTorch bruto roda na ponta.

### VG-CORE
- **Responsabilidade:** Conversão de detecções em pacotes CoT (Cursor on Target) no padrão ATAK/ATAK-CIV.
- **Input:** JSON de `BoundingBox` oriundo do VG-VISION.
- **Output:** Pacote XML-CoT validado pelo schema ATAK.
- **Regra crítica:** Todo pacote gerado deve ser validado pelo schema XML antes do envio. Pacotes inválidos são descartados e logados.

### VG-COMM
- **Responsabilidade:** Gateway de comunicação híbrida com suporte a múltiplos transportes.
- **Input:** Pacote XML-CoT do VG-CORE.
- **Output:** Entrega via rede (4G / Wi-Fi tático / LoRa Meshtastic) com fila de prioridade.
- **Resiliência:** Deve operar com alta latência e perda de pacotes sem bloquear o pipeline.
- **Transporte LoRa:** Via protocolo Meshtastic (rádios LoRa 915 MHz / 433 MHz).

### VG-LAB (research/lab-distillation)
- **Responsabilidade:** Pipeline de destilação de conhecimento (Teacher → Student).
- **Modelo Professor:** Grounding DINO (ou similar open-source de larga escala) — roda em servidor GPU.
- **Modelo Estudante:** YOLOv11-Nano / MobileNet — treinado para imitar o Professor.
- **Auto-Labeling:** O Professor rotula dados brutos automaticamente e armazena no Feature Store (Layer 2).
- **Output do pipeline:** Modelo Estudante convertido para `.tflite` / `.onnx`, pronto para deploy Edge.

---

## Stack Tecnológica

### Edge (VG-VISION / VG-CORE / VG-COMM)
- **Linguagem:** Python 3.11+
- **Inferência:** TensorFlow Lite / ONNX Runtime
- **Serialização:** JSON (detecções) / XML (CoT ATAK)
- **Testes:** Pytest + pytest-cov

### Servidor / Laboratório (VG-LAB)
- **Linguagem:** Python 3.11+
- **Framework de Treinamento:** PyTorch + Ultralytics (YOLO)
- **Banco de Dados:** PostgreSQL 15 (FTS-Core) + SQLite 3 (LTM)
- **ORM:** SQLAlchemy
- **Auto-Labeling:** Grounding DINO via `groundingdino` package

### Infraestrutura de Treinamento (VG-LAB)
- **Engine:** NVIDIA CUDA Toolkit / CUDA-Q (Hybrid Workloads)
- **Containerização:** NVIDIA Docker (`--runtime nvidia`)
- **Objetivo:** Aceleração de Tensores para Destilação de Conhecimento (Teacher → Student)
- **Referência:** [NVIDIA CUDA-Q Starter Kits](https://developer.nvidia.com/cuda-q#section-starter-kits)

### Comunicação
- **Protocolo tático:** CoT (Cursor on Target) — padrão ATAK
- **Rádio:** LoRa via Meshtastic
- **Rede:** 4G / Wi-Fi (fallback hierárquico gerenciado pelo VG-COMM)

---

## Arquitetura do Banco de Dados

| Camada | Tecnologia | Propósito |
|---|---|---|
| Layer 0 — LTM | SQLite | Persistência offline em cada nó (celular / RPi) |
| Layer 1 — FTS-Core | PostgreSQL | Telemetria em tempo real e histórico de missões |
| Layer 2 — Feature Store | JSONB (PostgreSQL) | Labels do modelo Professor vinculados às imagens brutas |

---

## Regras de Desenvolvimento

1. **TDD Obrigatório:** Nenhum código entra em `main` sem testes Pytest aprovados.
2. **AI-Jail:** Scripts gerados por IA devem ser executados em Docker Containers isolados.
3. **Schema-First:** O contrato de interface (JSON/XML Schema) é definido antes da implementação.
4. **Sem CUDA no SO principal:** Todo treinamento usa `nvidia-docker`. Proibido instalar CUDA diretamente.
5. **Pacotes CoT inválidos são descartados:** VG-CORE nunca envia um pacote que falhe na validação do schema ATAK.
6. **Deploy Edge = conversão obrigatória:** Nenhum modelo PyTorch bruto é deployado na ponta.

---

## Comandos de Desenvolvimento

```bash
# Instalar dependências de desenvolvimento
pip install -r requirements-dev.txt

# Executar todos os testes
pytest vanguard/tests/ -v --cov=vanguard

# Executar testes de um módulo específico
pytest vanguard/tests/test_vg_core.py -v

# Subir ambiente de laboratório (requer NVIDIA Docker)
docker-compose up vg-lab

# Subir apenas o FreeTAKServer (para testes de integração CoT)
docker-compose up freetakserver
```

---

## Histórico de Versões deste Arquivo

| Versão | Data | Mudança |
|---|---|---|
| V.1.0 | 2026-03-26 | Criação da especificação inicial com todos os módulos definidos. |

---

*CLAUDE.md — VANGUARD V.1.0 — UNIFEI — 2026*
