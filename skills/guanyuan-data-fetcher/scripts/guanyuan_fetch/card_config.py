"""Card Configuration Module

Defines Guanyuan card configurations. Supports loading from JSON config files
for generalized use across different dashboards, while maintaining backward
compatibility with the original hardcoded defaults.
"""

import json
import re
from typing import Dict, List, Literal, Optional
from datetime import datetime
from pathlib import Path


def validate_date(date_str: str, field_name: str = "date") -> str:
    """Validate date string format YYYY-MM-DD and calendar validity.

    Args:
        date_str: Date string to validate
        field_name: Name of the field for error messages

    Returns:
        The date string if valid

    Raises:
        ValueError: If date format is wrong or date is invalid (e.g., 2026-02-29)
    """
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        raise ValueError(
            f"无效日期 '{date_str}' in {field_name}: "
            f"必须是 YYYY-MM-DD 格式的有效日期（例如 2026-03-31）"
        )
    return date_str


# Default page configuration (backward compatible)
PAGE_ID = "wac63dff1a9ee41988f87507"
PAGE_NAME = "1.2 核心指标"

# Default time range configuration
START_DATE = "2025-12-01"


def get_end_date() -> str:
    """Get current date in YYYY-MM-DD format"""
    return datetime.now().strftime("%Y-%m-%d")


# Filter templates
FilterTemplate = Literal["A", "B"]


