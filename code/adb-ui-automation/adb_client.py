# -*- coding: utf-8 -*-
"""
ADB UI 自动化骨架
==================
通用 ADB 客户端、UI 层级解析与长列表遍历，与业务无关。
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

ARTIFACT_ROOT = Path("artifacts")
DEFAULT_PACKAGE = os.environ.get("APP_PACKAGE", "com.example.gallery")
DEFAULT_COMPONENT = os.environ.get("APP_COMPONENT", f"{DEFAULT_PACKAGE}/.ui.SplashActivity")
ADB_PATH = os.environ.get("ADB_PATH", "adb")


@dataclass(frozen=True, order=True)
class Rect:
    left: int
    top: int
    right: int
    bottom: int

    @property
    def width(self) -> int: return max(0, self.right - self.left)
    @property
    def height(self) -> int: return max(0, self.bottom - self.top)
    @property
    def area(self) -> int: return self.width * self.height
    @property
    def center_x(self) -> float: return (self.left + self.right) / 2
    @property
    def center_y(self) -> float: return (self.top + self.bottom) / 2

    def intersect(self, other: "Rect") -> "Rect | None":
        result = Rect(
            max(self.left, other.left), max(self.top, other.top),
            min(self.right, other.right), min(self.bottom, other.bottom),
        )
        return result if result.width > 0 and result.height > 0 else None

    def as_list(self) -> list[int]:
        return [self.left, self.top, self.right, self.bottom]


@dataclass(frozen=True)
class UiNode:
    rect: Rect
    class_name: str
    package: str
    resource_id: str
    text: str
    content_desc: str
    clickable: bool
    checkable: bool
    checked: bool
    enabled: bool
    focusable: bool
    focused: bool
    selected: bool
    scrollable: bool
    long_clickable: bool
    password: bool


class AdbError(RuntimeError):
    pass


class UiTreeSnapshot:
    def __init__(self, root: UiNode, nodes: List[UiNode], xml: str, width: int, height: int):
        self.root = root
        self.nodes = nodes
        self.xml = xml
        self.width = width
        self.height = height


BOUNDS_RE = re.compile(r"^\[(\d+),(\d+)\]\[(\d+),(\d+)\]$")


def parse_bounds(bounds_str: str) -> Rect:
    match = BOUNDS_RE.match(bounds_str)
    if not match:
        raise ValueError(f"Invalid bounds format: {bounds_str}")
    return Rect(int(match.group(1)), int(match.group(2)), int(match.group(3)), int(match.group(4)))


def parse_bool(value: str) -> bool:
    return value.lower() == "true"


def parse_ui_xml(xml_content: str, width: int, height: int) -> UiTreeSnapshot:
    nodes = []
    root = None
    # Regex parsing is faster than XML parsing for large dumps in Python
    pattern = re.compile(r'<node\s+([^>]*?)\/?>')
    for match in pattern.finditer(xml_content):
        attrs_str = match.group(1)
        attrs = dict(re.findall(r'(\w[\w-]*)="([^"]*)"', attrs_str))
        
        try:
            rect = parse_bounds(attrs.get("bounds", "[0,0][0,0]"))
        except ValueError:
            continue

        node = UiNode(
            rect=rect,
            class_name=attrs.get("class", ""),
            package=attrs.get("package", ""),
            resource_id=attrs.get("resource-id", ""),
            text=attrs.get("text", ""),
            content_desc=attrs.get("content-desc", ""),
            clickable=parse_bool(attrs.get("clickable", "false")),
            checkable=parse_bool(attrs.get("checkable", "false")),
            checked=parse_bool(attrs.get("checked", "false")),
            enabled=parse_bool(attrs.get("enabled", "true")),
            focusable=parse_bool(attrs.get("focusable", "false")),
            focused=parse_bool(attrs.get("focused", "false")),
            selected=parse_bool(attrs.get("selected", "false")),
            scrollable=parse_bool(attrs.get("scrollable", "false")),
            long_clickable=parse_bool(attrs.get("long-clickable", "false")),
            password=parse_bool(attrs.get("password", "false")),
        )
        nodes.append(node)
        if root is None:
            root = node
            
    if root is None:
        root = UiNode(Rect(0,0,width,height), "", "", "", "", "", False, False, False, True, False, False, False, False, False, False)

    return UiTreeSnapshot(root, nodes, xml, width, height)


class AdbClient:
    def __init__(self, adb_path: str = ADB_PATH, serial: str | None = None):
        self.adb_path = adb_path
        self.serial = serial
        self._base_cmd = [self.adb_path]
        if self.serial:
            self._base_cmd.extend(["-s", self.serial])

    def _run(self, *args: str, timeout: int = 20) -> str:
        cmd = self._base_cmd + list(args)
        try:
            completed = subprocess.run(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                text=True, encoding="utf-8", errors="replace", timeout=timeout, check=False,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)
            )
            if completed.returncode != 0:
                raise AdbError(f"ADB failed: {' '.join(args)}\n{completed.stderr.strip()}")
            return completed.stdout.strip()
        except subprocess.TimeoutExpired:
            raise AdbError(f"Timeout: {' '.join(args)}")

    def shell(self, *args: str, timeout: int = 20) -> str:
        return self._run("shell", *args, timeout=timeout)

    def pull(self, remote: str, local: str, timeout: int = 60) -> None:
        self._run("pull", remote, local, timeout=timeout)
        
    def screenshot(self, local_path: str, timeout: int = 10) -> None:
        self.shell("screencap", "-p", "/sdcard/screen_tmp.png", timeout=timeout)
        self.pull("/sdcard/screen_tmp.png", local_path, timeout=timeout)
        self.shell("rm", "/sdcard/screen_tmp.png", timeout=5)

    def force_stop(self, package: str) -> None:
        self.shell("am", "force-stop", package)

    def get_window_size(self) -> Tuple[int, int]:
        output = self.shell("wm", "size")
        match = re.search(r"Physical size: (\d+)x(\d+)", output)
        if not match:
            # Fallback for some weird devices
            match = re.search(r"(\d+)x(\d+)", output)
        if not match:
            raise AdbError(f"Cannot parse window size: {output}")
        return int(match.group(1)), int(match.group(2))

    def dump_ui(self, local_path: str, timeout: int = 20) -> UiTreeSnapshot:
        size = self.get_window_size()
        self.shell("uiautomator", "dump", "/sdcard/ui_dump.xml", timeout=timeout)
        self.pull("/sdcard/ui_dump.xml", local_path, timeout=timeout)
        self.shell("rm", "/sdcard/ui_dump.xml", timeout=5)
        with open(local_path, "r", encoding="utf-8") as f:
            content = f.read()
        return parse_ui_xml(content, size[0], size[1])

    def swipe(self, start_x: int, start_y: int, end_x: int, end_y: int, duration_ms: int = 300) -> None:
        self.shell("input", "swipe", str(start_x), str(start_y), str(end_x), str(end_y), str(duration_ms))

    def tap(self, x: int, y: int) -> None:
        self.shell("input", "tap", str(x), str(y))

    def scroll_forward(self, bounds: Rect) -> None:
        cx = int(bounds.center_x)
        cy = int(bounds.center_y)
        h = bounds.height // 2
        self.swipe(cx, cy + h // 2, cx, cy - h // 2, 500)

    def wait_for_stable_ui(self, max_attempts: int = 5, delay: float = 1.0, local_path: str = "/tmp/ui_dump.xml") -> UiTreeSnapshot:
        prev_content = None
        for i in range(max_attempts):
            size = self.get_window_size()
            self.shell("uiautomator", "dump", "/sdcard/ui_dump.xml", timeout=20)
            self.pull("/sdcard/ui_dump.xml", local_path, timeout=10)
            with open(local_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            if content == prev_content:
                return parse_ui_xml(content, size[0], size[1])
            
            prev_content = content
            time.sleep(delay)
        
        return parse_ui_xml(content, size[0], size[1]) if content else parse_ui_xml("", 0, 0)
