from lint import typed_numerals as tn


def test_hand_typed_numbers_are_caught_and_allowlist_passes():
    text = ("Section 5.1 reports 17,748 clearings. H1 and D3' in 2018; W = 60 and alpha = 0.05; "
            "a 3-way line; the 2 x 2 table; `claude-haiku-4-5-20251001`; doi:10.4121/uuid:abc; "
            "the tag p7-v1.1 and B = 10,000 with seed 20261201.\n")
    tokens = [v["token"] for v in tn.find_violations(text)]
    assert tokens == ["17,748"]


def test_placeholders_and_filled_spans_are_not_hand_typed():
    assert tn.find_violations("Exposure {{e1/exposure.json>units|int}} of all.\n") == []
    text = "Exposure 11.41% of clearings, 7 lines.\n"
    start = text.index("11.41%")
    assert [v["token"] for v in tn.find_violations(text, [(start, start + len("11.41%"))])] == ["7"]


def test_every_registered_constant_cites_a_source():
    assert all("prereg/" in src or "algorithm" in src for src in tn.REGISTERED.values())
