import os
import sys

sys.path.insert(
    0,
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "research",
        "lab-distillation",
    ),
)

from auto_labeling import GroundingDinoAutoLabeler, PostGISFeatureStoreRepository


def test_auto_labeling_filters_by_threshold():
    labeler = GroundingDinoAutoLabeler(confidence_threshold=0.5)
    labels = labeler.build_labels(
        "img-1",
        [
            {"class": "person", "confidence": 0.9, "bbox": [0.1, 0.1, 0.2, 0.2], "lon": -43.2, "lat": -22.1},
            {"class": "vehicle", "confidence": 0.4, "bbox": [0.2, 0.2, 0.3, 0.3], "lon": -43.2, "lat": -22.1},
        ],
    )
    assert len(labels) == 1
    assert labels[0].class_name == "person"


def test_postgis_repository_contains_spatial_sql():
    repo = PostGISFeatureStoreRepository()
    assert "CREATE EXTENSION IF NOT EXISTS postgis" in repo.ENABLE_POSTGIS_SQL
    assert "ST_GeomFromText" in repo.INSERT_SQL
