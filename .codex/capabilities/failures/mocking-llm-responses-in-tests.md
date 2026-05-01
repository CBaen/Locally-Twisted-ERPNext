---
name: Mocking LLM responses in unit tests
type: failure
date_discovered: 2026-04-25
---

## What was tried

Writing unit tests against code that calls an LLM by mocking the LLM's response. The intent: deterministic tests, no API costs, no network dependencies, fast feedback loop.

A typical attempt:

```python
def test_summarize_handles_long_input(mock_anthropic):
    mock_anthropic.messages.create.return_value = MagicMock(
        content=[MagicMock(text="A short, neat summary.")]
    )
    result = summarize(very_long_input)
    assert "summary" in result.lower()
```

## Why it didn't work

The mock answers the question "does my Python correctly pass arguments and parse responses." It does not answer the question the test was trying to ask: "does my prompt actually produce a useful result." Those are different questions, and only the second one matters for an LLM-based feature.

Concretely, mocked tests pass when:
- The prompt has degraded after a refactor and now produces garbage. (The mock returns the original neat string regardless.)
- Token limits are exceeded silently and the model truncates. (The mock has no size.)
- A model upgrade changes output format. (The mock is frozen on the old format.)

You ship the broken prompt with a green test suite.

## What to do instead

Write **two** layers of tests:

1. **Unit tests for the surrounding code only.** Test the input transformation, output parsing, error handling, retry logic — everything except the LLM call. Mock the LLM here; the mock is honest because you're testing your code, not the model's output.

2. **Eval-style integration tests for the LLM behavior itself.** A small set of input/output pairs run against the *real* model on a cadence (CI nightly, pre-release, manual). These tests are slower, costlier, and non-deterministic — but they answer the question that actually matters. Use a framework like [promptfoo](https://www.promptfoo.dev/) or [DeepEval](https://github.com/confident-ai/deepeval), or write the harness yourself.

Together, these give you fast feedback on plumbing and slow but trustworthy feedback on the prompt.

## Recurrence risk

Evergreen. The temptation to mock the LLM will resurface every time someone wants tests to run faster or cheaper. The cost-benefit feels right in the moment and shows up wrong in production. Re-document the alternative in your project's testing rules so contributors don't relitigate the decision every time.