class CardConfig:
    """Configuration for a single Guanyuan card"""

    def __init__(
        self,
        card_id: str,
        card_name: str,
        filter_template: FilterTemplate,
        output_filename: str,
        tab_name: str = None,
    ):
        self.card_id = card_id
        self.card_name = card_name
        self.filter_template = filter_template
        self.output_filename = output_filename
        self.tab_name = tab_name or "默认"

    def to_dict(self) -> Dict:
        """Convert to dictionary for metadata"""
        return {
            "card_id": self.card_id,
            "card_name": self.card_name,
            "filter_template": self.filter_template,
            "output_filename": self.output_filename,
            "tab_name": self.tab_name,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "CardConfig":
        """Create CardConfig from dictionary (e.g., JSON config entry)

        Args:
            data: Dictionary with keys: card_id, card_name, filter_template,
                  output_filename, tab_name (optional)

        Returns:
            CardConfig instance
        """
        return cls(
            card_id=data["card_id"],
            card_name=data["card_name"],
            filter_template=data["filter_template"],
            output_filename=data.get("output_filename", f"{data['card_name']}.csv"),
            tab_name=data.get("tab_name"),
        )


class DashboardConfig:
    """Configuration for an entire Guanyuan dashboard page.

    Loaded from a JSON config file or constructed programmatically.
    """

    def __init__(
        self,
        page_id: str,
        page_name: str,
        cards: List[CardConfig],
        start_date: str = "2025-12-01",
        end_date: Optional[str] = None,
    ):
        self.page_id = page_id
        self.page_name = page_name
        self.cards = cards
        self.start_date = start_date
        self.end_date = end_date  # None means "today"

    def get_end_date(self) -> str:
        """Get effective end date (resolves 'today' to current date)"""
        if self.end_date is None or self.end_date == "today":
            return get_end_date()
        return self.end_date

    def to_dict(self) -> Dict:
        """Convert to serializable dictionary"""
        return {
            "page_id": self.page_id,
            "page_name": self.page_name,
            "default_date_range": {
                "start": self.start_date,
                "end": self.end_date or "today",
            },
            "cards": [card.to_dict() for card in self.cards],
        }

    @classmethod
    def from_json_file(cls, config_path: Path) -> "DashboardConfig":
        """Load dashboard configuration from a JSON file.

        Args:
            config_path: Path to JSON config file

        Returns:
            DashboardConfig instance

        Raises:
            FileNotFoundError: If config file does not exist
            json.JSONDecodeError: If config file is not valid JSON
            KeyError: If required fields are missing
        """
        config_path = Path(config_path)
        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")

        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        cards = [CardConfig.from_dict(card_data) for card_data in data["cards"]]

        date_range = data.get("default_date_range", {})
        start_date = date_range.get("start", "2025-12-01")
        end_date = date_range.get("end", "today")
        if end_date == "today":
            end_date = None

        return cls(
            page_id=data["page_id"],
            page_name=data["page_name"],
            cards=cards,
            start_date=start_date,
            end_date=end_date,
        )

    @classmethod
    def get_default(cls) -> "DashboardConfig":
        """Get the default dashboard config (backward compatible with original hardcoded cards)"""
        return cls(
            page_id=PAGE_ID,
            page_name=PAGE_NAME,
            cards=list(CARDS),  # Copy of the default cards list
            start_date=START_DATE,
            end_date=None,
        )


# --- Default card definitions (backward compatible) ---

CARDS: List[CardConfig] = [
    # Card #1: 首借交易额_重主营_by 6大客群 (Template A - 2 filters)
    CardConfig(
        card_id="jf7c4b4828db24159b573a32",
        card_name="首借交易额_重主营_by 6大客群",
        filter_template="A",
        output_filename="首借交易额_重主营_by6大客群.csv",
        tab_name="默认",
    ),

    # Card #2: 首借交易金额 (Template B - 5 filters)
    CardConfig(
        card_id="ddd5b55e62a2a4c979f9ff11",
        card_name="首借交易金额",
        filter_template="B",
        output_filename="首借交易金额.csv",
        tab_name="规模",
    ),

    # Card #3: 过件率-排年龄_分渠道 (Template B - 5 filters)
    CardConfig(
        card_id="wb89068311995463299e6e1c",
        card_name="过件率-排年龄_分渠道",
        filter_template="B",
        output_filename="过件率_排年龄_分渠道.csv",
        tab_name="质量",
    ),

    # Card #4: 1-3过件率-排年龄_分渠道 (Template B - 5 filters)
    CardConfig(
        card_id="x8283e0f1e8f2467f954bccb",
        card_name="1-3过件率-排年龄_分渠道",
        filter_template="B",
        output_filename="1_3过件率_排年龄_分渠道.csv",
        tab_name="质量",
    ),

    # Card #5: 申完成本_排年龄_分渠道 (Template B - 5 filters)
    CardConfig(
        card_id="f96d0cdc038d24966ace3acf",
        card_name="申完成本_排年龄_分渠道",
        filter_template="B",
        output_filename="申完成本_排年龄_分渠道.csv",
        tab_name="效率",
    ),
]


def get_card_by_id(card_id: str, cards: List[CardConfig] = None) -> CardConfig:
    """Get card configuration by ID

    Args:
        card_id: Card ID to look up
        cards: Card list to search (default: CARDS)
    """
    search_list = cards if cards is not None else CARDS
    for card in search_list:
        if card.card_id == card_id:
            return card
    raise ValueError(f"Card ID not found: {card_id}")


def get_cards_by_template(template: FilterTemplate, cards: List[CardConfig] = None) -> List[CardConfig]:
    """Get all cards using a specific filter template

    Args:
        template: Filter template type
        cards: Card list to search (default: CARDS)
    """
    search_list = cards if cards is not None else CARDS
    return [card for card in search_list if card.filter_template == template]


def load_config(config_path: Optional[str] = None) -> DashboardConfig:
    """Load dashboard configuration from file or use defaults.

    Args:
        config_path: Path to JSON config file. If None, uses default config.
                     Resolves relative paths from current working directory.

    Returns:
        DashboardConfig instance
    """
    if config_path is None:
        return DashboardConfig.get_default()

    path = Path(config_path)
    # If relative, try resolving against the configs directory first
    if not path.is_absolute() and not path.exists():
        configs_dir = Path(__file__).parent / "configs"
        candidate = configs_dir / path
        if candidate.exists():
            path = candidate

    return DashboardConfig.from_json_file(path)


def generate_output_filename(page_name: str, start_date: str, end_date: str) -> str:
    """Generate output filename with page name and query time

    Args:
        page_name: Dashboard page name (e.g., "1.2 核心指标")
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format

    Returns:
        Filename like "核心指标_20251201_20260330.xlsx"

    Example:
        >>> generate_output_filename("1.2 核心指标", "2025-12-01", "2026-03-30")
        "核心指标_20251201_20260330.xlsx"
    """
    # Remove numbers and dots from page name, keep only Chinese characters
    cleaned_name = re.sub(r'[^\u4e00-\u9fff]', '', page_name)

    # Convert dates from YYYY-MM-DD to YYYYMMDD
    start_compact = start_date.replace('-', '')
    end_compact = end_date.replace('-', '')

    # Return formatted filename
    return f"{cleaned_name}_{start_compact}_{end_compact}.xlsx"
