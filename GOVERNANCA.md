# 🛡️ VANGUARD: Arquitetura de Governança Central (V.1.0)

**Projeto de Iniciação Científica — UNIFEI**
**Domínio:** Ciência de Dados Aplicada à Defesa e Consciência Situacional
**Nome oficial:** VANGUARD — *Vision, Analytics & Next-Generation Units for Reconnaissance and Defense*

---

## 1. Filosofia de Engenharia (Anti-Vibe Coding — Akita Way)

| Princípio | Regra |
|---|---|
| **Controle Total** | Nenhuma sugestão de IA será aceita sem validação técnica e alinhamento com esta especificação. |
| **Disciplina sobre Intuição** | O design da arquitetura e as regras de negócio são definidos pelo humano. A IA é usada **apenas** como aceleradora de implementação. |
| **Documentação é Código** | Mudanças na arquitetura exigem atualização imediata deste documento **antes** de qualquer alteração no código. |
| **CLAUDE.md é Lei** | O arquivo `CLAUDE.md` é a especificação permanente. Qualquer mudança arquitetural deve ser refletida nele via TDD imediatamente. |

---

## 2. Domínios e Subgrupos (Monorepo Strategy)

O projeto é dividido em módulos com responsabilidades isoladas para garantir testabilidade e isolamento de falhas:

### VG-VISION — Percepção de Borda (Edge Inference)
- **Função:** Inferência de modelos destilados (YOLO-Nano / MobileNet) em tempo real.
- **Hardware alvo:** Celulares Android (NPU) ou Raspberry Pi.
- **Contrato de saída:** Metadados em JSON → `[BoundingBox(class, conf, loc)]` → VG-CORE.
- **Formato de deploy:** `.tflite` ou `.onnx` obrigatório.

### VG-CORE — Orquestração Tática
- **Função:** O "Cérebro". Traduz detecções em pacotes CoT (*Cursor on Target*).
- **Governança:** Validação rigorosa de Schema XML conforme o padrão ATAK / ATAK-CIV.
- **Contrato:** `ObjectDetection → XML-CoT (ATAK Standard)`.

### VG-COMM — Gateway de Comunicação Híbrida
- **Função:** Transporte híbrido. Gerencia filas de prioridade para 4G, Wi-Fi tático e rádios LoRa (Meshtastic).
- **Resiliência:** Deve suportar latência alta e perda de pacotes sem travar o sistema.
- **Contrato:** `CoT-Packet → PriorityQueue → Network`.

### VG-LAB — Pipeline de Dados e Destilação
- **Função:** Auto-Labeling com o modelo Professor (Grounding DINO) e Destilação de Conhecimento para o modelo Estudante.
- **Banco de Dados:** PostgreSQL (histórico / FTS-Core) + SQLite (local / LTM).

---

## 3. Arquitetura do Banco de Dados (Schema de Defesa)

Dividida em três camadas para garantir integridade em ambientes de combate/simulação:

| Camada | Tecnologia | Função |
|---|---|---|
| **Layer 0 — LTM** (Local Tactical Memory) | SQLite | Persistência offline imediata em cada nó (celular / Raspberry Pi). |
| **Layer 1 — FTS-Core** | PostgreSQL | Telemetria em tempo real e histórico de missões no servidor central. |
| **Layer 2 — Feature Store** | JSONB (PostgreSQL) | Metadados e labels gerados pelo modelo Professor vinculados às imagens brutas, permitindo retreinamento do modelo Estudante. |

---

## 4. Estratégia de IA — Teacher-Student Distillation

| Papel | Modelo | Ambiente |
|---|---|---|
| **Modelo Professor** | Grounding DINO (ou similar open-source) | Servidor com GPU — NVIDIA Docker Container (isolado). |
| **Modelo Estudante** | YOLOv11-Nano / MobileNet | Edge (celular / Raspberry Pi). |
| **Deploy obrigatório** | `.tflite` / `.onnx` | Conversão antes de qualquer deploy na ponta. |

---

## 5. Infraestrutura de Treinamento (VG-LAB)

- **Engine:** NVIDIA CUDA Toolkit / CUDA-Q (Hybrid Workloads).
- **Containerização:** NVIDIA Docker (`--runtime nvidia`).
- **Objetivo:** Aceleração de Tensores para Destilação de Conhecimento (Teacher → Student).
- **AI-Jail:** Execuções de scripts gerados por IA ocorrem **dentro** de Docker Containers isolados para proteger a máquina local e o ambiente da UNIFEI de conflitos de drivers e bibliotecas.
- **Referência:** [NVIDIA CUDA-Q Starter Kits](https://developer.nvidia.com/cuda-q#section-starter-kits)

> **Disciplina:** Não instale CUDA diretamente no SO principal. Use o Docker com suporte a GPU.

---

## 6. Protocolo de Desenvolvimento (TDD & Sandbox)

| Regra | Detalhe |
|---|---|
| **Rede de Segurança** | Antes de cada feature, a IA deve escrever os testes (Pytest). Se não houver teste, o código não entra na branch `main`. |
| **AI-Jail** | Execuções de scripts gerados pela IA ocorrem em Docker Containers isolados. |
| **Refatoração** | Mudanças que afetam múltiplos serviços exigem testes de integração cruzada no Monorepo. |
| **CLAUDE.md Permanente** | Se a arquitetura mudar no `CLAUDE.md`, o código deve ser refatorado via TDD imediatamente. |

---

## 7. Estrutura de Pastas do Monorepo

```
/vanguard
  /services
    /vg-vision       # Inferência Edge (TFLite/ONNX)
    /vg-core         # Motor CoT/ATAK
    /vg-comm         # Gateway Híbrido (4G/Wi-Fi/LoRa)
  /research
    /lab-distillation  # Pipeline Teacher-Student (VG-LAB)
  /tests             # Testes unitários e de integração
  CLAUDE.md          # Especificação técnica ativa (Lei do projeto)
  GOVERNANCA.md      # Este arquivo — Governança Central
  docker-compose.yml # Ambiente de desenvolvimento isolado
```

---

## 8. Checklist de Engenharia (Pré-GitHub)

- [x] Repositório criado no GitHub.
- [x] `GOVERNANCA.md` versionado no repositório.
- [x] `CLAUDE.md` com especificação técnica ativa.
- [x] Estrutura de pastas do Monorepo criada.
- [x] `docker-compose.yml` com suporte a NVIDIA e isolamento de rede para FreeTAKServer.
- [ ] Servidor com GPU (NVIDIA) na UNIFEI — *a definir após aprovação da IC*.
- [ ] Primeiro teste de validação CUDA (latência de transferência de memória).
- [ ] Testes unitários VG-CORE (conversão de detecção para XML-CoT ATAK).
- [ ] Modelo Professor (Grounding DINO) containerizado e validado.
- [ ] Primeiro modelo Estudante convertido para `.tflite` e testado em edge.

---

*Documento de Governança Central — VANGUARD V.1.0 — UNIFEI — 2026*
