from typing import List, Dict

def flatten_skills(skills_json: Dict[str, List[str]]) -> List[str]:
    """
    Convert categorized skills.json into a flat skill list.
    """
    flat = []
    for _, skills in skills_json.items():
        flat.extend(skills)
    return list(set(flat))
