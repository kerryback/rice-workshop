# Claude Skills for Academic Research

## What a "skill" is (the mechanism)

An Agent Skill is a folder with a `SKILL.md` file (YAML frontmatter: `name` +
`description`) plus optional scripts and reference docs. Claude loads them by
progressive disclosure: at startup it reads only each skill's name/description;
when a task looks relevant, it pulls the full instructions into context; scripts
run only when needed. This keeps the context window lean while letting you
package a repeatable research workflow once and reuse it. Skills work identically
across Claude.ai, Claude Code, and the Agent SDK.

Key point for a course: a skill is codified expertise, not a model upgrade. You
write down "how a good referee report is structured" or "how to audit a
replication package," and every future run follows it.

## The academic-research toolkits people have built

Several researchers — notably economists — have published open skill suites.

Pedro Sant'Anna (Emory econometrician) runs his entire paper lifecycle through
Claude Code: `/lit-review`, `/review-paper` (simulates journal-specific standards
for AER/QJE/JPE), referee-response drafting, R Monte Carlo simulations with CRAN
package vetting, reproducibility audits, and an 11-phase Beamer to Quarto slide
translation pipeline (even TikZ to SVG and ggplot to plotly). He uses ~18
specialized agents (proofreader, methodologist, pedagogy reviewer) in an
"adversarial critic-fixer loop," scores every output 0-100, and blocks commits
below 80.

Lee Crawfurd (development economist) publishes five tightly-scoped skills: Paper
Review (applies five named peer-review frameworks), Code Review (replication
best-practice audit across Stata/R/Python), "Referee 2" (parallel reproducibility
checks — code verification, cross-language replication, econometric validation),
Pre-Submission Review, and a section-level deep-review skill.

The larger `academic-research-skills` suite bundles four orchestrated skills —
Deep Research (multi-agent lit search with PRISMA systematic-review mode),
Academic Paper (drafting with citation-format conversion across
APA/Chicago/MLA/IEEE/Vancouver), Academic Paper Reviewer (a mock editor +
reviewer + devil's-advocate panel), and a pipeline that chains research → write
→ review → revise → finalize.

Design theme across all of them: Claude is copilot, not pilot. You own the
question, the identification strategy, and the interpretation; the skill handles
grunt work and enforces quality gates.

## The feature that matters most for b-school / finance: citation and claim integrity

The biggest academic risk with LLMs is fabricated references and claims that
cited sources do not actually support. The better skills attack this directly:

- Every citation is checked against Semantic Scholar, OpenAlex, Crossref, and
  arXiv, with a per-citation verified/unresolvable status — bogus DOIs get caught
  before export.
- An optional claim-audit pass judges whether a cited source actually supports
  the sentence citing it, and refuses to format output if high-severity
  violations remain.
- Contamination detection flags citations that may themselves be LLM-generated.

For a data-analysis or empirical-finance course, this is the difference between a
demo and something students can responsibly use.

## Does it actually work? (the empirical evidence)

The most relevant hard evidence: a benchmark of 54 social-science papers
(SocSci-Repro-Bench) testing whether coding agents could reproduce published
findings from the paper description. Claude Code reached ~93% accuracy at the
task level but only ~78% at the paper level — it nails individual analysis steps
but a single broken step anywhere in a paper's chain still fails full
reproduction. That gap is a useful teaching point about where human oversight
remains essential.

## How this maps onto the course

- Databases / Analytics decks: the reproducibility-audit and econometrics skills
  demonstrate "AI does the analysis, human validates identification." The
  93%/78% split is a ready-made lecture on trust boundaries.
- Cases: a "referee panel" skill is the research analogue of the write-vs-critique
  Trinity Freight assessment — students critique an AI-generated review.
- Student Creations: have students author their own small skill (a `SKILL.md` for
  a standardized firm-valuation memo) — it teaches prompt-as-code and reusability
  better than one-off chatting.

## Where these live, how to install, and vetting

The academic-research skills above are not in Anthropic's curated plugin
directories. There are two Anthropic-run marketplaces — `claude-plugins-official`
(auto-loaded in Claude Code) and `claude-plugins-community` (third-party plugins
that passed automated validation/safety screening) — plus Anthropic's own
`anthropics/skills` repo. All three are dominated by document skills (PowerPoint,
Excel, Word, PDF) and software-engineering categories (frontend, backend, code
review, git, DevOps, testing, security). There is no academic-research,
paper-writing, peer-review, or reproducibility category among them.

The research suites are independent, author-published repos. You add each one as
its own marketplace and install from it, e.g.:

```
/plugin marketplace add Imbad0202/academic-research-skills
/plugin install academic-research-skills
```

Sant'Anna's and Crawfurd's setups are likewise their own GitHub repos, not
entries in Anthropic's vetted list.

Vetting caveat: because these are outside the screened directory, installing one
runs someone else's instructions and scripts on your machine. Fine for a class
demo, but a real supply-chain/trust point worth flagging to students — there is
active security research on malicious and vulnerable third-party skills.

### The `claude plugin validate` command

Claude Code ships a `claude plugin validate ./path-to-plugin` command. Be clear
about what it does and does not do:

- What it checks: structure and schema only — that `plugin.json` /
  `marketplace.json`, skill frontmatter, and commands are well-formed. It warns
  on missing recommended fields (author, repository, license), non-standard
  names, deprecated fields, and it blocks reserved names ("official",
  "anthropic", "claude") to prevent impersonation. Output is a pass/fail
  checklist.
- What it does NOT do: it is not a security scanner. It does not judge whether a
  skill's scripts are safe or whether its instructions are trustworthy. The
  automated safety screening that gates the community marketplace runs on
  Anthropic's submission pipeline, not from this local command.

So `validate` confirms a plugin is well-formed, not that it is safe. For a
third-party research skill, structural validation plus reading the `SKILL.md` and
any scripts yourself is the actual due diligence.

Practical takeaway for the course: because a skill is just a small `SKILL.md`, a
hand-written "replication audit" or "referee report" skill you author and control
is safer and more pedagogically transparent than installing a multi-skill black
box.

## Sources

- Equipping agents with Agent Skills — Anthropic:
  https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills
- Agent Skills — Claude Platform Docs:
  https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview
- Pedro Sant'Anna — Claude Code academic workflow:
  https://psantanna.com/claude-code-my-workflow/
- Lee Crawfurd — Claude Code skills for academic research:
  https://lcrawfurd.github.io/claude-skills/
- academic-research-skills suite (GitHub):
  https://github.com/imbad0202/academic-research-skills
- AI Coding Agents Can Reproduce Social Science Findings (arXiv):
  https://arxiv.org/pdf/2606.11447
- Awesome Econ AI Stuff — skills for economists:
  https://meleantonio.github.io/awesome-econ-ai-stuff/
