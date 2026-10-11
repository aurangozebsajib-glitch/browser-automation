
from backend.parser import parse_ideas, is_duplicate
def test_parse():
    raw="1. Title One: A story about cats\n2. Title Two - A dog adventure"
    ideas=parse_ideas(raw)
    assert len(ideas)>=2
    assert not is_duplicate("Title One", ["title two"])
    assert is_duplicate("Title One", ["Title One"])
    print("ok")
if __name__=="__main__":
    test_parse()
