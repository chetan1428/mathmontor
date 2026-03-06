"""
memory — Memory & Self-Learning Layer (Package)
Uses SQLite to persist problems, answers, feedback.
Retrieves similar past problems using keyword similarity.
"""

from memory.db_init import DB_PATH, init_db
from memory.save import save_problem, update_feedback, save_ocr_correction
from memory.retrieve_similar_problems import (
    find_similar,
    get_ocr_corrections,
    get_all_problems,
    get_stats,
    format_memory_context,
)

__all__ = [
    "DB_PATH",
    "init_db",
    "save_problem",
    "update_feedback",
    "save_ocr_correction",
    "find_similar",
    "get_ocr_corrections",
    "get_all_problems",
    "get_stats",
    "format_memory_context",
]

if __name__ == "__main__":
    init_db()
    print("Memory DB initialized at:", DB_PATH)
    print("Stats:", get_stats())
