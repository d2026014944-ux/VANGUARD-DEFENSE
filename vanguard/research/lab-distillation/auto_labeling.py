from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class GeoLabel:
    image_id: str
    class_name: str
    confidence: float
    bbox: tuple[float, float, float, float]
    lon: float
    lat: float
    srid: int = 4326

    def point_wkt(self) -> str:
        return f"POINT({self.lon} {self.lat})"


class GroundingDinoAutoLabeler:
    """
    Auto-labeling Teacher pipeline.
    Current scope: filter and normalize pre-computed detections for persistence.
    Target scope: connect actual inference to the groundingdino package in GPU environment.
    """

    def __init__(self, confidence_threshold: float = 0.35):
        if not 0.0 <= confidence_threshold <= 1.0:
            raise ValueError("confidence_threshold deve estar em [0,1]")
        self.confidence_threshold = confidence_threshold

    def build_labels(self, image_id: str, detections: list[dict[str, Any]]) -> list[GeoLabel]:
        labels: list[GeoLabel] = []
        for detection in detections:
            confidence = float(detection["confidence"])
            if confidence < self.confidence_threshold:
                continue
            labels.append(
                GeoLabel(
                    image_id=image_id,
                    class_name=str(detection["class"]),
                    confidence=confidence,
                    bbox=tuple(detection["bbox"]),
                    lon=float(detection["lon"]),
                    lat=float(detection["lat"]),
                )
            )
        return labels


class PostGISFeatureStoreRepository:
    """Persistência de labels no PostgreSQL + PostGIS (Layer 2 Feature Store)."""

    ENABLE_POSTGIS_SQL = "CREATE EXTENSION IF NOT EXISTS postgis;"

    CREATE_TABLE_SQL = """
    CREATE TABLE IF NOT EXISTS vg_lab_auto_labels (
        id BIGSERIAL PRIMARY KEY,
        image_id TEXT NOT NULL,
        class_name TEXT NOT NULL,
        confidence DOUBLE PRECISION NOT NULL,
        bbox_x DOUBLE PRECISION NOT NULL,
        bbox_y DOUBLE PRECISION NOT NULL,
        bbox_w DOUBLE PRECISION NOT NULL,
        bbox_h DOUBLE PRECISION NOT NULL,
        geom geometry(Point, 4326) NOT NULL,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );
    """

    INSERT_SQL = """
    INSERT INTO vg_lab_auto_labels (
        image_id, class_name, confidence,
        bbox_x, bbox_y, bbox_w, bbox_h, geom
    ) VALUES (
        %s, %s, %s,
        %s, %s, %s, %s, ST_SetSRID(ST_GeomFromText(%s), %s)
    );
    """

    def ensure_schema(self, connection: Any) -> None:
        with connection.cursor() as cursor:
            cursor.execute(self.ENABLE_POSTGIS_SQL)
            cursor.execute(self.CREATE_TABLE_SQL)
        connection.commit()

    def save_labels(self, connection: Any, labels: list[GeoLabel]) -> int:
        if not labels:
            return 0
        with connection.cursor() as cursor:
            for label in labels:
                x, y, w, h = label.bbox
                cursor.execute(
                    self.INSERT_SQL,
                    (
                        label.image_id,
                        label.class_name,
                        label.confidence,
                        x,
                        y,
                        w,
                        h,
                        label.point_wkt(),
                        label.srid,
                    ),
                )
        connection.commit()
        return len(labels)
