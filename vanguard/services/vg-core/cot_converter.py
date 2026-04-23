"""
VG-CORE — Motor de Conversão CoT (Cursor on Target)
Responsabilidade: Converter detecções do VG-VISION em pacotes XML-CoT válidos (padrão ATAK/ATAK-CIV).
Contrato: BoundingBox JSON → XML-CoT validado pelo schema ATAK.
Regra crítica: Pacotes inválidos são descartados e logados. Nunca envia XML malformado.
"""
from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional
from xml.etree import ElementTree as ET

logger = logging.getLogger(__name__)


@dataclass
class BoundingBox:
    """Contrato de entrada oriundo do VG-VISION."""
    class_name: str
    confidence: float
    x: float  # normalizado [0, 1]
    y: float  # normalizado [0, 1]
    width: float   # normalizado [0, 1]
    height: float  # normalizado [0, 1]
    lat: Optional[float] = None   # latitude geográfica (se disponível)
    lon: Optional[float] = None   # longitude geográfica (se disponível)
    hae: float = 0.0              # height above ellipsoid (metros)


@dataclass
class CotPacket:
    """Representação interna de um pacote CoT antes da serialização XML."""
    uid: str
    cot_type: str        # Ex: "a-h-G" (hostile ground unit)
    lat: float
    lon: float
    hae: float
    time: str            # ISO 8601
    start: str           # ISO 8601
    stale: str           # ISO 8601
    detail: str          # Descrição livre (class_name + confidence)


