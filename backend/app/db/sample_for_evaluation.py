"""
Samples a diverse set of real, already-processed publications for
manual evaluation - satisfies the brief's requirement for "a small
set of manually classified publications and expected summaries...
for system evaluation."

Reuses already-processed records (real AI summary + topics already
generated) rather than requiring fresh manual data entry - the human
reviewer marks whether the EXISTING AI output is correct, which is
faster and just as valid an evaluation.

Samples across institutions for diversity, writes output as a
readable markdown file for manual review.
"""

from database import get_session
from db_models import Publication

TARGET_PER_INSTITUTION = 5

session = get_session()
try:
    institutions = session.query(Publication.institution).filter(
        Publication.processed == True
    ).distinct().all()
    institutions = [i[0] for i in institutions if i[0] != "TEST"]

    sample = []
    for inst in institutions:
        records = session.query(Publication).filter(
            Publication.institution == inst,
            Publication.processed == True,
        ).limit(TARGET_PER_INSTITUTION).all()
        sample.extend(records)
finally:
    session.close()

print(f"Sampled {len(sample)} records across {len(institutions)} institutions")

output_path = "/workspaces/ai-innovation-observatory/evaluation/review_sample.md"
with open(output_path, "w") as f:
    f.write("# Evaluation Sample - Manual Review\n\n")
    f.write("For each record below, review the AI-generated Summary and Topics against the source text, "
            "then fill in the REVIEWER SECTION. Mark Correct/Incorrect and note the correct value if incorrect.\n\n")
    f.write("---\n\n")

    for i, pub in enumerate(sample, 1):
        f.write(f"## Record {i} (ID: {pub.id})\n\n")
        f.write(f"**Institution:** {pub.institution}\n\n")
        f.write(f"**Title:** {pub.title}\n\n")
        f.write(f"**Source:** {pub.source_url}\n\n")
        f.write(f"**Original content (excerpt):**\n{pub.body_text[:400]}\n\n")
        f.write(f"**AI-Generated Summary:**\n{pub.summary}\n\n")
        f.write(f"**AI-Generated Topics:** {pub.topics}\n\n")
        f.write(f"**AI-Generated Relevance Note:**\n{pub.relevance_note}\n\n")
        f.write("### REVIEWER SECTION (fill in)\n")
        f.write("- Summary accurate? [ ] Yes  [ ] No - if no, what's wrong:\n")
        f.write("- Topics correct? [ ] Yes  [ ] No - if no, correct topics:\n")
        f.write("- Relevance note reasonable? [ ] Yes  [ ] No - notes:\n\n")
        f.write("---\n\n")

print(f"Written to {output_path}")
