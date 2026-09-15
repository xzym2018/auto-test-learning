# -*- coding: utf-8 -*-
"""
Gallery UI Automation Skeleton
=============================
- ADB 客户端、UI 层级解析、图库列表遍历与定位。
- 与业务无关，纯骨架；只使用 ADB 和 UI 层级。
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import time
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple, Dict, Any

# 相对导入 AdbClient
try:
    from adb_client import AdbClient, AdbError, Rect, UiNode, UiTreeSnapshot, ARTIFACT_ROOT, DEFAULT_PACKAGE, DEFAULT_COMPONENT
except ImportError:
    from adb_ui_automation.adb_client import AdbClient, AdbError, Rect, UiNode, UiTreeSnapshot, ARTIFACT_ROOT, DEFAULT_PACKAGE, DEFAULT_COMPONENT


# PLACEHOLDER_GALLERY_PARSER: 
# 源脚本中关于特定业务（如颜色、标题、已完成）的匹配逻辑。
# 这里用 "gallery_card_fingerprint" 和 "gallery_card_completion_mark" 抽象。

def gallery_card_fingerprint(node: UiNode, xml_content: str) -> str:
    """计算卡片指纹，用于去重（业务无关，只看资源ID和文本）。"""
    text = node.text.strip() or node.content_desc.strip()
    # 简单指纹：resource-id + 文本
    return f"{node.resource_id}|{text}"

def gallery_card_completion_mark(node: UiNode) -> bool:
    """判断卡片是否标记为‘已完成’（业务无关，只看文本）。"""
    text = node.text.strip().lower() + node.content_desc.strip().lower()
    # PLACEHOLDER: 根据业务语言添加，如 "done", "completed"
    return "done" in text or "completed" in text


class GalleryAutomation:
    def __init__(self, client: AdbClient):
        self.client = client
        self.session_dir = ARTIFACT_ROOT / f"gallery-run-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        self.session_dir.mkdir(parents=True, exist_ok=True)

    def _save_snapshot(self, tag: str, snapshot: UiTreeSnapshot) -> None:
        xml_path = self.session_dir / f"{tag}.xml"
        png_path = self.session_dir / f"{tag}.png"
        with open(xml_path, "w", encoding="utf-8") as f:
            f.write(snapshot.xml)
        self.client.screenshot(str(png_path))

    def wait_for_stable_ui(self) -> UiTreeSnapshot:
        """等待 UI 稳定（连续两次 dump 一致）。"""
        prev_content = None
        for i in range(5):
            snapshot = self.client.dump_ui(str(self.session_dir / f"dump_{i}.xml"))
            if snapshot.xml == prev_content:
                return snapshot
            prev_content = snapshot.xml
            time.sleep(1.0)
        return snapshot

    def find_gallery_cards(self) -> List[UiNode]:
        """查找当前屏幕中所有图库卡片（可点击/可长按的大尺寸元素）。"""
        snapshot = self.wait_for_stable_ui()
        cards = []
        for node in snapshot.nodes:
            if node.clickable or node.long_clickable:
                # 简单启发：忽略导航栏、状态栏等小元素
                if node.rect.width > 200 and node.rect.height > 200:
                    cards.append(node)
        return cards

    def scroll_and_find_target(self, max_swipes: int = 20, target_index: int = 1) -> Optional[UiNode]:
        """自动翻页查找目标卡片（默认第一个）。"""
        seen_fingerprints = set()
        current_index = 0
        
        for i in range(max_swipes):
            cards = self.find_gallery_cards()
            for card in cards:
                fp = gallery_card_fingerprint(card, self.client.xml if hasattr(self.client, 'xml') else "")
                if fp not in seen_fingerprints:
                    seen_fingerprints.add(fp)
                    current_index += 1
                    if current_index == target_index:
                        self._save_snapshot("target_found", self.client.snapshot if hasattr(self.client, 'snapshot') else None)
                        return card
            
            # 向下翻页
            w, h = self.client.get_window_size()
            self.client.swipe(w // 2, int(h * 0.6), w // 2, int(h * 0.4), 500)
            time.sleep(1.5)
            
        return None

    def click_target(self, target: UiNode) -> None:
        """点击目标并截图取证。"""
        self.client.tap(int(target.rect.center_x), int(target.rect.center_y))
        time.sleep(1.0)
        self._save_snapshot("after_click", self.client.dump_ui(str(self.session_dir / "after_click.xml")))

    def run(self, target_index: int = 1) -> Dict[str, Any]:
        """执行完整流程。"""
        print(f"启动 {DEFAULT_PACKAGE}...")
        self.client.force_stop(DEFAULT_PACKAGE)
        time.sleep(1)
        self.client.shell("am", "start", "-n", DEFAULT_COMPONENT)
        time.sleep(3)
        
        target = self.scroll_and_find_target(target_index=target_index)
        
        if target:
            print(f"找到目标: {target.text or target.content_desc} ({target.rect.as_list()})")
            self.click_target(target)
            result = {"status": "success", "target": asdict(target.rect)}
        else:
            print("未找到目标。")
            result = {"status": "not_found"}
            
        with open(self.session_dir / "summary.json", "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
            
        return result

if __name__ == "__main__":
    auto = GalleryAutomation(AdbClient())
    auto.run(target_index=1)
