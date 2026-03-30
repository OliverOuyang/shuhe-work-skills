"""Unit tests for filter_builder module"""

import pytest
from scripts.guanyuan_fetch.filter_builder import (
    build_template_a_filters,
    build_template_b_filters,
    build_filters,
    validate_filters,
)


class TestTemplateAFilters:
    """Tests for Template A filter building"""

    def test_template_a_structure(self):
        """Test that Template A produces 2 filters with correct structure"""
        filters = build_template_a_filters("2025-12-01", "2026-03-30")

        assert len(filters) == 2

        # Filter 1: Date dimension (common filter)
        f1 = filters[0]
        assert f1["filterType"] == "common"
        assert f1["filterInfo"]["name"] == "日期维度"
        assert f1["filterInfo"]["conditionType"] == "EQ"
        assert f1["filterInfo"]["filterValues"] == ["月"]
        assert f1["filterInfo"]["defaultFilter"] is True

        # Filter 2: Date range (dynamic filter)
        f2 = filters[1]
        assert f2["filterType"] == "dynamic"
        assert f2["filterInfo"]["name"] == "日期区间"
        assert f2["filterInfo"]["fdType"] == "DATE"
        assert f2["filterInfo"]["filterValues"] == ["2025-12-01", "2026-03-30"]
        assert f2["filterInfo"]["defaultFilter"] is False

    def test_template_a_date_range(self):
        """Test that Template A correctly uses provided dates"""
        filters = build_template_a_filters("2024-01-01", "2024-12-31")
        date_filter = filters[1]
        assert date_filter["filterInfo"]["filterValues"] == ["2024-01-01", "2024-12-31"]


class TestTemplateBFilters:
    """Tests for Template B filter building"""

    def test_template_b_structure(self):
        """Test that Template B produces 5 filters with correct structure"""
        filters = build_template_b_filters("2025-12-01", "2026-03-30")

        assert len(filters) == 5

        # Filter 1: Date dimension
        assert filters[0]["filterInfo"]["name"] == "日期维度"
        assert filters[0]["filterInfo"]["filterValues"] == ["月"]

        # Filter 2: T+N caliber
        assert filters[1]["filterInfo"]["name"] == "T+N日口径"
        assert filters[1]["filterInfo"]["filterValues"] == ["T3"]

        # Filter 3: Date range
        assert filters[2]["filterInfo"]["name"] == "日期区间"
        assert filters[2]["filterInfo"]["filterValues"] == ["2025-12-01", "2026-03-30"]

        # Filter 4: Level 1 channel
        assert filters[3]["filterInfo"]["name"] == "一级渠道"
        assert filters[3]["filterInfo"]["filterValues"] == []  # Empty = ALL

        # Filter 5: Level 2 channel
        assert filters[4]["filterInfo"]["name"] == "二级渠道"
        assert filters[4]["filterInfo"]["filterValues"] == []  # Empty = ALL


class TestBuildFilters:
    """Tests for the main build_filters function"""

    def test_build_template_a(self):
        """Test building Template A via main function"""
        filters = build_filters("A", "2025-12-01", "2026-03-30")
        assert len(filters) == 2

    def test_build_template_b(self):
        """Test building Template B via main function"""
        filters = build_filters("B", "2025-12-01", "2026-03-30")
        assert len(filters) == 5

    def test_invalid_template(self):
        """Test that invalid template raises ValueError"""
        with pytest.raises(ValueError, match="Invalid template"):
            build_filters("C", "2025-12-01", "2026-03-30")


class TestValidateFilters:
    """Tests for filter validation"""

    def test_validate_valid_template_a(self):
        """Test that valid Template A filters pass validation"""
        filters = build_template_a_filters("2025-12-01", "2026-03-30")
        assert validate_filters(filters) is True

    def test_validate_valid_template_b(self):
        """Test that valid Template B filters pass validation"""
        filters = build_template_b_filters("2025-12-01", "2026-03-30")
        assert validate_filters(filters) is True

    def test_validate_missing_filter_type(self):
        """Test that missing filterType raises ValueError"""
        filters = [{"filterInfo": {}}]
        with pytest.raises(ValueError, match="missing 'filterType'"):
            validate_filters(filters)

    def test_validate_missing_filter_info(self):
        """Test that missing filterInfo raises ValueError"""
        filters = [{"filterType": "common"}]
        with pytest.raises(ValueError, match="missing 'filterInfo'"):
            validate_filters(filters)

    def test_validate_missing_required_keys(self):
        """Test that missing required keys raise ValueError"""
        filters = [
            {
                "filterType": "common",
                "filterInfo": {
                    "name": "test",
                    # Missing fdId, filterValues, defaultFilter, conditionType
                },
            }
        ]
        with pytest.raises(ValueError, match="missing"):
            validate_filters(filters)

    def test_validate_dynamic_filter_requires_fd_type(self):
        """Test that dynamic filters require fdType"""
        filters = [
            {
                "filterType": "dynamic",
                "filterInfo": {
                    "fdId": "test",
                    "name": "test",
                    "filterValues": ["value"],
                    "defaultFilter": True,
                    # Missing fdType
                },
            }
        ]
        with pytest.raises(ValueError, match="missing 'fdType'"):
            validate_filters(filters)