class VGCoreConverter:
    """
    Converte detecções do VG-VISION em pacotes XML-CoT compatíveis com ATAK.
    Segue o schema CoT 2.0 (https://www.mitre.org/sites/default/files/pdf/09_4937.pdf).
    """

    # Mapeamento de classes detectadas para tipos CoT ATAK
    COT_TYPE_MAP: dict[str, str] = {
        "person":   "a-h-G",      # hostile ground
        "vehicle":  "a-h-G-E-V",  # hostile ground vehicle
        "aircraft": "a-h-A",      # hostile air
        "unknown":  "a-u-G",      # unknown ground
    }
    DEFAULT_COT_TYPE = "a-u-G"
    # ATAK/CoT convention for unknown CE/LE uses a very high sentinel value.
    # Mantemos 9999999.0 para indicar "erro de localização desconhecido".
    UNKNOWN_ERROR_VALUE = 9999999.0
    REQUIRED_EVENT_ATTRS = ("version", "uid", "type", "time", "start", "stale", "how")
    REQUIRED_POINT_ATTRS = ("lat", "lon", "hae", "ce", "le")
    CONTRACT_XSD_PATH = (
        Path(__file__).resolve().parents[2] / "contracts" / "cot-event.xsd"
    )

    def __init__(self, stale_seconds: int = 30):
        self.stale_seconds = stale_seconds

    def _map_cot_type(self, class_name: str) -> str:
        return self.COT_TYPE_MAP.get(class_name.lower(), self.DEFAULT_COT_TYPE)

    def _iso_now(self) -> str:
        return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"

    def _iso_stale(self) -> str:
        from datetime import timedelta
        dt = datetime.now(timezone.utc) + timedelta(seconds=self.stale_seconds)
        return dt.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"

    def detection_to_cot_packet(self, box: BoundingBox) -> Optional[CotPacket]:
        """
        Converte um BoundingBox em um CotPacket.
        Retorna None se dados geográficos ausentes (lat/lon obrigatórios para CoT).
        """
        if box.lat is None or box.lon is None:
            logger.warning(
                "BoundingBox sem coordenadas geográficas ignorada: class=%s conf=%.2f",
                box.class_name, box.confidence,
            )
            return None

        if not (0.0 <= box.confidence <= 1.0):
            logger.error("Confiança fora do intervalo [0,1]: conf=%.4f", box.confidence)
            return None

        now = self._iso_now()
        return CotPacket(
            uid=f"VANGUARD-{uuid.uuid4()}",
            cot_type=self._map_cot_type(box.class_name),
            lat=box.lat,
            lon=box.lon,
            hae=box.hae,
            time=now,
            start=now,
            stale=self._iso_stale(),
            detail=f"{box.class_name} conf={box.confidence:.2f}",
        )

    def cot_packet_to_xml(self, packet: CotPacket) -> str:
        """
        Serializa um CotPacket em XML-CoT válido (schema ATAK CoT 2.0).
        Raises ValueError se o pacote estiver incompleto.
        """
        if not packet.uid or not packet.cot_type:
            raise ValueError("CotPacket inválido: uid e cot_type são obrigatórios.")

        event = ET.Element("event")
        event.set("version", "2.0")
        event.set("uid", packet.uid)
        event.set("type", packet.cot_type)
        event.set("time", packet.time)
        event.set("start", packet.start)
        event.set("stale", packet.stale)
        event.set("how", "m-g")  # machine-generated

        point = ET.SubElement(event, "point")
        point.set("lat", f"{packet.lat:.7f}")
        point.set("lon", f"{packet.lon:.7f}")
        point.set("hae", f"{packet.hae:.2f}")
        point.set("ce", str(self.UNKNOWN_ERROR_VALUE))   # circular error (desconhecido)
        point.set("le", str(self.UNKNOWN_ERROR_VALUE))   # linear error (desconhecido)

        detail = ET.SubElement(event, "detail")
        remarks = ET.SubElement(detail, "remarks")
        remarks.text = packet.detail

        contact = ET.SubElement(detail, "contact")
        contact.set("callsign", "VANGUARD")

        xml_str = ET.tostring(event, encoding="unicode", xml_declaration=False)
        return xml_str

    def validate_cot_xml_contract(self, xml_str: str) -> bool:
        """
        Validação de contrato obrigatória antes do envio para VG-COMM.
        Garante estrutura mínima do CoT e faixas válidas de coordenadas.
        """
        if not self.CONTRACT_XSD_PATH.exists():
            logger.error("Contrato XSD não encontrado em %s", self.CONTRACT_XSD_PATH)
            return False

        try:
            ET.parse(self.CONTRACT_XSD_PATH)
        except ET.ParseError as exc:
            logger.error("Contrato XSD inválido: %s", exc)
            return False

        try:
            root = ET.fromstring(xml_str)
        except ET.ParseError as exc:
            logger.error("XML-CoT malformado: %s", exc)
            return False

        if root.tag != "event":
            return False

        for attr in self.REQUIRED_EVENT_ATTRS:
            if not root.get(attr):
                return False

        point = root.find("point")
        detail = root.find("detail")
        if point is None or detail is None:
            return False

        for attr in self.REQUIRED_POINT_ATTRS:
            if point.get(attr) is None:
                return False

        try:
            lat = float(point.get("lat", "nan"))
            lon = float(point.get("lon", "nan"))
            float(point.get("hae", "nan"))
            float(point.get("ce", "nan"))
            float(point.get("le", "nan"))
        except ValueError:
            return False

        if not (-90.0 <= lat <= 90.0 and -180.0 <= lon <= 180.0):
            return False

        contact = detail.find("contact")
        if contact is None or not contact.get("callsign"):
            return False

        return True

    def convert(self, box: BoundingBox) -> Optional[str]:
        """
        Pipeline completo: BoundingBox → XML-CoT.
        Retorna None se a detecção for inválida ou sem coordenadas geográficas.
        """
        packet = self.detection_to_cot_packet(box)
        if packet is None:
            return None
        try:
            xml_str = self.cot_packet_to_xml(packet)
            if not self.validate_cot_xml_contract(xml_str):
                logger.error("XML-CoT rejeitado por validação de contrato.")
                return None
            logger.debug("CoT gerado: uid=%s type=%s", packet.uid, packet.cot_type)
            return xml_str
        except ValueError as exc:
            logger.error("Falha ao serializar CotPacket: %s", exc)
            return None

    def convert_batch(self, boxes: List[BoundingBox]) -> List[str]:
        """Converte uma lista de detecções, descartando as inválidas."""
        results = []
        for box in boxes:
            xml_str = self.convert(box)
            if xml_str is not None:
                results.append(xml_str)
        return results
