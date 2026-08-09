# binomial-tutor

A Claude skill that tutors a student through binomial option pricing:
replicating portfolios, risk-neutral probabilities, multi-period trees, and
American options. Claude asks the student to work the problems and gives
feedback on the answers rather than presenting solutions.

Built as the worked example of a tutoring skill for session 4 of the Rice
Business AI course.

## Installing it

Copy the whole folder into your personal skills directory:

```
cp -r binomial-tutor ~/.claude/skills/
```

To make it available in one project only, copy it into `.claude/skills/` inside
that project instead.

## Using it

In Claude Code, type

```
/binomial-tutor
```

or just say what you want — "teach me the binomial model", "I don't understand
risk-neutral probabilities", "quiz me on American options", "check my work on
this tree". Claude will ask what you want to cover and where you are starting
from, and go from there.

The whole arc takes 30 to 45 minutes. You can stop between sections and pick it
up later.

## What's inside

```
binomial-tutor/
├── SKILL.md                    tutoring protocol Claude follows
├── references/
│   ├── 01-replication.md       one period: replication and no arbitrage
│   ├── 02-risk-neutral.md      where q comes from and what it means
│   ├── 03-multiperiod.md       two periods, dynamic hedging, n periods
│   ├── 04-american.md          early exercise
│   └── exercises.md            problem bank with answers
└── scripts/
    └── binomial.py             prices trees, generates exercises, plots
```

## The script on its own

`scripts/binomial.py` is usable without Claude. It prices European and American
calls and puts on a recombining tree and prints the tree, the risk-neutral
probability, and the replicating portfolio at every node.

```
python scripts/binomial.py --S 100 --K 100 --r 0.02 --u 1.1 --d 0.9 \
    --n 2 --kind "American put"
```

`u` and `d` are gross returns (1.1 means +10%), `r` is per period, and `--d`
defaults to `1/u`. Add `--plot trees.html` for interactive figures of the stock
and option trees, or `--blank 1,0` to hide a node and its ancestors so the tree
becomes a problem to solve.

Requires numpy, and plotly only if you use `--plot`.

The pricing functions and the tree figure come from the binomial trees notebook
at [learn-investments.rice-business.org](https://learn-investments.rice-business.org)
by Kerry Back and Kevin Crotty, extended here to allow a down factor other than
`1/u` and to report the replicating portfolio and early-exercise nodes.
