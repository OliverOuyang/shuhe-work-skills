#!/usr/bin/env python3
"""
版本管理模块
提供 skill 版本信息读取、版本升级等功能
"""
import json
import re
from pathlib import Path
from typing import Dict, Optional, Tuple


class VersionManager:
    """版本管理器"""
    
    def __init__(self, root_dir: Optional[Path] = None):
        """初始化版本管理器"""
        self.root_dir = root_dir or Path(__file__).parent.parent.parent.parent
        self.package_json = self.root_dir / "package.json"
    
    def get_plugin_version(self) -> str:
        """获取插件版本"""
        if not self.package_json.exists():
            return "unknown"
        
        with open(self.package_json, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('version', 'unknown')
    
    def list_skills(self):
        """列出所有 skills (返回完整的 skill 对象列表)"""
        if not self.package_json.exists():
            return []

        with open(self.package_json, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('claudePlugin', {}).get('skills', [])

    def get_skill_info(self, skill_name: str):
        """获取特定 skill 的完整信息"""
        skills = self.list_skills()
        return next((s for s in skills if s.get('name') == skill_name), None)
    
    def bump_skill_version(self, skill_name: str, bump_type: str = 'patch') -> str:
        """升级 skill 版本"""
        skill = self.get_skill_info(skill_name)
        if not skill:
            raise ValueError(f"Skill '{skill_name}' not found")

        current_version = skill.get('version', self.get_plugin_version())
        new_version = self.bump_version(current_version, bump_type)

        # Update package.json
        with open(self.package_json, 'r', encoding='utf-8') as f:
            data = json.load(f)

        for s in data['claudePlugin']['skills']:
            if s['name'] == skill_name:
                s['version'] = new_version
                break

        with open(self.package_json, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        return new_version

    def get_skill_version(self, skill_name: str) -> Optional[str]:
        """获取特定 skill 的版本"""
        skill = self.get_skill_info(skill_name)
        if skill:
            return skill.get('version', self.get_plugin_version())
        return None
    
    def parse_semver(self, version: str) -> Tuple[int, int, int]:
        """解析语义化版本号"""
        match = re.match(r'(\d+)\.(\d+)\.(\d+)', version)
        if not match:
            return (0, 0, 0)
        return tuple(map(int, match.groups()))
    
    def bump_version(self, version: str, bump_type: str) -> str:
        """升级版本号
        
        Args:
            version: 当前版本（如 "1.2.3"）
            bump_type: 升级类型（major/minor/patch）
        
        Returns:
            新版本号
        """
        major, minor, patch = self.parse_semver(version)
        
        if bump_type == 'major':
            major += 1
            minor = 0
            patch = 0
        elif bump_type == 'minor':
            minor += 1
            patch = 0
        elif bump_type == 'patch':
            patch += 1
        else:
            raise ValueError(f"Invalid bump type: {bump_type}")
        
        return f"{major}.{minor}.{patch}"
    
    def update_plugin_version(self, new_version: str) -> bool:
        """更新插件版本"""
        if not self.package_json.exists():
            return False
        
        try:
            with open(self.package_json, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            data['version'] = new_version
            
            with open(self.package_json, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"Error updating version: {e}")
            return False


def main():
    """CLI 入口"""
    import sys
    
    vm = VersionManager()
    
    if len(sys.argv) < 2:
        print("Usage: version_manager.py <command> [args]")
        print("Commands: list, info <skill>, bump <major|minor|patch>")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == 'list':
        print(f"Plugin Version: {vm.get_plugin_version()}\n")
        print("Skills:")
        for name, version in vm.list_skills().items():
            print(f"  {name}: {version}")
    
    elif command == 'info' and len(sys.argv) > 2:
        skill_name = sys.argv[2]
        version = vm.get_skill_version(skill_name)
        if version:
            print(f"{skill_name}: {version}")
        else:
            print(f"Skill '{skill_name}' not found")
    
    elif command == 'bump' and len(sys.argv) > 2:
        bump_type = sys.argv[2]
        current = vm.get_plugin_version()
        new_version = vm.bump_version(current, bump_type)
        print(f"Current: {current}")
        print(f"New: {new_version}")
        
        if input("Update? (y/n): ").lower() == 'y':
            if vm.update_plugin_version(new_version):
                print("✓ Version updated")
            else:
                print("✗ Update failed")
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == '__main__':
    main()
