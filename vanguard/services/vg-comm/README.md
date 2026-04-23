# VG-COMM — Hybrid Communication Gateway

**Responsabilidade:** Transporte híbrido de pacotes CoT com suporte a múltiplas redes.

## Contrato de Interface
- **Input:** Pacote XML-CoT validado pelo VG-CORE
- **Output:** Entrega via rede com fila de prioridade
- **Schema:** `vanguard/contracts/cot-event.xsd`

## Transportes Suportados
- **4G** — Cobertura principal
- **Wi-Fi Tático** — Redes locais de campo
- **LoRa (Meshtastic)** — Comunicação de longa distância sem infraestrutura (915 MHz / 433 MHz)

## Resiliência
Opera com alta latência e perda de pacotes sem bloquear o pipeline principal.
