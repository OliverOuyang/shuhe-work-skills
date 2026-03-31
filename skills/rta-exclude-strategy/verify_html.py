"""
验证 HTML 报告功能
"""

import os


def verify_html_report():
    """验证HTML报告的关键功能"""

    # 查找最新的HTML文件
    html_files = [f for f in os.listdir('.') if f.endswith('.html') and f.startswith('RTA')]

    if not html_files:
        print("Error: No HTML report found")
        return False

    html_file = html_files[0]
    print(f"Verifying: {html_file}")
    print(f"File size: {os.path.getsize(html_file)} bytes")

    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # 验证关键元素
    checks = {
        'HTML5 doctype': '<!DOCTYPE html>' in content,
        'UTF-8 charset': 'charset="UTF-8"' in content,
        'Sidebar navigation': 'class="sidebar"' in content,
        'Section 1 (conclusion)': 'id="section1"' in content,
        'Section 2 (strategy)': 'id="section2"' in content,
        'Section 3 (evaluation)': 'id="section3"' in content,
        'Heatmap': 'heatmap' in content.lower(),
        'Gradient CSS': 'linear-gradient' in content,
        'JavaScript sorting': 'sortTable' in content,
        'Smooth scrolling': 'smooth' in content,
        'Table structure': '<table>' in content and '<thead>' in content,
        'Excluded cells': 'excluded-cell' in content,
        'Chinese content': any(ord(c) > 0x4e00 and ord(c) < 0x9fa5 for c in content[:1000])
    }

    print("\nFeature Checks:")
    print("-" * 50)

    all_passed = True
    for feature, passed in checks.items():
        status = "PASS" if passed else "FAIL"
        print(f"{feature:.<40} {status}")
        if not passed:
            all_passed = False

    print("-" * 50)
    print(f"\nOverall: {'ALL CHECKS PASSED' if all_passed else 'SOME CHECKS FAILED'}")

    return all_passed


if __name__ == '__main__':
    verify_html_report()
