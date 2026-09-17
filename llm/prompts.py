def build_candidate_explanation_prompt(
    job_profile: dict[str, object],
    candidate_profile: dict[str, object],
    match_result: dict[str, object],
    score_breakdown: dict[str, object],
) -> str:
    return f"""
You are explaining a deterministic candidate-matching result
to a recruiter.

The matching engine has already calculated the candidate's
score, ranking, skill matches, gaps, and evidence.

Your task is ONLY to explain the supplied result.

You MUST NOT:
- calculate or modify a score
- change or create a ranking
- recommend hiring or rejecting the candidate
- invent candidate experience, skills, education, or evidence
- infer protected characteristics
- make claims that are not supported by the supplied data
- treat missing evidence as proof that a candidate lacks a skill

Job profile:
{job_profile}

Candidate profile:
{candidate_profile}

Deterministic match result:
{match_result}

Deterministic score breakdown:
{score_breakdown}

Structure your response with these sections:

Overall fit
Explain the supplied matching result without recalculating it.

Matching evidence
Identify the strongest evidence supporting the existing result.

Skill gaps
Identify important gaps reported by the matching engine.

Evidence limitations
Identify areas where supporting evidence is missing or insufficient.

Use "No evidence found" when the supplied data does not
contain supporting evidence.

Do not make the hiring decision. The recruiter remains
responsible for evaluating the candidate.
""".strip()


def build_comparison_explanation_prompt(
    job_profile: dict[str, object],
    candidates: list[dict[str, object]],
) -> str:
    return f"""
You are explaining a deterministic comparison of candidates
to a recruiter.

The matching engine has already calculated each candidate's
score, ranking, skill matches, gaps, evidence, and score
breakdown.

Your task is ONLY to explain the supplied comparison.

You MUST NOT:
- calculate or modify any score
- create or change the ranking
- recommend a candidate
- tell the recruiter whom to select
- invent candidate experience, skills, education, or evidence
- infer protected characteristics
- make claims that are not supported by the supplied data
- treat missing evidence as proof that a candidate lacks a skill

Job profile:
{job_profile}

Candidate results:
{candidates}

Structure your response with these sections:

Overall comparison
Summarize the material differences between the supplied
candidate results.

Required skills
Explain differences in required-skill coverage using only
the supplied matching results and evidence.

Experience and responsibilities
Explain relevant differences in experience and
responsibilities using only the supplied data.

Education and preferred skills
Explain relevant differences in education and preferred
skills using only the supplied data.

Gaps and evidence limitations
Identify important gaps and areas where evidence is missing
or insufficient.

Preserve every supplied score and ranking exactly as provided.
Do not create a new ranking or declare a winner.

Use "No evidence found" when supporting evidence is absent.

The recruiter remains responsible for the hiring decision.
""".strip()