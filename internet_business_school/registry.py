"""Persistent students and a durable certificate key, so a certificate issued today verifies next year."""

from __future__ import annotations

import json
import os
import secrets
import time

from .core import School, Student


def _key_for(store: str) -> bytes:
    """IBS_CERT_KEY if set, else a random key kept next to the store (created once, never regenerated)."""
    env = os.environ.get("IBS_CERT_KEY")
    if env:
        return env.encode()
    path = f"{os.path.splitext(store)[0]}.key"
    try:
        with open(path, encoding="utf-8") as fh:
            key = fh.read().strip()
        if key:
            return key.encode()
    except FileNotFoundError:
        pass
    key = secrets.token_hex(32)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        fh.write(key)
    return key.encode()


class Registry:
    def __init__(self, store: str):
        self.store = store
        self.school = School(key=_key_for(store))
        try:
            with open(store, encoding="utf-8-sig") as fh:
                doc = json.load(fh)
        except FileNotFoundError:
            doc = {"students": {}}
        if not isinstance(doc, dict) or not isinstance(doc.get("students"), dict):
            raise ValueError(f"{store}: not a school registry")
        self.doc = doc

    def _record(self, name: str) -> dict:
        name = " ".join(name.split())
        if name not in self.doc["students"]:
            raise ValueError(f"no student {name!r}; run `enroll` first")
        return self.doc["students"][name]

    def student(self, name: str) -> Student:
        rec = self._record(name)
        return Student(" ".join(name.split()), dict(rec["grades"]), set(rec["completed"]))

    def enroll(self, name: str) -> bool:
        name = " ".join(name.split())
        if not name:
            raise ValueError("student name is required")
        if name in self.doc["students"]:
            return False
        self.doc["students"][name] = {
            "grades": {},
            "completed": [],
            "evidence": {},
            "enrolled": time.strftime("%Y-%m-%d"),
        }
        return True

    def submit(self, name: str, lesson: str, levels: dict, metrics: dict, evidence: str = "") -> dict:
        if lesson not in self.school.lessons:
            raise ValueError(f"unknown lesson {lesson!r}; see `curriculum`")
        s = self.student(name)
        result = self.school.submit(s, lesson, levels or None, metrics or None)
        rec = self._record(name)
        rec["grades"], rec["completed"] = s.grades, sorted(s.completed)
        if evidence and result["passed"]:
            rec["evidence"][lesson] = evidence
        result["next"] = self.school.next_lesson(s)
        return result

    def save(self):
        tmp = f"{self.store}.tmp"
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(self.doc, fh, indent=2)
        os.replace(tmp, self.store)


def parse_pairs(items: list[str], what: str) -> dict:
    """["insight=4", "evidence=3"] -> {"insight": 4.0, ...}"""
    out = {}
    for item in items or []:
        k, sep, v = item.partition("=")
        if not sep or not k.strip():
            raise ValueError(f"{what} must look like name=value, got {item!r}")
        try:
            out[k.strip()] = float(v)
        except ValueError:
            raise ValueError(f"{what} {k.strip()!r} needs a number, got {v!r}") from None
    return out
