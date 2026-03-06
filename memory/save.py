"""
save.py — Save Operations
Functions to persist problems, feedback, and OCR corrections.
"""

import sqlite3
import json
from typing import List

from memory.db_init import DB_PATH, init_db


def save_problem(
    input_text: str,
    input_type: str,
    parsed: dict,
    answer: str,
    explanation: str,
    confidence: int,
    feedback: str = "",
    feedback_comment: str = "",
    rag_sources: List[str] = None
) -> int:
    """Save a solved problem to memory. Returns the new row id."""
    init_db()
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.execute("""
        INSERT INTO problems
            (input_text, input_type, parsed_json, topic, answer, explanation,
             confidence, feedback, feedback_comment, rag_sources)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        input_text,
        input_type,
        json.dumps(parsed),
        parsed.get("topic", "unknown"),
        answer,
        explanation,
        confidence,
        feedback,
        feedback_comment,
        json.dumps(rag_sources or [])
    ))
    conn.commit()
    row_id = cursor.lastrowid
    conn.close()
    return row_id


def update_feedback(problem_id: int, feedback: str, comment: str = ""):
    """Update feedback on a saved problem."""
    init_db()
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("""
        UPDATE problems SET feedback = ?, feedback_comment = ?
        WHERE id = ?
    """, (feedback, comment, problem_id))
    conn.commit()
    conn.close()


def save_ocr_correction(original: str, corrected: str):
    """Store an OCR correction for future reference."""
    init_db()
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute(
        "INSERT INTO ocr_corrections (original, corrected) VALUES (?, ?)",
        (original, corrected)
    )
    conn.commit()
    conn.close()
