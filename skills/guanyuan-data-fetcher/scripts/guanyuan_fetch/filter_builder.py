"""Filter Builder Module

Builds filter payloads for Guanyuan get_card_data API calls.
Implements Template A (2 filters) and Template B (5 filters) based on spec Section 7.
"""

from typing import Dict, List, Any, Literal
from datetime import datetime


def build_template_a_filters(start_date: str, end_date: str) -> List[Dict[str, Any]]:
    """Build Template A filters (2 filters) for Card #1

    Template A structure (from spec Section 7.3.1):
    1. Common filter: 日期维度 (date dimension) -> value: "月"
    2. Dynamic filter: 日期区间 (date range) -> values: [start_date, end_date]

    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format

    Returns:
        List of filter dictionaries ready for get_card_data API
    """
    return [
        # Filter 1: Date dimension = "月" (monthly) - DYNAMIC filter
        {
            "filterType": "dynamic",
            "filterInfo": {
                "fdId": "o658e5441331a4a3ab5194ee",  # Real field ID from get_card_filters
                "name": "日期维度",
                "alias": "日期维度",
                "fdType": "STRING",
                "filterValues": ["月"],
                "defaultFilter": True,
            },
        },
        # Filter 2: Date range - COMMON filter
        {
            "filterType": "common",
            "filterInfo": {
                "fdId": "td881b43e6ceb4b53930e737",  # Real field ID from get_card_filters
                "name": "calculate_day",
                "alias": "日期区间",
                "conditionType": "BT",
                "filterValues": [start_date, end_date],
                "defaultFilter": True,
            },
        },
    ]


def build_template_b_filters(start_date: str, end_date: str) -> List[Dict[str, Any]]:
    """Build Template B filters (5 filters) for Cards #2-5

    Template B structure (from actual get_card_filters response):
    1. Dynamic filter: 日期维度 -> value: "月"
    2. Dynamic filter: T+N日口径 -> value: "T3"
    3. Common filter: 日期区间 -> values: [start_date, end_date]
    4. Common filter: 一级渠道 -> ALL (empty list)
    5. Common filter: 二级渠道 -> ALL (empty list)

    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format

    Returns:
        List of filter dictionaries ready for get_card_data API
    """
    return [
        # Filter 1: Date dimension = "月" (monthly) - DYNAMIC
        {
            "filterType": "dynamic",
            "filterInfo": {
                "fdId": "o658e5441331a4a3ab5194ee",
                "name": "日期维度",
                "alias": "日期维度",
                "fdType": "STRING",
                "filterValues": ["月"],
                "defaultFilter": True,
            },
        },
        # Filter 2: T+N caliber = "T0" (default, adjust as needed) - DYNAMIC
        {
            "filterType": "dynamic",
            "filterInfo": {
                "fdId": "q4a3c634321b64da1806cd97",
                "name": "T+N日口径",
                "alias": "T+N日口径",
                "fdType": "STRING",
                "filterValues": ["T0"],  # Can be T0, T3, T15, T30, T90
                "defaultFilter": True,
            },
        },
        # Filter 3: Date range - COMMON
        {
            "filterType": "common",
            "filterInfo": {
                "fdId": "dadcf00e5643d4ea2b5148da",
                "name": "计算日期（calculate_date）",
                "alias": "日期区间",
                "conditionType": "BT",
                "filterValues": [start_date, end_date],
                "defaultFilter": True,
            },
        },
        # Filter 4: Level 1 channel = ALL (use default values) - COMMON
        {
            "filterType": "common",
            "filterInfo": {
                "fdId": "e07c34ea4817b40a8b497ebf",
                "name": "渠道一级分组名称（marketing_channel_group_name_1）",
                "alias": "一级渠道",
                "conditionType": "IN",
                "filterValues": ["信息流渠道", "CPA渠道", "付费商店渠道", "免费渠道", "其他"],
                "defaultFilter": True,
            },
        },
        # Filter 5: Level 2 channel = ALL (use default values) - COMMON
        {
            "filterType": "common",
            "filterInfo": {
                "fdId": "e541d0e6b499548679356050",
                "name": "渠道二级分组名称（marketing_channel_group_name_2）",
                "alias": "二级渠道",
                "conditionType": "IN",
                "filterValues": ["字节", "腾讯", "精准营销", "商店信息流", "商店", "免费", "其他信息流", "其他CPA", None],
                "defaultFilter": True,
            },
        },
    ]


def build_filters(
    template: Literal["A", "B"], start_date: str, end_date: str
) -> List[Dict[str, Any]]:
    """Build filters based on template type

    Args:
        template: Filter template type ("A" or "B")
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format

    Returns:
        List of filter dictionaries

    Raises:
        ValueError: If template is not "A" or "B"
    """
    if template == "A":
        return build_template_a_filters(start_date, end_date)
    elif template == "B":
        return build_template_b_filters(start_date, end_date)
    else:
        raise ValueError(f"Invalid template: {template}. Must be 'A' or 'B'")


def validate_filters(filters: List[Dict[str, Any]]) -> bool:
    """Validate that all filters have required keys

    Args:
        filters: List of filter dictionaries

    Returns:
        True if all filters are valid

    Raises:
        ValueError: If any filter is missing required keys
    """
    for i, f in enumerate(filters):
        # Check top-level keys
        if "filterType" not in f:
            raise ValueError(f"Filter {i}: missing 'filterType'")
        if "filterInfo" not in f:
            raise ValueError(f"Filter {i}: missing 'filterInfo'")

        # Check filterInfo keys
        info = f["filterInfo"]
        required_keys = ["fdId", "name", "filterValues", "defaultFilter"]

        # conditionType is required for common filters, optional for dynamic
        if f["filterType"] == "common":
            required_keys.append("conditionType")
        elif f["filterType"] == "dynamic":
            required_keys.append("fdType")

        for key in required_keys:
            if key not in info:
                raise ValueError(
                    f"Filter {i} ({info.get('name', 'unknown')}): missing '{key}'"
                )

    return True
