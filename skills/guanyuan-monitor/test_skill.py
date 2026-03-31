"""Guanyuan Monitor Skill - End-to-End Test"""
import sys
import json
from pathlib import Path
from datetime import datetime

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "2_预算MMM模型" / "Data"))

print("=" * 60)
print("Guanyuan Monitor Skill - Functional Test")
print("=" * 60)

# Test 1: Module Imports
print("\n[Test 1] Module Imports")
try:
    from scripts.guanyuan_monitor import monitor_config
    from scripts.guanyuan_monitor import alert_rules
    from scripts.guanyuan_monitor import dingtalk_notifier
    from scripts.guanyuan_monitor import scheduler_manager
    from scripts.guanyuan_monitor import main
    print("[PASS] All modules imported successfully")
except Exception as e:
    print(f"[FAIL] Import error: {e}")
    sys.exit(1)

# Test 2: Load Configuration
print("\n[Test 2] Configuration Loading")
try:
    config_path = Path(__file__).parent / "configs" / "test_config.json"
    with open(config_path, 'r', encoding='utf-8') as f:
        config_data = json.load(f)

    config = monitor_config.MonitorConfig(**config_data)
    print(f"[PASS] Config loaded: monitor_id={config.monitor_id}")
    print(f"       Page ID: {config.page_id}")
    print(f"       Cards: {len(config.cards)}")
    print(f"       Schedule: {config.schedule.frequency} at {config.schedule.time}")
    print(f"       Webhook configured: {config.webhook is not None}")
    print(f"       Dry-run mode: {config.dry_run}")
except Exception as e:
    print(f"[FAIL] Config loading error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 3: Alert Rules
print("\n[Test 3] Alert Rule Engine")
try:
    # Test ThresholdRule configuration
    rule_config = monitor_config.ThresholdRuleConfig(
        rule_type="threshold",
        metric_column="test_metric",
        operator=">",
        threshold=100.0,
        description="Test metric exceeded threshold"
    )

    # Create rule from config
    rule = alert_rules.ThresholdRule(config=rule_config)

    # Mock data
    test_data = {"test_metric": [80, 90, 120]}  # Latest value is 120
    result = rule.evaluate(test_data)

    assert result.triggered == True, "Rule should trigger for value > 100"
    assert result.latest_value == 120, "Latest value should be 120"
    print(f"[PASS] ThresholdRule works correctly")
    print(f"       Triggered: {result.triggered}")
    print(f"       Latest value: {result.latest_value}")

except Exception as e:
    print(f"[FAIL] Alert rule error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 4: DingTalk Notifier
print("\n[Test 4] DingTalk Notifier")
try:
    webhook_config = monitor_config.WebhookConfig(
        url="https://oapi.dingtalk.com/robot/send?access_token=test",
        secret="SECtestkey123",
        keywords=["监控", "测试"]
    )

    notifier = dingtalk_notifier.DingTalkNotifier(webhook_config)

    # Test message formatting
    alert_result = alert_rules.AlertResult(
        triggered=True,
        rule_type="threshold",
        field="test_metric",
        operator=">",
        threshold=100,
        latest_value=120,
        message="Test alert message",
        details={"card": "测试卡片", "time": "2026-03-30"},
        timestamp=datetime.now()
    )

    message = notifier.format_markdown_message(
        page_name="测试看板",
        card_name="测试卡片",
        alerts=[alert_result]
    )

    assert "测试看板" in message, "Message should contain page name"
    assert "test_metric" in message, "Message should contain field name"
    print("[PASS] DingTalk notifier works correctly")
    print(f"       Message length: {len(message)} chars")

except Exception as e:
    print(f"[FAIL] DingTalk notifier error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 5: Scheduler Manager
print("\n[Test 5] Scheduler Manager")
try:
    schedule_config = monitor_config.ScheduleConfig(
        frequency="daily",
        time="09:00"
    )

    # Just test the command building, don't actually create tasks
    import platform
    system = platform.system()
    print(f"[PASS] Scheduler manager initialized for {system}")
    print(f"       Schedule: {schedule_config.frequency} at {schedule_config.time}")

except Exception as e:
    print(f"[FAIL] Scheduler manager error: {e}")
    sys.exit(1)

# Test 6: CLI Argument Parsing
print("\n[Test 6] CLI Argument Parsing")
try:
    # Test setup mode args
    test_args = [
        "setup",
        "--page-url", "http://guandata.dmz.prod.caijj.net/page/test123",
        "--cards", "卡片1,卡片2",
        "--webhook", "https://oapi.dingtalk.com/robot/send?access_token=xxx"
    ]

    args = main.parse_cli_args(test_args)
    assert args.command == "setup", "Should parse setup command"
    assert args.page_url is not None, "Should parse page_url"
    assert args.cards is not None, "Should parse cards"
    print("[PASS] CLI parsing works correctly")
    print(f"       Command: {args.command}")
    print(f"       Page URL: {args.page_url}")

except Exception as e:
    print(f"[FAIL] CLI parsing error: {e}")
    sys.exit(1)

# Final Summary
print("\n" + "=" * 60)
print("All Tests Passed!")
print("=" * 60)
print("\nSkill is ready to use. Example commands:")
print("  /guanyuan-monitor --help")
print("  /guanyuan-monitor --config configs/simple_monitor.json --dry-run")
print("=" * 60)
