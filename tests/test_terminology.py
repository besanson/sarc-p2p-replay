from lint import terminology


def rules(text: str) -> list[str]:
    return [v["rule"] for v in terminology.lint_text(text)]


def test_simulation_flagged_unless_negated() -> None:
    assert rules("We run a simulation of the process.") == ["replay-not-simulation"]
    assert rules("This is a replay, not a simulation.") == []


def test_defect_needs_a_predicate_in_the_paragraph() -> None:
    assert rules("Many lines were defective.") == ["defect-scope"]
    assert rules("Many lines were defective: D4 failed.") == []
    assert rules("A defect is a failed predicate.") == []


def test_would_have_held_only_for_the_gate() -> None:
    assert rules("The clerk would have held it.") == ["would-have-held-scope"]
    assert rules("The gate would have held it.") == []


def test_banned_words_and_local_negation() -> None:
    for word in ("prevented", "caused", "lost", "fraud", "ready"):
        assert rules(f"The gate {word} it.") == ["banned"], word
    assert rules("We make no causal claim.") == []
    assert rules("No readiness threshold is set.") == []


def test_code_is_not_prose() -> None:
    assert rules("Call `simulate()` here.\n\n```\nfraud = 1\n```\n") == []


def test_negation_elsewhere_in_paragraph_does_not_excuse() -> None:
    assert rules("We do not name vendors. The gate prevented payment.") == ["banned"]


def test_repository_prose_is_clean() -> None:
    result = terminology.lint()
    assert result["files"], "README.md must be a target"
    assert result["all_clean"], result
