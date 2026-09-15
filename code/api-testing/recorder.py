# -*- coding: utf-8 -*-
"""
测试结果记录器
==============
用例结果登记、控制台实时输出、汇总统计、JSON 落盘。
与框架无关，可配合任何执行器使用。
"""
import datetime
import json


class ResultRecorder:
    def __init__(self):
        self.results = []
        self.pass_count = 0
        self.fail_count = 0

    def record(self, cid, name, method, path, status, expected, passed, detail=""):
        """登记一条用例结果并实时打印。"""
        if passed:
            self.pass_count += 1
        else:
            self.fail_count += 1
        tag = "PASS" if passed else "FAIL"
        self.results.append({
            "id": cid, "name": name, "method": method, "path": path,
            "status": status, "expected": expected, "passed": passed,
            "detail": detail,
        })
        suffix = f" - {detail}" if detail else ""
        print(f"  [{tag}] {cid}: {method} {path} -> {status} (exp {expected}){suffix}")

    def summary(self):
        """打印通过率汇总，返回失败用例列表。"""
        total = self.pass_count + self.fail_count
        rate = self.pass_count / total * 100 if total else 0
        print("\n" + "=" * 60)
        print(f"RESULT: {self.pass_count} PASS, {self.fail_count} FAIL, "
              f"{total} TOTAL ({rate:.1f}%)")
        print("=" * 60)
        failed = [r for r in self.results if not r["passed"]]
        if failed:
            print("\nFAILED:")
            for r in failed:
                print(f"  [{r['id']}] {r['name']} -> {r['status']} (exp {r['expected']})")
                if r["detail"]:
                    print(f"       {r['detail']}")
        return failed

    def save(self, path):
        """结果落盘为 JSON。"""
        total = self.pass_count + self.fail_count
        rate = self.pass_count / total * 100 if total else 0
        payload = {
            "test_time": datetime.datetime.now().isoformat(),
            "summary": {
                "pass": self.pass_count, "fail": self.fail_count,
                "total": total, "rate": f"{rate:.1f}%",
            },
            "results": self.results,
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        print(f"\n结果已保存: {path}")
