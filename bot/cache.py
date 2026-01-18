from __future__ import annotations

import json
import os
import pickle
from collections import deque
from typing import TYPE_CHECKING, Any, Dict, List

from bot import app_vars
from bot.migrators import cache_migrator

if TYPE_CHECKING:
    from bot.player.track import Track


cache_data_type = Dict[str, Any]


class Cache:
    def __init__(self, cache_data: cache_data_type):
        self.cache_version = cache_data["cache_version"] if "cache_version" in cache_data else CacheManager.version
        self.recents: deque[Track] = (
            cache_data["recents"]
            if "recents" in cache_data
            else deque(maxlen=app_vars.recents_max_lenth)
        )
        self.favorites: Dict[str, List[Track]] = (
            cache_data["favorites"] if "favorites" in cache_data else {}
        )
        self.queue: List[Track] = cache_data["queue"] if "queue" in cache_data else []

    @property
    def data(self):
        return {
            "cache_version": self.cache_version,
            "recents": self.recents,
            "favorites": self.favorites,
            "queue": self.queue,
        }


class CacheManager:
    version = 4

    def __init__(self, file_name: str) -> None:
        self.original_file_name = os.path.abspath(file_name)
        self._prepare_paths(file_name)
        self._ensure_cache_dir()
        try:
            data = cache_migrator.migrate(self, self._load())
            self.cache = Cache(data)
        except FileNotFoundError:
            self.cache = Cache({})
            self._dump(self.cache.data)
        else:
            self._dump(self.cache.data)

    def _prepare_paths(self, file_name: str) -> None:
        abs_path = os.path.abspath(file_name)
        if os.path.isdir(abs_path):
            self.cache_dir = abs_path
        else:
            base_dir = os.path.splitext(abs_path)[0]
            self.cache_dir = base_dir
        self.recents_file = os.path.join(self.cache_dir, "recents.dat")
        self.favorites_file = os.path.join(self.cache_dir, "favorites.dat")
        self.queue_file = os.path.join(self.cache_dir, "queue.dat")
        self.meta_file = os.path.join(self.cache_dir, "meta.json")

    def _dump(self, data: cache_data_type):
        os.makedirs(self.cache_dir, exist_ok=True)
        with open(self.recents_file, "wb") as f:
            pickle.dump(data.get("recents", deque(maxlen=app_vars.recents_max_lenth)), f)
        with open(self.favorites_file, "wb") as f:
            pickle.dump(data.get("favorites", {}), f)
        with open(self.queue_file, "wb") as f:
            pickle.dump(data.get("queue", []), f)
        with open(self.meta_file, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "cache_version": data.get("cache_version", self.version),
                },
                f,
            )

    def _load(self) -> cache_data_type:
        try:
            return self._load_split()
        except FileNotFoundError:
            return self._load_single()

    def _load_split(self) -> cache_data_type:
        with open(self.meta_file, "r", encoding="utf-8") as f:
            try:
                meta = json.load(f)
            except Exception:
                f.seek(0)
                meta = pickle.load(f)
        with open(self.recents_file, "rb") as f:
            recents = pickle.load(f)
        with open(self.favorites_file, "rb") as f:
            favorites = pickle.load(f)
        with open(self.queue_file, "rb") as f:
            queue = pickle.load(f)
        return {
            "cache_version": meta.get("cache_version", self.version),
            "recents": recents,
            "favorites": favorites,
            "queue": queue,
        }

    def _load_single(self) -> cache_data_type:
        with open(self.original_file_name, "rb") as f:
            return pickle.load(f)

    def _ensure_cache_dir(self):
        os.makedirs(self.cache_dir, exist_ok=True)

    def close(self):
        pass

    def save(self):
        self._dump(self.cache.data)
