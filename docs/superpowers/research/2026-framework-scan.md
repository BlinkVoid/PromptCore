# Framework Research Scan & Shortlist (2023–2026)

Branch: `improve-selection-accuracy` · Date: 2026-08-24 · Status: research only, no code changes

## 1. Methodology

Sources searched: arXiv abstract pages fetched directly (authoritative IDs verified, not guessed),
web search across Microsoft Research / Google DeepMind publication pages, ACL Anthology,
OpenReview (ICLR/ICML proceedings), Papers With Code, GitHub repos of the papers, and
Semantic Scholar citation counts surfaced in search snippets.

Inclusion criteria:

1. **Real, verifiable paper** — authors, year, venue/arXiv id confirmed via primary source
   (arXiv abs page or publisher proceedings). Anything that could not be sourced was rejected.
2. **Prompting/reasoning technique** — expressible as a meta-prompt template PromptCore can emit;
   not a fine-tuning method, training pipeline, or multi-model system orchestrator.
3. **Published ~2023–2026** and NOT already in the catalog's 40-framework README table
   (Step Back, Contrastive CoT, Skeleton of Thought, Program of Thoughts, etc. excluded up front).
4. **Adoption evidence** — peer-review acceptance at a major venue and/or citation count /
   independent replication.
5. **Category fit** — maps onto PromptCore categories: code / math / logic / creative / data /
   research / planning / general.

Corrections found during verification: Chain-of-Abstraction is **Gao et al.** (FAIR/EPFL,
arXiv:2401.17464), commonly misattributed to Hao et al.; "Chain of Code" is arXiv:**2312.04474**
(a web snippet circulating arXiv:2405.14859 for it points to an unrelated physics paper).

## 2. Ranked Shortlist

| # | Name | Citation | Mechanism (one line) | Best for | Complexity | Distinct keywords | Adoption evidence |
|---|------|----------|----------------------|----------|-----------|-------------------|-------------------|
| 1 | Self-Discover | Zhou et al. 2024, arXiv:2402.03620 (NeurIPS 2024; USC + Google DeepMind) | LLM SELECTs/ADAPTs/IMPLEMENTs atomic reasoning modules into an explicit task-specific reasoning structure (JSON key-value plan) before solving | General, Logic, Planning, Research | 7 | structure composition, meta-reasoning, module selection, JSON plan | NeurIPS 2024; up to +32% over CoT on BBH/T4D/MATH; beats CoT-Self-Consistency with 10–40x less compute; structures transfer GPT-4→Llama2 |
| 2 | Chain of Draft (CoD) | Xu, Xie, Zhao, He 2025 (Zoom), arXiv:2502.18600 | Each reasoning step limited to ≤5 words — concise dense intermediate drafts instead of verbose CoT | Math, Logic, Code, General, Creative | 3 | token efficiency, latency reduction, terse steps | Widely replicated/discussed post-Feb-2025; parity accuracy at ~7.6% of CoT tokens on GSM8K/date/sports tasks; open-source repo |
| 3 | CRITIC | Gou et al., ICLR 2024, arXiv:2305.11738 (Tsinghua + MSRA) | Verify-then-correct loop: LLM critiques its own draft using external tools (search, code interpreter), then revises iteratively | Research, Data, Code, General | 6 | tool-interactive critique, external feedback, iterative correction | ICLR 2024; +7.7 F1 QA, +7% math, −79% toxicity vs baselines; beats ReAct on QA; standard baseline in self-correction literature |
| 4 | Chain of Code (CoC) | Li et al., ICML 2024 Oral, arXiv:2312.04474 (Stanford + Google DeepMind) | Write code for sub-tasks; interpreter runs executable parts while the LLM "emulates" undefined semantic functions ("LMulator") | Code, Math, Data, Logic | 6 | code emulation, LMulator, pseudocode fallback, mixed semantic/numeric | ICML 2024 oral; 84% BBH (+12% over CoT); strong Stanford/DeepMind authorship adoption |
| 5 | Medprompt | Nori et al. 2023, arXiv:2311.16452 (Microsoft) | Compose kNN-selected few-shot exemplars + choice-shuffle ensembling + generative CoT for multiple-choice domains | Research, Data, General | 7 | kNN exemplar selection, option-shuffle ensemble, test-time composition | SOTA on all 9 MultiMedQA datasets (>90% MedQA); generalized to law/accounting/philosophy MMLU subsets; heavily cited & re-implemented (DSPy etc.) |
| 6 | RE2 (Re-Reading) | Xu et al., EMNLP 2024, arXiv:2309.06275 | Repeat the question twice in the input so the second pass sees "later" tokens first — pseudo-bidirectional encoding for decoder-only LLMs | Math, Logic, General, Research | 2 | input-phase enhancement, question repetition, orthogonal plug-in | EMNLP 2024 main; consistent gains across 14 datasets / 112 experiments; composable with any output-phase technique incl. our existing catalog |
| 7 | PlanSearch | Wang et al., ICLR 2025, arXiv:2409.03733 (Scale AI) | Generate diverse observations about a problem, combine them into candidate natural-language plans, then implement each — search in idea space, not code space | Code, Creative, Planning | 8 | observation combination, idea-space search, output diversity | ICLR 2025; LiveCodeBench pass@200 77.0% vs 60.6% repeated sampling (Claude 3.5 Sonnet); open-source scaleapi/plansearch |
| 8 | Chain-of-Abstraction (CoA) | Gao et al. 2024 (FAIR/EPFL), arXiv:2401.17464 | Decode reasoning chains with abstract placeholders (y1, y2…), then infill via tools in one batch — decouples reasoning from knowledge lookup, parallelizable | Math, Data, Research | 5 | placeholder abstraction, deferred tool reification, OOD robustness | ACL/ARR 2024; +~6% avg accuracy over tool-augmented CoT baselines, 1.4x faster inference. Caveat: original result uses fine-tuning; adopt as zero-shot promptable adaptation |
| 9 | Deliberate-then-Generate (DTG) | Bei Li et al. 2023, arXiv:2305.19835 (AAAI 2024; NEU/Microsoft) | Force error-detection deliberation on a deliberately flawed (or empty) candidate before generating the final output | Creative, General, Research | 4 | error detection first, candidate critique, generation quality | AAAI 2024; SoTA on multiple of 20+ text-generation datasets (translation, summarization, dialogue); single-step inference cost |

