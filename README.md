# 🛡️ VANGUARD-DEFENSE
**Vision, Analytics & Next-Generation Units for Reconnaissance and Defense**

Projeto de Iniciação Científica — UNIFEI
Domínio: Ciência de Dados Aplicada à Defesa e Consciência Situacional.

---

## Módulos

| Módulo | Responsabilidade | Contrato |
|---|---|---|
| **VG-VISION** | Inferência TFLite/ONNX (Edge) | `Stream → List[BoundingBox]` |
| **VG-CORE** | Motor de Conversão CoT (Cursor on Target) | `BoundingBox JSON → XML-CoT (ATAK)` |
| **VG-COMM** | Gateway Híbrido (4G / Wi-Fi / LoRa) | `CoT-Packet → PriorityQueue → Network` |
| **VG-LAB** | Pipeline de Destilação (Teacher → Student) | `RawData → AutoLabeling → DistilledModel` |

## Documentação

- [`GOVERNANCA.md`](GOVERNANCA.md) — Arquitetura de Governança Central (V.1.0)
- [`CLAUDE.md`](CLAUDE.md) — Especificação Técnica Ativa (Lei do Projeto)

## Início Rápido

```bash
# Instalar dependências de desenvolvimento
pip install -r requirements-dev.txt

# Executar testes
pytest vanguard/tests/ -v

# Subir ambiente de laboratório (requer NVIDIA Docker)
docker-compose up vg-lab
```

## Filosofia

Este projeto segue o princípio **Anti-Vibe Coding (Akita Way)**: toda sugestão de IA é validada
contra a especificação técnica antes de entrar em produção. Documentação é código.
