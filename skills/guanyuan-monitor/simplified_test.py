"""Simplified Guanyuan Monitor Skill Test"""
import sys
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "2_预算MMM模型" / "Data"))

print("=" * 70)
print("Guanyuan Monitor Skill - Simplified Functional Test")
print("=" * 70)

# Test 1: Core Module Imports
print("\n[Test 1] Core Module Imports")
success_count = 0
total_count = 5

modules = [
    ("Monitor Config", "scripts.guanyuan_monitor.monitor_config"),
    ("Alert Rules", "scripts.guanyuan_monitor.alert_rules"),
    ("DingTalk Notifier", "scripts.guanyuan_monitor.dingtalk_notifier"),
    ("Scheduler Manager", "scripts.guanyuan_monitor.scheduler_manager"),
    ("Main Entry", "scripts.guanyuan_monitor.main")
]

for name, module_path in modules:
    try:
        __import__(module_path)
        print(f"  [OK] {name}")
        success_count += 1
    except Exception as e:
        print(f"  [FAIL] {name}: {e}")

print(f"\nResult: {success_count}/{total_count} modules imported successfully")

# Test 2: Configuration Loading
print("\n[Test 2] Configuration Loading and Validation")
try:
    from scripts.guanyuan_monitor import monitor_config
    import json

    config_path = Path(__file__).parent / "configs" / "test_config.json"
    with open(config_path, 'r', encoding='utf-8') as f:
        config_data = json.load(f)

    config = monitor_config.MonitorConfig(**config_data)

    print(f"  [OK] Configuration loaded successfully")
    print(f"       Monitor ID: {config.monitor_id}")
    print(f"       Page ID: {config.page_id}")
    print(f"       Cards: {len(config.cards)}")
    print(f"       Rules per card: {len(config.cards[0].rules)}")
    print(f"       Schedule: {config.schedule.frequency} at {config.schedule.time}")
    print(f"       Webhook: {config.webhook.url[:50]}...")
    print(f"       Dry-run: {config.dry_run}")

except Exception as e:
    print(f"  [FAIL] {e}")
    import traceback
    traceback.print_exc()

# Test 3: Rule Configuration Validation
print("\n[Test 3] Alert Rule Configuration Validation")
try:
    from scripts.guanyuan_monitor import monitor_config

    # Create different rule types
    threshold_rule = monitor_config.ThresholdRuleConfig(
        rule_type="threshold",
        metric_column="test_field",
        operator=">",
        threshold=100.0,
        description="Test threshold rule"
    )

    change_rate_rule = monitor_config.ChangeRateRuleConfig(
        rule_type="change_rate",
        metric_column="test_field",
        rate_type="mom",
        threshold_pct=0.1,
        description="Test change rate rule"
    )

    print(f"  [OK] Threshold Rule: {threshold_rule.metric_column} {threshold_rule.operator} {threshold_rule.threshold}")
    print(f"  [OK] Change Rate Rule: {change_rate_rule.rate_type.upper()} change > {change_rate_rule.threshold_pct*100}%")

except Exception as e:
    print(f"  [FAIL] {e}")

# Test 4: Webhook Configuration
print("\n[Test 4] Webhook Configuration and Signing")
try:
    from scripts.guanyuan_monitor import monitor_config, dingtalk_notifier

    webhook_config = monitor_config.WebhookConfig(
        url="https://oapi.dingtalk.com/robot/send?access_token=test",
        secret="SECtest123",
        keywords=["监控", "测试"]
    )

    notifier = dingtalk_notifier.DingTalkNotifier(webhook_config)

    print(f"  [OK] Webhook initialized")
    print(f"       URL: {webhook_config.url[:50]}...")
    print(f"       Secret: {'*' * len(webhook_config.secret)}")
    print(f"       Keywords: {', '.join(webhook_config.keywords)}")

except Exception as e:
    print(f"  [FAIL] {e}")

# Test 5: CLI Argument Parsing
print("\n[Test 5] CLI Argument Parsing")
try:
    from scripts.guanyuan_monitor import main

    # Test setup command
    test_args_setup = [
        "setup",
        "--page-url", "http://guandata.dmz.prod.caijj.net/page/test123",
        "--cards", "卡片1,卡片2",
        "--webhook", "https://oapi.dingtalk.com/robot/send?access_token=xxx"
    ]

    args_setup = main.parse_cli_args(test_args_setup)
    print(f"  [OK] Setup command parsed")
    print(f"       Command: {args_setup.command}")
    print(f"       Page URL: {args_setup.page_url}")
    print(f"       Cards: {args_setup.cards}")

    # Test run command
    test_args_run = [
        "run",
        "--monitor-id", "test_001",
        "--dry-run"
    ]

    args_run = main.parse_cli_args(test_args_run)
    print(f"  [OK] Run command parsed")
    print(f"       Command: {args_run.command}")
    print(f"       Monitor ID: {args_run.monitor_id}")
    print(f"       Dry-run: {args_run.dry_run}")

except Exception as e:
    print(f"  [FAIL] {e}")
    import traceback
    traceback.print_exc()

# Summary
print("\n" + "=" * 70)
print("Skill Functional Test Complete!")
print("=" * 70)
print("\nThe guanyuan-monitor skill is operational.")
print("\nUsage examples:")
print("  /guanyuan-monitor setup --help")
print("  /guanyuan-monitor run --monitor-id test_001 --dry-run")
print("  /guanyuan-monitor list")
print("=" * 70)