Coverage check vs. catalog gaps: #2/#6 are low-complexity cheap wins the selector currently lacks;
#3/#9 cover verify-before-answer for creative/general (only CoVe exists today); #1/#7 extend
planning/code beyond ToT/GoT/RAP; #4/#5 add domain-grounded selection strategies.

## 3. Rejected (with reasons)

- **Take a Deep Breath** — phrase originates from OPRO (Yang et al. 2023, arXiv:2309.03409, ICLR
  2024), where it was *discovered* as an instruction, not proposed as a framework. Mechanistically
  a one-sentence variant of zero-shot CoT; gains model-dependent. Redundant with catalog CoT.
- **Archon** (Saad-Falcon et al., arXiv:2409.15254, ICML 2025) — verified real and impressive
  (+15.1% over frontier models), but it is an *architecture-search system* stacking ensembling/
  fusion/ranking/verification layers across multiple LLMs — not a single promptable reasoning
  template. Out of scope for PromptCore's per-task framework model.
- **CodeIt** (Butt et al. 2023/ICLR 2024) — self-improvement training loop (hindsight relabeling +
  replay) for ARC; requires training, not prompting.
- **DynaThink** (Pan et al., arXiv:2407.01009) — real paper but essentially no citations/adoption
  at scan time; fails inclusion criterion 5.
- **Self-Probing, sparse/adaptive-CoT variants, bottom-up program-guided reasoning** — could not be
  sourced to a specific authoritative paper in this pass; per instructions, unverified = rejected.
- **Skeleton-of-Anything variants, Step-Back, Contrastive CoT** — already covered by catalog
  entries (Skeleton of Thought, Step Back, Contrastive CoT).
- **Hao et al. attribution of Chain-of-Abstraction** — misattribution; correct cite is Gao et al.,
  arXiv:2401.17464 (kept the technique, fixed the citation).

## 4. Suggested Module Placement

Existing registry layout: `src/promptcore/domain/frameworks/{zero_shot,thought_generation,
decomposition,self_criticism,ensembling,advanced}.py`.

Primary recommendation — reuse thematic submodules (keeps selector import graph unchanged):

| Candidate | Module | Rationale |
|-----------|--------|-----------|
| Chain of Draft, Chain-of-Abstraction, Chain of Code | `frameworks/thought_generation.py` | chain-style generation families (alongside CoT/PoT/Faithful CoT) |
| RE2 | `frameworks/zero_shot.py` | input-phase wrapper, zero extra calls |
| CRITIC, DTG | `frameworks/self_criticism.py` | critique/refine loops (alongside Self-Refine/CoVe) |
| Self-Discover, PlanSearch | `frameworks/advanced.py` | structure/search orchestration (alongside ToT/GoT/Meta-CoT) |
| Medprompt | `frameworks/ensembling.py` | exemplar-selection + shuffle-ensemble composition |

Alternative: a new `frameworks/modern.py` holding all nine as a coherent "post-2023 wave" batch —
useful for A/B benchmarking old-vs-new selector accuracy (matches this branch's eval harness), at
the cost of splitting chain-style frameworks across two files. If the improvement loop needs a
clean treatment/control split, prefer `modern.py`; otherwise prefer thematic placement.
