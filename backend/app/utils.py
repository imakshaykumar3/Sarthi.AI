# app/utils.py
import json, re
from datetime import datetime
from typing import Dict, Any, List, Optional

def safe_dict(val: Any) -> Dict[str, Any]:
    if isinstance(val, dict): return val
    return {}

def get_last_user_message(messages: List[Any]) -> str:
    if not messages: return ""
    last_msg = messages[-1]
    if hasattr(last_msg, "content"): return str(last_msg.content)
    if isinstance(last_msg, dict): return str(last_msg.get("content", ""))
    return str(last_msg)

def extract_json_from_text(text: str) -> Dict[str, Any]:
    try:
        return json.loads(text)
    except:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            try: return json.loads(match.group(0))
            except: pass
    return {}

def get_trip(details: Any, key: str) -> Optional[str]:
    d = safe_dict(details)
    return d.get(key)

def clean_content(content):
    if isinstance(content, list):
        return " ".join([c.get("text", "") for c in content if "text" in c])
    return str(content)