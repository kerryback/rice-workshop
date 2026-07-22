# Where to find the journal skill packs online

## Source repository

Awesome Journal Skills (AJS)
- GitHub: https://github.com/hanlulong/Awesome-Journal-Skills
- License: MIT
- Maintained by CoPaper.AI (Stanford REAP) / StatsPAI; published under Lu Han's account (https://github.com/hanlulong)

The repo advertises ~4,150 Agent Skills across 299 packs, covering 522 journals and 155
CS/AI conference venues. It is large (~200 MB, ~11,000 files) because every journal is a
full plugin.

## How it is organized

- One directory per journal.
- `<Journal>/` (bare name) is just a README stub / landing page.
- `<Journal>-Skills/` holds the actual plugin: a `skills/` folder plus
  `resources/` (journal profile, official-source map, worked examples, exemplars),
  a `.claude-plugin/` manifest, and a LICENSE.

Each finance pack ships 12 sub-skills, e.g. for the Journal of Finance:
jf-topic-selection, jf-literature-positioning, jf-empirical-design, jf-identification,
jf-robustness, jf-tables-figures, jf-internet-appendix, jf-writing-style,
jf-referee-strategy, jf-submission, jf-rebuttal, and a jf-workflow router.

The content is journal-specific and current (e.g. the JF pack encodes the 60-page limit,
the bundled Internet Appendix, the AFA portal fee tiers, and the Data-and-Code-Sharing policy).

## Business-school disciplines covered (selected)

- Finance: Journal of Finance, Journal of Financial Economics, Review of Financial Studies,
  Review of Finance, Journal of Financial and Quantitative Analysis, Journal of Corporate Finance,
  Journal of Banking and Finance, Financial Management, and more.
- Accounting: The Accounting Review, Journal of Accounting Research,
  Journal of Accounting and Economics, Review of Accounting Studies, Contemporary Accounting Research.
- Marketing: Journal of Marketing, Journal of Marketing Research, Marketing Science,
  Journal of Consumer Research, and others.
- Operations: Operations Research, M&SOM, POM, Journal of Operations Management.
- Strategy / Management / OB: Strategic Management Journal, Academy of Management Journal/Review/Annals,
  Administrative Science Quarterly, Organization Science.
- Entrepreneurship: Journal of Business Venturing, Entrepreneurship Theory and Practice.
- Information Systems: MIS Quarterly, Information Systems Research, JMIS, JAIS.

## How to get a specific pack

Option A — sparse-clone just the packs you want (avoids the full 200 MB):

    git clone --no-checkout --depth 1 https://github.com/hanlulong/Awesome-Journal-Skills
    cd Awesome-Journal-Skills
    git sparse-checkout init --cone
    git sparse-checkout set Journal-of-Finance-Skills Journal-of-Financial-Economics-Skills Review-of-Financial-Studies-Skills
    git checkout

Option B — clone everything, then copy out the `<Journal>-Skills` folders you want.

To use a pack, copy its `skills/<name>` folders into `~/.claude/skills/` (or the project's
`.claude/skills/`), or install the pack via its `.claude-plugin` manifest.

## Local copies

The JF, JFE, and RFS packs are copied into this research repo at:
- ~/repos/research/Journal-of-Finance-Skills
- ~/repos/research/Journal-of-Financial-Economics-Skills
- ~/repos/research/Review-of-Financial-Studies-Skills

A full clone of the source repo (and Lu Han's other tools) is under ~/repos/research/luhan/.
