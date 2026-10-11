
import re, json, uuid, hashlib

def parse_ideas(raw: str):
    raw = raw.strip()
    ideas = []
    # Try JSON array
    try:
        data = json.loads(raw)
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    title = item.get("title") or item.get("name") or str(item)[:60]
                    desc = item.get("description") or item.get("desc") or item.get("idea") or ""
                    ideas.append({"title": title.strip(), "description": desc.strip(), "raw": json.dumps(item, ensure_ascii=False)})
                else:
                    ideas.append({"title": str(item)[:80], "description": str(item), "raw": str(item)})
            if ideas:
                return ideas
    except:
        pass

    # Numbered list / markdown list
    lines = [l.strip() for l in raw.splitlines() if l.strip()]
    pattern = re.compile(r'^(?:\d+[\.\)\-]|\-|\*|•)\s*(.+)')
    for line in lines:
        m = pattern.match(line)
        content = m.group(1) if m else line
        if len(content) < 10: 
            continue
        # Split title: description by - or :
        if ":" in content[:60]:
            parts = content.split(":",1)
            title, desc = parts[0].strip(), parts[1].strip()
        elif " - " in content:
            parts = content.split(" - ",1)
            title, desc = parts[0].strip(), parts[1].strip()
        else:
            title, desc = content[:70], content
        ideas.append({"title": title, "description": desc, "raw": content})

    # fallback: split by double newline
    if not ideas:
        chunks = re.split(r'
\s*
', raw)
        for c in chunks:
            if len(c.strip())>15:
                ideas.append({"title": c[:70], "description": c, "raw": c})

    return ideas

def stable_idea_id(title):
    h = hashlib.md5(title.encode()).hexdigest()[:6].upper()
    return f"IDE_{h}"

def is_duplicate(new_title, existing_titles):
    nt = new_title.lower().strip()
    for et in existing_titles:
        if nt == et.lower().strip():
            return True
        # simple containment
        if nt in et.lower() or et.lower() in nt:
            if abs(len(nt)-len(et))<10:
                return True
    return False
