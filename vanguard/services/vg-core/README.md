# VG-CORE — Tactical Orchestration Module

**Responsabilidade:** Motor de Conversão CoT (Cursor on Target). Traduz detecções em pacotes XML-CoT compatíveis com o padrão ATAK/ATAK-CIV.

## Contrato de Interface
- **Input:** JSON de `BoundingBox` oriundo do VG-VISION
- **Output:** Pacote XML-CoT validado pelo schema ATAK

## Regra Crítica
Todo pacote gerado deve ser validado pelo schema XML antes do envio. **Pacotes inválidos são descartados e logados.** Nunca envia XML malformado para o VG-COMM.

## Testes
```bash
pytest ../../tests/test_vg_core.py -v
```
