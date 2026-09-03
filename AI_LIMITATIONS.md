# AI Layer - Known Limitations

Documents real accuracy issues found during testing of the local AI
model (Ollama, qwen2.5:1.5b), and how each was handled. Kept here so
these are documented findings, not things quietly missed - and to
directly support the SRS's human-in-the-loop requirement (Section 2,
constraint) and NFR-12 (AI output must be labeled, not treated as
authoritative).

## Why a local model, briefly

Ollama + qwen2.5:1.5b was chosen over a hosted API (e.g. Gemini) to
keep the AI layer genuinely free with no API key, appropriate for a
student project's budget constraint (SRS 2.4). This trades some
accuracy for zero ongoing cost - the tradeoff below is a direct
consequence of that choice, not an implementation mistake.

## Issues found, and what was done about each

| File | Issue found | Example | Resolution |
|---|---|---|---|
| `summarize.py` | Arithmetic errors - miscalculated a percentage change | Calculated 142.3 -> 146.2 as "4.05%" (actual: 2.74%) | Not fixable via prompting (small models are broadly unreliable at arithmetic) - documented, not resolved |
| `classify.py` | Wrong/missing category judgment | Missed "Digital Finance" on a stablecoin-regulation article; added "Digital Finance" incorrectly to CPI data | Fixed - added a worked example to the prompt (few-shot), verified correct on 3 fresh test cases afterward |
| `relevance.py` | Doubled/echoed prompt label in output | Output started with "Relevance: Relevance: ..." | Fixed - stripped in code (deterministic post-processing) |
| `relevance.py` | Imprecise/confusing phrasing | Said "BOT's work in financial stability in Kenya" instead of clearly framing Tanzania's own perspective | Not fixed - documented as a known limitation |
| `relevance.py` | Minor fabricated framing | Claimed CPI data was shown "relative to international standards" when the input data contained no such comparison | Not fixed - documented as a known limitation |
| Multiple files | Missing spaces between words | "monetarypolicy", "of4.05%", "retainthe" | Tokenization quirk of this small model - not reliably fixable via prompting, documented |

## What this means for the project

- Two real issues were found and genuinely fixed through iteration
  (classify.py's category accuracy, relevance.py's doubled label) -
  not just accepted on first output.
- The remaining issues are genuine limitations of running a small
  (1.5B parameter) model on CPU, not implementation bugs. This is
  consistent with the accuracy-vs-cost tradeoff discussed before
  choosing a local model over a hosted API.
- This is precisely why the SRS requires human-in-the-loop review
  (Reviewer/Supervisor role) and NFR-12's AI-generated labeling -
  these findings are direct, tested evidence for why that requirement
  exists, not a theoretical concern.
- A future upgrade path (documented, not implemented): switching
  `llm_client.py` to call a hosted API (e.g. Gemini's free tier,
  investigated earlier in this project) instead of Ollama would
  likely resolve most of the above, at the cost of needing an API key
  and internet dependency for the AI layer.
