from lint import proof_status


def test_allowed_tags_with_scope_are_clean():
    text = "P1.\nPROOF-STATUS: machine-checked (tests/test_properties.py, 400 cases)\n"
    assert proof_status.lint_text(text)["clean"]
    assert proof_status.lint_text("PROOF-STATUS: pending-human-review\n")["clean"]


def test_proven_is_forbidden():
    result = proof_status.lint_text("PROOF-STATUS: proven\n")
    assert result["forbidden"] == ["proven"] and not result["clean"]


def test_machine_checked_needs_source_and_domain():
    no_domain = proof_status.lint_text("PROOF-STATUS: machine-checked (tests/test_properties.py)\n")
    assert not no_domain["clean"] and no_domain["scope_violations"][0]["has_source"]
    no_source = proof_status.lint_text("PROOF-STATUS: machine-checked (400 cases)\n")
    assert not no_source["clean"] and no_source["scope_violations"][0]["has_domain"]
    split = proof_status.lint_text("PROOF-STATUS: machine-checked\n\ntests/test_properties.py 400\n")
    assert not split["clean"]


def test_repository_property_tags_are_clean():
    targets = proof_status.default_targets()
    assert any(p.name == "test_properties.py" for p in targets)
    assert proof_status.main([]) == 0
    text = next(p for p in targets if p.name == "test_properties.py").read_text(encoding="utf-8")
    assert len(proof_status.find_tags(text)) == 5
