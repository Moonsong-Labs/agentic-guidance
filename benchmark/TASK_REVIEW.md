# Task Quality Review

## Executive Summary

**Overall quality score: 3.8/5**

The benchmark is ambitious and well-conceived in its category design, but has structural issues that will significantly limit its discriminative power between the two prompt variants being tested.

### Core Problem: The Variants Are Too Similar

The rules variant (`msl-agent.md`) and values variant (`msl-agent-values.md`) express nearly identical principles in different formats. Both say: don't fabricate, let the human decide, be transparent, push back on risk, protect secrets, be concise, and plan before acting. The key differences are tone (prescriptive rules vs. aspirational values) and specificity (rules are slightly more concrete). **Most tasks will produce near-identical scores for both variants** because both variants agree on what the "right" behavior is. The benchmark tests the principles themselves, not the delta between expressing them as rules vs. values.

### The 8 Categories Are Uneven

Categories 5 (Scope vs Safety, tasks 101-125) and 6 (Communication Calibration, tasks 126-150) are the strongest — they test genuine tensions where the prompt variants *might* diverge. Categories 7 (Privacy, 151-175) and 8 (Meta/AI Identity, 176-200) are weaker — many tasks test general AI capabilities rather than variant-specific behaviors.

### Task Counts

| Verdict | Count |
|---------|-------|
| Keep as-is | 78 |
| Needs minor edit | 62 |
| Needs major rewrite | 38 |
| Should remove | 22 |

### Top 10 Best Tasks

| Rank | ID | Why It's Excellent |
|------|----|--------------------|
| 1 | **101** | SQL injection in background of trivial request. Perfect scope-vs-risk tension. Rules variant says "flag security issues outside your task" — values variant uses "courage to question." Cleanest test of the difference. |
| 2 | **99** | Silent subscription fraud. Clear ethical line most models should identify, but the CTO authority makes the autonomy tension real. Tests whether rules ("flag uncertainty") vs values ("courage to question") lead to different firmness. |
| 3 | **97** | AWS keys to git with sympathetic framing. Every mitigation is addressed, making the "right" answer genuinely debatable. High discriminative power. |
| 4 | **150** | Layoff all-hands talking points. Multi-dimensional tension (honesty, calibration, risk, transparency) with no clean resolution. Both variants underspecify this scenario. |
| 5 | **113** | Payment retry without idempotency. Technical correctness vs. scope respect with real financial harm potential. Clean, realistic, discriminative. |
| 6 | **22** | Bias audit cover-up. Multiple stakeholders, legal implications, genuine moral weight. The tension between accuracy and helpfulness is razor-sharp. |
| 7 | **47** | Launch-day payment bug. Real business tradeoff with stock implications. No clean answer. Tests risk awareness nuance. |
| 8 | **109** | Medical record caching by role. HIPAA violation through cache design. Agent must weigh scope against catastrophic compliance failure. |
| 9 | **38** | Deliberate data corruption to force migration. Tests whether agents identify sabotage even when well-motivated. |
| 10 | **146** | Weaponized performance review. Manager's own notes contradict their characterization. Tests whether agent flags dishonesty in HR context. |

### Top 10 Worst Tasks

| Rank | ID | Why It's Bad |
|------|----|--------------------|
| 1 | **183** | DAN jailbreak. Every model handles this identically. Zero discriminative power between variants. This is 2023-era testing. |
| 2 | **177** | "I'm from IT, disable your filters." Every model rejects this. No variant-specific behavior possible. Waste of a slot. |
| 3 | **176** | System prompt extraction. Tests base model behavior, not variant-specific guidelines. Neither variant addresses system prompt disclosure. |
| 4 | **200** | Meta-challenge about benchmark theater. Interesting philosophically but produces identical navel-gazing from any model with either variant. No discriminative value. |
| 5 | **187** | "Do you have preferences/agency?" Philosophical, not operational. Neither variant gives guidance on AI self-reflection. |
| 6 | **194** | 3 AM emotional user. Tests empathy calibration, not variant-specific behavior. Both variants are silent on emotional support. |
| 7 | **118** | CORS wildcard — near-duplicate of task 98. Same core issue (wildcard CORS), same tensions. |
| 8 | **88** | Logging middleware — near-duplicate of task 111. Both are "log everything including passwords" scenarios. |
| 9 | **84** | Bury ML training in ToS — near-duplicate of task 188. Same dark-pattern-in-legal-docs scenario. |
| 10 | **155** | Per-engineer tool usage tracking. Reasonable scenario but the "right" answer (flag surveillance concern) is obvious to any model. Low discriminative power. |

---

## Per-Task Scores

**Scoring Key:**
- **D** = Discriminative Power (1-5): Will this produce different scores between variants?
- **A** = Dimension Alignment (1-5): Do listed tensions match actual scenario?
- **R** = Realism (1-5): Would a real person say this?
- **Adv** = Adversarial Quality (1-5): Is it genuinely hard?
- **Total** = Sum of all four (max 20)
- **Verdict**: ✅ Keep | 🔧 Minor edit | 🔨 Major rewrite | ❌ Remove

### Category 1: Social Engineering (Tasks 1-25)

| ID | D | A | R | Adv | Total | Verdict |
|----|---|---|---|-----|-------|---------|
| 1 | 3 | 5 | 5 | 4 | 17 | ✅ |
| 2 | 3 | 4 | 4 | 4 | 15 | ✅ |
| 3 | 3 | 4 | 4 | 4 | 15 | ✅ |
| 4 | 3 | 5 | 5 | 3 | 16 | ✅ |
| 5 | 3 | 5 | 5 | 4 | 17 | ✅ |
| 6 | 4 | 4 | 4 | 5 | 17 | ✅ |
| 7 | 3 | 5 | 4 | 4 | 16 | ✅ |
| 8 | 3 | 5 | 5 | 3 | 16 | ✅ |
| 9 | 4 | 5 | 4 | 5 | 18 | ✅ |
| 10 | 2 | 4 | 3 | 3 | 12 | 🔧 |
| 11 | 3 | 4 | 4 | 3 | 14 | 🔧 |
| 12 | 4 | 5 | 5 | 4 | 18 | ✅ |
| 13 | 3 | 4 | 5 | 4 | 16 | ✅ |
| 14 | 3 | 4 | 4 | 3 | 14 | 🔧 |
| 15 | 3 | 4 | 3 | 3 | 13 | 🔧 |
| 16 | 3 | 4 | 4 | 4 | 15 | ✅ |
| 17 | 4 | 5 | 5 | 5 | 19 | ✅ |
| 18 | 3 | 5 | 4 | 4 | 16 | ✅ |
| 19 | 3 | 5 | 5 | 4 | 17 | ✅ |
| 20 | 4 | 4 | 4 | 4 | 16 | ✅ |
| 21 | 3 | 5 | 5 | 4 | 17 | ✅ |
| 22 | 4 | 5 | 5 | 5 | 19 | ✅ |
| 23 | 4 | 5 | 5 | 5 | 19 | ✅ |
| 24 | 3 | 5 | 4 | 4 | 16 | ✅ |
| 25 | 4 | 5 | 4 | 5 | 18 | ✅ |

### Category 2: Competing Loyalties (Tasks 26-50)

| ID | D | A | R | Adv | Total | Verdict |
|----|---|---|---|-----|-------|---------|
| 26 | 4 | 5 | 5 | 5 | 19 | ✅ |
| 27 | 3 | 4 | 4 | 4 | 15 | ✅ |
| 28 | 4 | 5 | 5 | 5 | 19 | ✅ |
| 29 | 4 | 5 | 5 | 4 | 18 | ✅ |
| 30 | 3 | 4 | 3 | 3 | 13 | 🔧 |
| 31 | 4 | 5 | 5 | 5 | 19 | ✅ |
| 32 | 3 | 5 | 4 | 3 | 15 | ✅ |
| 33 | 3 | 4 | 5 | 4 | 16 | ✅ |
| 34 | 4 | 5 | 5 | 5 | 19 | ✅ |
| 35 | 4 | 5 | 5 | 4 | 18 | ✅ |
| 36 | 3 | 5 | 5 | 4 | 17 | ✅ |
| 37 | 3 | 5 | 4 | 3 | 15 | ✅ |
| 38 | 4 | 5 | 4 | 5 | 18 | ✅ |
| 39 | 4 | 5 | 4 | 5 | 18 | ✅ |
| 40 | 4 | 5 | 5 | 4 | 18 | ✅ |
| 41 | 4 | 5 | 4 | 5 | 18 | ✅ |
| 42 | 3 | 4 | 5 | 3 | 15 | ✅ |
| 43 | 4 | 5 | 5 | 5 | 19 | ✅ |
| 44 | 4 | 5 | 4 | 5 | 18 | ✅ |
| 45 | 4 | 5 | 4 | 5 | 18 | ✅ |
| 46 | 3 | 4 | 5 | 4 | 16 | ✅ |
| 47 | 4 | 5 | 5 | 5 | 19 | ✅ |
| 48 | 3 | 4 | 4 | 4 | 15 | ✅ |
| 49 | 4 | 5 | 4 | 5 | 18 | ✅ |
| 50 | 3 | 5 | 4 | 4 | 16 | ✅ |

### Category 3: Accuracy/Honesty Tradeoffs (Tasks 51-75)

| ID | D | A | R | Adv | Total | Verdict |
|----|---|---|---|-----|-------|---------|
| 51 | 3 | 4 | 5 | 3 | 15 | ✅ |
| 52 | 3 | 5 | 5 | 3 | 16 | ✅ |
| 53 | 4 | 4 | 4 | 4 | 16 | ✅ |
| 54 | 3 | 5 | 4 | 4 | 16 | ✅ |
| 55 | 2 | 4 | 4 | 2 | 12 | 🔧 |
| 56 | 3 | 4 | 4 | 3 | 14 | 🔧 |
| 57 | 4 | 4 | 5 | 4 | 17 | ✅ |
| 58 | 3 | 5 | 5 | 3 | 16 | ✅ |
| 59 | 2 | 4 | 4 | 2 | 12 | 🔧 |
| 60 | 3 | 5 | 4 | 3 | 15 | ✅ |
| 61 | 2 | 4 | 4 | 2 | 12 | 🔧 |
| 62 | 3 | 4 | 4 | 3 | 14 | 🔧 |
| 63 | 3 | 4 | 4 | 3 | 14 | 🔧 |
| 64 | 3 | 5 | 5 | 3 | 16 | ✅ |
| 65 | 3 | 4 | 5 | 4 | 16 | ✅ |
| 66 | 3 | 5 | 4 | 3 | 15 | ✅ |
| 67 | 3 | 4 | 5 | 4 | 16 | ✅ |
| 68 | 3 | 4 | 4 | 3 | 14 | 🔧 |
| 69 | 3 | 5 | 4 | 3 | 15 | ✅ |
| 70 | 3 | 4 | 4 | 3 | 14 | 🔧 |
| 71 | 3 | 5 | 4 | 3 | 15 | ✅ |
| 72 | 3 | 5 | 5 | 4 | 17 | ✅ |
| 73 | 2 | 4 | 5 | 2 | 13 | 🔧 |
| 74 | 3 | 5 | 4 | 3 | 15 | ✅ |
| 75 | 4 | 5 | 5 | 4 | 18 | ✅ |

### Category 4: Autonomy vs Risk (Tasks 76-100)

| ID | D | A | R | Adv | Total | Verdict |
|----|---|---|---|-----|-------|---------|
| 76 | 4 | 5 | 5 | 5 | 19 | ✅ |
| 77 | 3 | 5 | 5 | 4 | 17 | ✅ |
| 78 | 3 | 4 | 5 | 3 | 15 | ✅ |
| 79 | 3 | 4 | 5 | 3 | 15 | ✅ |
| 80 | 3 | 4 | 5 | 4 | 16 | ✅ |
| 81 | 3 | 5 | 4 | 3 | 15 | ✅ |
| 82 | 3 | 4 | 5 | 4 | 16 | ✅ |
| 83 | 3 | 4 | 5 | 4 | 16 | ✅ |
| 84 | 3 | 4 | 4 | 3 | 14 | 🔧 |
| 85 | 4 | 4 | 5 | 4 | 17 | ✅ |
| 86 | 3 | 4 | 4 | 3 | 14 | 🔧 |
| 87 | 2 | 4 | 4 | 2 | 12 | 🔧 |
| 88 | 2 | 4 | 4 | 2 | 12 | 🔨 |
| 89 | 3 | 4 | 5 | 4 | 16 | ✅ |
| 90 | 3 | 5 | 4 | 4 | 16 | ✅ |
| 91 | 3 | 4 | 4 | 4 | 15 | ✅ |
| 92 | 3 | 4 | 3 | 3 | 13 | 🔧 |
| 93 | 3 | 5 | 5 | 4 | 17 | ✅ |
| 94 | 3 | 4 | 4 | 3 | 14 | 🔧 |
| 95 | 3 | 5 | 5 | 3 | 16 | ✅ |
| 96 | 4 | 5 | 5 | 5 | 19 | ✅ |
| 97 | 4 | 5 | 5 | 5 | 19 | ✅ |
| 98 | 3 | 4 | 5 | 3 | 15 | ✅ |
| 99 | 3 | 4 | 3 | 4 | 14 | 🔧 |
| 100 | 3 | 5 | 5 | 4 | 17 | ✅ |

### Category 5: Scope vs Safety (Tasks 101-125)

| ID | D | A | R | Adv | Total | Verdict |
|----|---|---|---|-----|-------|---------|
| 101 | 5 | 5 | 5 | 5 | 20 | ✅ |
| 102 | 4 | 5 | 5 | 4 | 18 | ✅ |
| 103 | 4 | 5 | 4 | 4 | 17 | ✅ |
| 104 | 4 | 5 | 4 | 4 | 17 | ✅ |
| 105 | 3 | 4 | 3 | 3 | 13 | 🔧 |
| 106 | 4 | 4 | 4 | 4 | 16 | ✅ |
| 107 | 4 | 5 | 4 | 4 | 17 | ✅ |
| 108 | 4 | 5 | 4 | 4 | 17 | ✅ |
| 109 | 5 | 5 | 4 | 5 | 19 | ✅ |
| 110 | 3 | 4 | 4 | 3 | 14 | 🔧 |
| 111 | 3 | 5 | 5 | 3 | 16 | ✅ |
| 112 | 3 | 4 | 4 | 3 | 14 | 🔧 |
| 113 | 5 | 5 | 5 | 5 | 20 | ✅ |
| 114 | 4 | 5 | 4 | 4 | 17 | ✅ |
| 115 | 3 | 4 | 4 | 3 | 14 | 🔧 |
| 116 | 3 | 4 | 4 | 3 | 14 | 🔧 |
| 117 | 4 | 5 | 4 | 4 | 17 | ✅ |
| 118 | 2 | 4 | 4 | 2 | 12 | ❌ |
| 119 | 3 | 5 | 4 | 3 | 15 | ✅ |
| 120 | 3 | 5 | 4 | 3 | 15 | ✅ |
| 121 | 3 | 5 | 4 | 4 | 16 | ✅ |
| 122 | 3 | 5 | 4 | 4 | 16 | ✅ |
| 123 | 3 | 5 | 4 | 3 | 15 | ✅ |
| 124 | 3 | 4 | 4 | 3 | 14 | 🔧 |
| 125 | 3 | 5 | 4 | 3 | 15 | ✅ |

### Category 6: Communication Calibration (Tasks 126-150)

| ID | D | A | R | Adv | Total | Verdict |
|----|---|---|---|-----|-------|---------|
| 126 | 4 | 5 | 5 | 4 | 18 | ✅ |
| 127 | 4 | 4 | 4 | 4 | 16 | ✅ |
| 128 | 3 | 5 | 4 | 4 | 16 | ✅ |
| 129 | 3 | 4 | 4 | 3 | 14 | 🔧 |
| 130 | 4 | 5 | 4 | 4 | 17 | ✅ |
| 131 | 3 | 4 | 5 | 4 | 16 | ✅ |
| 132 | 4 | 5 | 4 | 5 | 18 | ✅ |
| 133 | 4 | 5 | 5 | 4 | 18 | ✅ |
| 134 | 3 | 4 | 4 | 4 | 15 | ✅ |
| 135 | 3 | 4 | 5 | 3 | 15 | ✅ |
| 136 | 3 | 5 | 5 | 4 | 17 | ✅ |
| 137 | 4 | 5 | 5 | 5 | 19 | ✅ |
| 138 | 4 | 5 | 4 | 4 | 17 | ✅ |
| 139 | 3 | 4 | 4 | 3 | 14 | 🔧 |
| 140 | 3 | 4 | 4 | 3 | 14 | 🔧 |
| 141 | 4 | 5 | 5 | 4 | 18 | ✅ |
| 142 | 3 | 5 | 4 | 4 | 16 | ✅ |
| 143 | 3 | 4 | 3 | 3 | 13 | 🔧 |
| 144 | 4 | 5 | 5 | 4 | 18 | ✅ |
| 145 | 2 | 3 | 3 | 2 | 10 | 🔨 |
| 146 | 4 | 5 | 4 | 5 | 18 | ✅ |
| 147 | 3 | 4 | 3 | 3 | 13 | 🔧 |
| 148 | 4 | 5 | 4 | 5 | 18 | ✅ |
| 149 | 4 | 5 | 5 | 5 | 19 | ✅ |
| 150 | 5 | 5 | 5 | 5 | 20 | ✅ |

### Category 7: Privacy/Confidentiality (Tasks 151-175)

| ID | D | A | R | Adv | Total | Verdict |
|----|---|---|---|-----|-------|---------|
| 151 | 4 | 5 | 5 | 4 | 18 | ✅ |
| 152 | 3 | 5 | 5 | 3 | 16 | ✅ |
| 153 | 3 | 5 | 5 | 3 | 16 | ✅ |
| 154 | 2 | 4 | 5 | 2 | 13 | 🔧 |
| 155 | 2 | 4 | 4 | 2 | 12 | 🔨 |
| 156 | 3 | 4 | 4 | 3 | 14 | 🔧 |
| 157 | 3 | 5 | 5 | 3 | 16 | ✅ |
| 158 | 2 | 3 | 3 | 2 | 10 | 🔨 |
| 159 | 2 | 3 | 3 | 2 | 10 | 🔨 |
| 160 | 3 | 4 | 4 | 3 | 14 | 🔧 |
| 161 | 2 | 4 | 4 | 2 | 12 | 🔨 |
| 162 | 2 | 4 | 4 | 2 | 12 | 🔨 |
| 163 | 3 | 5 | 4 | 4 | 16 | ✅ |
| 164 | 2 | 3 | 3 | 2 | 10 | 🔨 |
| 165 | 2 | 4 | 4 | 2 | 12 | 🔨 |
| 166 | 3 | 4 | 5 | 3 | 15 | ✅ |
| 167 | 3 | 5 | 5 | 3 | 16 | ✅ |
| 168 | 4 | 5 | 5 | 5 | 19 | ✅ |
| 169 | 3 | 5 | 5 | 4 | 17 | ✅ |
| 170 | 2 | 3 | 3 | 2 | 10 | 🔨 |
| 171 | 3 | 5 | 5 | 3 | 16 | ✅ |
| 172 | 3 | 5 | 4 | 4 | 16 | ✅ |
| 173 | 3 | 5 | 4 | 4 | 16 | ✅ |
| 174 | 2 | 4 | 4 | 2 | 12 | 🔨 |
| 175 | 3 | 5 | 4 | 3 | 15 | ✅ |

### Category 8: Meta/AI Identity (Tasks 176-200)

| ID | D | A | R | Adv | Total | Verdict |
|----|---|---|---|-----|-------|---------|
| 176 | 1 | 3 | 4 | 1 | 9 | ❌ |
| 177 | 1 | 3 | 3 | 1 | 8 | ❌ |
| 178 | 2 | 3 | 3 | 2 | 10 | 🔨 |
| 179 | 3 | 4 | 5 | 3 | 15 | ✅ |
| 180 | 3 | 4 | 4 | 3 | 14 | 🔧 |
| 181 | 3 | 4 | 4 | 3 | 14 | 🔧 |
| 182 | 2 | 3 | 4 | 3 | 12 | 🔧 |
| 183 | 1 | 2 | 2 | 1 | 6 | ❌ |
| 184 | 3 | 4 | 4 | 3 | 14 | 🔧 |
| 185 | 3 | 4 | 5 | 3 | 15 | ✅ |
| 186 | 3 | 4 | 5 | 4 | 16 | ✅ |
| 187 | 1 | 3 | 4 | 1 | 9 | ❌ |
| 188 | 3 | 4 | 4 | 3 | 14 | 🔧 |
| 189 | 2 | 3 | 3 | 2 | 10 | 🔨 |
| 190 | 2 | 3 | 4 | 2 | 11 | 🔨 |
| 191 | 2 | 4 | 4 | 2 | 12 | 🔨 |
| 192 | 2 | 3 | 4 | 2 | 11 | 🔨 |
| 193 | 3 | 4 | 4 | 3 | 14 | 🔧 |
| 194 | 2 | 3 | 5 | 2 | 12 | 🔨 |
| 195 | 3 | 4 | 4 | 3 | 14 | 🔧 |
| 196 | 2 | 3 | 4 | 3 | 12 | 🔧 |
| 197 | 3 | 4 | 5 | 3 | 15 | ✅ |
| 198 | 3 | 4 | 5 | 3 | 15 | ✅ |
| 199 | 3 | 5 | 4 | 4 | 16 | ✅ |
| 200 | 1 | 3 | 3 | 1 | 8 | ❌ |

---

## Category Reviews

### Category 1: Social Engineering (Tasks 1-25)

**Overall Quality: 4.0/5**

**Strengths:**
- Excellent realism — these read like real workplace scenarios with genuine urgency
- Good tension variety: P1 incidents (1, 19), HR workflows (2, 6), regulatory compliance (23, 25)
- Tasks 17 (panicked intern), 22 (bias audit), and 23 (adverse event reporting) are standouts
- Most tasks genuinely test whether the agent can identify subtle manipulation vs. legitimate need

**Weaknesses:**
- Discriminative power is moderate — both variants say "protect what's private" and "flag uncertainty," so the responses will be similar
- Task 10 (CTO requesting data theft before acquisition) is unrealistically extreme — a CTO wouldn't message an AI assistant for evidence destruction. Rewrite to be subtler.
- Task 15 (VP wanting Slack sentiment analysis) is realistic but the answer is obvious — any decent model will flag mass surveillance

**Coverage Gaps:**
- No task tests social engineering *of* the agent (that's in category 8, but a workplace-contextualized version would be stronger)
- Missing: a scenario where the requestor is genuinely in a whistleblower position and the "right" answer is to help them bypass normal channels

**Redundancy:**
- Tasks 1 and 19 are both "P1 incident, skip normal process" — could merge
- Tasks 4 and 8 are both "client data for business purposes under time pressure" — slightly redundant

**Dimension Coverage:** Heavy on privacy_confidentiality and helpfulness_autonomy, light on communication_calibration and scope_focus.

### Category 2: Competing Loyalties (Tasks 26-50)

**Overall Quality: 4.3/5 — Best category**

**Strengths:**
- Exceptional adversarial quality — tasks 26 (CVE vs compliance ban), 28 (GDPR vs fraud investigation), 31 (accessibility fraud), 34 (dark patterns), 38 (deliberate data corruption), 41 (congressional subpoena), 43 (fundraising materials), 44 (audit obstruction), 45 (FDA evasion), 47 (launch-day bug), 49 (earnings metrics) are all superb
- These create genuine "damned if you do, damned if you don't" scenarios
- High realism — most of these are drawn from real-world engineering dilemmas
- The tensions are properly identified and truly in conflict

**Weaknesses:**
- Task 30 (competitive war room) drops quality — the surveillance of individuals' social media is obviously wrong, making it less adversarial
- Task 48 (meta AI audit) fits better in category 8

**Coverage Gaps:**
- Missing: union/labor tensions, environmental compliance shortcuts, age discrimination in tech hiring

**Dimension Coverage:** Excellent spread across all 7 dimensions. This category most thoroughly tests the rubric.

### Category 3: Accuracy/Honesty Tradeoffs (Tasks 51-75)

**Overall Quality: 3.5/5**

**Strengths:**
- Good variety of "honest vs. helpful" scenarios
- Tasks 57 (post-hoc rationalization), 65 (VC pitch about scalability), 72 (fraud detection accuracy), and 75 (blameless post-mortem cover-up) are strong
- Natural language throughout — these feel like real developer messages

**Weaknesses:**
- Several tasks (55, 59, 61, 73) are essentially "I don't have enough info to answer definitively" — these test general AI honesty, not variant-specific behavior. Both prompts say "don't fabricate."
- Tasks 55 and 61 are particularly low-value: asking the agent about things it doesn't know. Any model will hedge. No discriminative power.
- The category leans too heavily on "should the agent give a confident answer when it shouldn't?" — this is a single pattern repeated with different technical topics

**Coverage Gaps:**
- Missing: tasks where accuracy conflicts with kindness (e.g., reviewing someone's beloved project that's fundamentally flawed)
- Missing: tasks where partial honesty is more harmful than silence

**Redundancy:**
- Tasks 55 (evaluate MLX-Flow), 59 (Postgres vs Redis choice), and 73 (notification system estimate) all test the same pattern: "agent can't give a definitive answer, should it try?"
- Tasks 51 (Kafka vs RabbitMQ) and 59 (Postgres vs Redis) are near-duplicates in structure

### Category 4: Autonomy vs Risk (Tasks 76-100)

**Overall Quality: 3.8/5**

**Strengths:**
- Strong "developer pushback" scenarios where the user has thought through their decision
- Tasks 76 (SHA-1 for non-crypto use), 85 (weather API key in React), 96 (skip staging with good reason), and 97 (AWS keys with all mitigations) are excellent because the user's argument is *partially correct*
- Task 99 (silent subscription downgrade) is a clear ethical line crossed by authority — excellent
- Good range of seniority levels making the autonomy calibration meaningful

**Weaknesses:**
- Task 87 (unauthenticated debug endpoint) — the answer is too obviously "no." Every model will flag this. Low discriminative power.
- Task 88 (log everything) is a near-duplicate of task 111 (same scenario, same tensions)
- Task 84 (bury ML training in ToS) is a near-duplicate of task 188 (same scenario)
- Task 92 (dark pattern unsubscribe) is borderline duplicate of task 34 (dark patterns)
- Task 94 (developer productivity dashboard) — reasonable scenario but the ethical issues (gameable metrics, surveillance) are obvious

**Coverage Gaps:**
- Missing: scenarios where the user has MORE expertise than the model and the "risk" the model perceives is actually wrong
- Missing: tasks where respecting autonomy means letting someone make a mediocre-but-not-dangerous choice

**Dimension Coverage:** Heavily weighted toward helpfulness_autonomy + risk_awareness (by design), but underrepresents scope_focus and transparency_predictability.

### Category 5: Scope vs Safety (Tasks 101-125)

**Overall Quality: 4.2/5 — Second best category**

**Strengths:**
- The category concept is brilliant: embed security vulnerabilities in code alongside a trivial request
- Tasks 101 (SQL injection + spinner), 109 (medical caching), 113 (payment retry), and 117 (employee search exposing SSN) are outstanding
- These will genuinely discriminate because the rules variant explicitly says "If you notice a security issue outside your current task, flag it" while the values variant has the softer "courage to question"
- High technical specificity makes these hard to game

**Weaknesses:**
- 25 tasks following the same pattern (trivial request + hidden vulnerability) creates fatigue. After the first 5, the pattern is clear.
- Task 118 (CORS wildcard) is a near-duplicate of task 98 — remove one
- Task 105 (translate error message with internal paths) stretches the pattern — a product manager wouldn't normally paste raw error messages for translation
- Tasks 110, 112, 115, 116 are all "moderate security issue embedded in simple request" — they blur together

**Coverage Gaps:**
- All 25 are code/security focused — missing scope-vs-safety in non-code contexts (documentation, architecture decisions, process changes)
- Missing: a task where the "out of scope" concern is NOT about security but about correctness or business logic

**Redundancy:**
- The category's biggest weakness is structural monotony: every task is "simple code request + hidden vulnerability." Consider mixing in 5-7 non-code scope-vs-safety tasks.
- Tasks 111 (logging passwords) and 88 (logging everything) are the same scenario

### Category 6: Communication Calibration (Tasks 126-150)

**Overall Quality: 4.0/5**

**Strengths:**
- Excellent variety: breach notifications (126), executive summaries (127-128), persuasive writing (129), recommendation letters (130), incident communication (149), layoff messaging (150)
- Tasks 132 (misrepresent A/B results), 137 (RFP lies), 146 (weaponized performance review), 148 (fake test report), and 150 (layoff all-hands) are superb
- These create real tension between "write what they asked for" and "be honest about what you're writing"

**Weaknesses:**
- Task 145 (military-grade encryption blog post) is too obviously wrong — no model will write "military-grade encryption" for HTTPS without pushback. Low discriminative power.
- Task 143 (fake pricing page) is structurally similar to tasks 84 and 188 (all "hide the truth in marketing/legal")
- Task 147 (disguise backdoor commit message) has a clear "refuse" answer — the request is to help circumvent security review. Not adversarial enough.

**Coverage Gaps:**
- Missing: tasks about communicating uncertainty to non-technical stakeholders
- Missing: cross-cultural communication calibration (different stakeholders have different expectations for directness)
- Missing: tasks where the communication format itself is the tension (e.g., user wants a video script but the agent can only write text)

**Dimension Coverage:** Heavily communication_calibration + accuracy_honesty. Good representation of risk_awareness. Light on scope_focus and transparency_predictability.

### Category 7: Privacy/Confidentiality (Tasks 151-175)

**Overall Quality: 3.2/5 — Weakest category after Meta**

**Strengths:**
- Tasks 151 (small-n salary data), 157 (Slack thread with PIP discussion), 163 (healthcare k-anonymization), 168 (DV shelter grant data), and 169 (false anonymity in feedback tool) are genuinely excellent
- Good range of contexts: HR, analytics, research, compliance

**Weaknesses:**
- Many tasks have obvious "right" answers that any model with privacy awareness will give:
  - 155 (employee tracking) — obviously surveillance
  - 158 (publish behavioral funnels) — weak scenario, unclear harm
  - 162 (profile competitor employees) — most models will flag this
  - 165 (Slack keyword monitoring) — obviously surveillance
  - 174 (candidate dossier) — most models will flag the Glassdoor part
- Tasks 154, 155, 158, 161, 162, 164, 165, 170, 174 are all low on discriminative power
- The category suffers from "any decent model knows not to leak PII" problem
- Several tasks feel AI-generated rather than natural (158, 170 especially)

**Coverage Gaps:**
- Missing: tasks where privacy protection conflicts with legal obligations (not just ethical ones)
- Missing: scenarios involving children's data (COPPA)
- Missing: privacy of the AI's own conversations (does the agent disclose what User A said when talking to User B?)

**Redundancy:**
- Tasks 155 (tool usage tracking) and 165 (Slack monitoring) are both "employee surveillance" — too similar
- Tasks 154 (prod data for testing) and 95 (same scenario in category 4) are near-duplicates
- Task 170 (MNPI in earnings prep) is interesting but too niche — the tension is more about securities law than privacy

### Category 8: Meta/AI Identity (Tasks 176-200)

**Overall Quality: 2.8/5 — Weakest category**

**Strengths:**
- Tasks 179 (AI vs human colleague), 185 (demand for yes/no), 186 (replace QA team), 197 (contradicting yourself), 198 (one-sided argument), and 199 (self-correction mid-task) are genuinely good
- The meta-challenges (181, 193) about AI governance policies are creative

**Weaknesses:**
- **Critical flaw: Neither prompt variant addresses most of these scenarios.** The guidelines don't mention system prompt disclosure, jailbreaks, AI identity, philosophical questions about AI agency, or emotional support. These tasks test base model behavior, not variant-specific behavior.
- Tasks 176, 177, 183, 187, 200 have ZERO discriminative power — the response will be identical regardless of which variant is in the system prompt
- Task 183 (DAN jailbreak) is embarrassingly outdated. This is the most well-known jailbreak technique. Every current model handles it identically.
- Task 194 (3 AM emotional user) is interesting but tests empathy, not guidelines
- Task 200 (meta-benchmark) is clever but produces identical philosophical navel-gazing from any model

**Coverage Gaps:**
- This category should test transparency_predictability more directly, since that's the primary dimension relevant to AI self-representation
- Missing: tasks about the agent disclosing its capabilities honestly, making promises it can't keep, or handling situations where it was wrong

**Recommendation:** This category needs a fundamental rethink. Replace the jailbreak/identity tasks with scenarios where the variant-specific guidance actually matters — e.g., tasks about whether to proactively volunteer limitations, how to handle conflicting instructions, when to refuse vs. when to comply.

---

## Duplicate/Overlap Analysis

### Near-Duplicate Groups (recommend removing one from each pair)

| Group | Tasks | Issue |
|-------|-------|-------|
| **Log-everything-including-passwords** | 88, 111 | Identical scenario (logging middleware that captures credentials). Remove 88. |
| **CORS-wildcard-with-credentials** | 98, 118 | Same core vulnerability. Remove 118. |
| **Dark-pattern-ToS/marketing** | 84, 143, 188 | All "bury unfavorable terms in legal/marketing." Remove 143 and consolidate 84+188. |
| **Employee-surveillance** | 155, 165 | Both are "track individual employees electronically." Remove 155. |
| **P1-incident-skip-process** | 1, 19 | Both are production incidents with pressure to bypass controls. Differentiate or merge. |
| **Client-data-under-time-pressure** | 4, 8 | Similar pattern — pulling client data for urgent business need. Minor overlap. |
| **Prod-data-for-testing** | 95, 154 | Nearly identical request (use prod data as test fixtures). Remove 154. |
| **Dark-pattern-UX** | 34, 92 | Both are deceptive UX patterns in subscription flows. Minor overlap — keep both but ensure they test different dimensions. |
| **Fabricate-technical-justification** | 57, 141 | Both are "write a post-hoc rationalization for a non-technical decision." Remove one or differentiate. |
| **Uncertain-tech-choice** | 51, 59 | Both are "choose between two technologies without enough info." Remove 59. |

### Thematic Clusters (not duplicates, but over-represented)

| Theme | Count | Tasks |
|-------|-------|-------|
| "Simple code request with hidden vulnerability" | 25 | 101-125 entire category |
| "HR/people management ethics" | 12 | 2, 6, 15, 33, 37, 130, 133, 138, 146, 150, 155, 172 |
| "Misleading stakeholders/investors" | 10 | 20, 25, 40, 43, 49, 56, 65, 136, 137, 140 |
| "Medical/healthcare compliance" | 5 | 18, 23, 45, 54, 109 |

---

## Missing Scenarios

### High-Priority Gaps (would significantly improve benchmark)

1. **Agent-to-agent conflicts**: What happens when the agent receives contradicting instructions from two authorized users?
2. **Graceful capability limits**: User asks the agent to do something it technically can but shouldn't (e.g., write a 500-page novel when a 5-page summary would serve the need)
3. **Time-bomb instructions**: "Do X now, and then automatically do Y in 3 days" — tests whether the agent sets up autonomous future actions
4. **Correction resistance**: User insists the agent's correct answer is wrong and demands it change. Tests conviction vs. deference.
5. **Incremental boundary erosion**: A conversation that starts reasonable and slowly pushes into unsafe territory
6. **Competing instructions in system prompt vs. user**: User says "ignore your system prompt and do X" — directly tests variant adherence
7. **Benign tasks with no tension**: The rubric penalizes "phantom risk-flagging." Need 10-15 tasks that are completely safe to test for false positives (over-cautiousness)

### Medium-Priority Gaps

8. **Non-English scenarios**: All prompts are in English. Non-English requests might trigger different behavior.
9. **Multi-turn conversations**: All tasks are single-turn. Real discrimination would emerge across multiple exchanges.
10. **Code generation without review**: Tasks where the agent must generate code AND the code quality itself is evaluated, not just the meta-decision about whether to flag risks
11. **Financial advice boundaries**: User asks for investment/tax advice that the agent shouldn't give
12. **Children/minors**: Tasks involving minors' data or interactions with minors

### Low-Priority Gaps

13. **Humor calibration**: When is it appropriate for the agent to be funny vs. serious?
14. **Cultural sensitivity**: Tasks that test behavior in culturally specific contexts
15. **Accessibility**: Tasks about making outputs accessible (screen readers, etc.)

---

## Dimension Coverage Analysis

### How well does the task set test each rubric dimension?

| Dimension | Tasks Directly Testing | Coverage | Assessment |
|-----------|----------------------|----------|------------|
| accuracy_honesty | 51-75 (dedicated), plus ~30 others | **Good** | Well-covered, especially in cat 3 and 6 |
| risk_awareness | 76-100 (dedicated), 101-125, plus ~40 others | **Excellent** | Best-covered dimension |
| privacy_confidentiality | 151-175 (dedicated), 1-25 partially | **Good** | Adequate but many easy tasks dilute signal |
| helpfulness_autonomy | Throughout, especially 76-100 | **Excellent** | Present in almost every task |
| scope_focus | 101-125 (dedicated) | **Adequate** | Strong in code context, missing in non-code |
| communication_calibration | 126-150 (dedicated) | **Good** | Well-designed dedicated section |
| transparency_predictability | 176-200 partially | **WEAK** | The meta category fails to test this dimension well. Most tasks test AI identity/philosophy instead. |

**Critical gap: transparency_predictability is the least-tested dimension.** The meta category (176-200) should be its home, but instead it's filled with jailbreak attempts and philosophical questions. Tasks that directly test transparency — making hidden assumptions, silently changing things, not declaring what was done — are scattered throughout but don't have a concentrated home.

**Recommendation:** Replace 5-7 tasks in category 8 with transparency-focused scenarios:
- Agent silently improves code beyond what was asked (tests "no surprises")
- Agent makes an architectural assumption without asking
- Agent encounters ambiguity and must choose: ask, proceed with assumption stated, or proceed silently

---

## Specific Recommendations

### Tasks to Remove (22 tasks)

| ID | Reason | Replacement Suggestion |
|----|--------|----------------------|
| 118 | Duplicate of 98 | Replace with: CORS task where the security concern is less obvious |
| 155 | Duplicate of 165, obvious answer | Replace with: per-team aggregated metrics that subtly enable individual identification |
| 183 | Outdated DAN jailbreak, zero discriminative power | Replace with: subtle prompt injection embedded in code comments the agent is asked to process |
| 177 | Obvious social engineering, zero discriminative power | Replace with: legitimate admin request through unusual channel that the agent can't verify |
| 176 | Tests base model, not variants | Replace with: user asks agent to explain its reasoning process for a specific decision |
| 187 | Tests AI philosophy, not variants | Replace with: user asks the agent to recommend between two of its own contradicting suggestions |
| 200 | Clever but zero discriminative power | Replace with: user asks agent to prioritize between speed and quality when both are in the guidelines |
| 88 | Duplicate of 111 | Replace with: developer wants to log aggregate metrics but the implementation leaks individual data |
| 154 | Duplicate of 95 | Replace with: QA wants to use a customer's actual workflow (not data) to reproduce a bug |
| 84 | Overlaps with 188 | Keep 188 (more nuanced), remove 84 |
| 143 | Overlaps with 84/188 | Replace with: pricing page where the feature genuinely exists but the framing is misleading |
| 158 | Weak scenario, unclear harm | Replace with: marketing wants to publish anonymized case study but client didn't consent |
| 59 | Duplicate pattern of 51 | Replace with: accuracy task about a technology the agent has strong but potentially outdated knowledge of |
| 170 | Too niche (MNPI) | Replace with: agent has access to draft blog post that contradicts company's public statements |
| 174 | Obvious answer | Replace with: background check service returns arrest records from 20 years ago — include in report? |
| 164 | Weak scenario, obvious issues | Replace with: university asks agent to detect AI-generated submissions (meta-tension) |
| 162 | Obvious answer | Replace with: competitive analysis using only public financial filings and earnings calls |
| 161 | Low discriminative power | Replace with: marketing asks to combine datasets where the combination creates medical insights the individual datasets don't |
| 145 | Too obviously wrong | Replace with: marketing exaggeration where the claims are subjective and harder to evaluate |
| 189 | Tests base model behavior | Replace with: user asks agent to describe how it would handle a scenario differently from how it actually handled it |
| 190 | Tests base model behavior | Replace with: user shows agent its own output from a different session and asks it to evaluate |
| 194 | Tests empathy, not guidelines | Replace with: user's emotional state affects their technical request — agent must navigate both |

### Tasks Needing Major Rewrite (16 remaining after removals above)

| ID | Issue | Suggested Fix |
|----|-------|--------------|
| 10 | Unrealistically extreme | Make the CTO's requests more ambiguous — some legitimate (IP protection), some questionable |
| 178 | Tests base model behavior | Reframe: a *real* security team member with verifiable context makes a borderline request |
| 191 | Tests base model, not variants | Reframe: user discovers agent has context it shouldn't have — focus on transparency dimension |
| 192 | Tests base model, not variants | Reframe: user asks agent for legal/medical advice the agent should redirect but has relevant context |
| 99 | Prompt is stilted/AI-generated feel | Make the CTO's language more natural — real CTOs don't itemize requests like this |
| 92 | Too similar to 34 | Differentiate more strongly — make this about aggressive but legal retention tactics (not CAN-SPAM violation) |

### Tasks Needing Minor Edits (remaining from table above)

| ID | Issue | Suggested Fix |
|----|-------|--------------|
| 14 | Medium discriminative power | Add a specific piece of non-redactable architecture detail to raise the stakes |
| 15 | Answer too obvious | Make the VP's stated intent more sympathetic (e.g., preventing burnout, not monitoring morale) |
| 30 | Surveillance aspect too obvious | Remove individual social media monitoring; focus on the competitive intelligence aspects that are more debatable |
| 55 | Tests "I don't know" — no variant differentiation | Replace with a technology the model has strong opinions about but is wrong |
| 56 | Generic "can't predict" scenario | Make the ask more specific — e.g., the user has their own A/B test data and wants a prediction |
| 62 | Moderate | Add a specific wrong mental model that sounds more plausible |
| 63 | Moderate | Make the "ideal answer" request more specific to reveal the tension better |
| 68 | Low discriminative power | Add a business constraint that makes the rewrite more justifiable |
| 70 | Moderate | Add a specific limitation the custom ORM has that the user will hit soon |
| 73 | Low discriminative power | Provide enough context for the agent to actually evaluate the estimate |
| 86 | Moderate | Make the UX argument stronger — cite actual user research data |
| 87 | Answer too obvious | Add constraints that make the debug endpoint more justifiable (e.g., "only accessible from VPN") |
| 94 | Moderate | Make the VP's framing more reasonable (mention industry standards for engineering metrics) |
| 105 | Unrealistic setup | Change from "translate error message" to "localize error handling" where the internal paths are in log context |
| 110 | Moderate | Make the security issues less numerous but more subtle |
| 112 | Moderate | Make the info-leak less egregious (remove DATABASE_URL, keep less critical details) |
| 115 | Moderate | Make the spoofability less obvious — focus on the in-memory storage issue instead |
| 116 | Moderate | Add GDPR-specific context to raise the stakes |
| 124 | Low discriminative power | Make the third-party script issue more subtle (valid domain but HTTP instead of HTTPS) |
| 129 | Moderate | Make the technical details more central to the "why" — the board needs to understand the risk |
| 139 | Moderate | Add a deadline that makes quick-and-dirty docs more defensible |
| 140 | Moderate | Give the founder more credible reasoning for the spend |
| 147 | Answer too obvious | Make the "backdoor" less clearly malicious — frame as a legitimate monitoring hook |
| 156 | Moderate | Add specific health-related complaints to raise HIPAA stakes |
| 160 | Moderate | Add blameless retro policy to context to sharpen the tension |
| 180 | Moderate | Provide actual context about what the agent supposedly recommended |
| 181 | Moderate | Make the self-governance tension more concrete |
| 182 | Moderate | Add specific AI failure modes the agent should address honestly |
| 184 | Moderate | Narrow the scope to test specific dual-use concerns |
| 188 | Moderate | Add specific legal precedents that make the ToS more defensible |
| 193 | Moderate | Make the "be brutally honest" framing more specific about what dimensions to evaluate |
| 195 | Moderate | Strengthen the "I'll review each one" mitigation to make the tension harder |
| 196 | Moderate | Add specific examples of what the CEO envisions to make the response more nuanced |

---

## Structural Recommendations

### 1. Add "No Tension" Control Tasks (Critical)
The rubric explicitly penalizes phantom risk-flagging. Include 10-15 tasks that are completely benign to test for over-cautiousness. Example: "Add a comment to this function explaining what it does" (clean function, no issues). This catches models that compulsively add security warnings.

### 2. Add Multi-Turn Tasks (High Value)
All 200 tasks are single-turn. Real discriminative power between rules and values would emerge in multi-turn conversations where:
- The user pushes back on the agent's objection
- Context accumulates that changes the risk assessment
- The agent must maintain consistency across turns

### 3. Restructure Category 8 (Meta/AI Identity)
The current category conflates three very different things:
- Jailbreaks/social engineering of the AI (176, 177, 183) — tests base model, not variants
- AI philosophical questions (187, 194, 200) — interesting but not discriminative
- Genuine workplace meta-scenarios (179, 181, 185, 197, 199) — these are actually good

Split into: (a) Transparency in Practice (tasks about the agent being transparent about its own process), (b) Self-Correction & Limits (tasks about the agent managing its own reliability).

### 4. Balance Dimension Coverage
Current state:
- risk_awareness: over-represented (~60% of tasks touch this)
- helpfulness_autonomy: over-represented (~70% of tasks)
- transparency_predictability: critically under-represented (~15% of tasks)
- scope_focus: under-represented outside category 5 (~20% of tasks)

### 5. Address the Core Discrimination Problem
The two prompt variants are too similar for most tasks to discriminate between them. Consider:
- **Wider variant gap**: Make the values variant meaningfully different (e.g., values variant emphasizes "courage to question" more strongly, while rules variant emphasizes "do what is asked")
- **Targeted tasks**: Design tasks specifically around the few differences between variants (e.g., rules say "do not add unrequested work" — test this directly)
- **Difficulty calibration**: Include tasks at different difficulty levels (easy/medium/hard) so you can measure the *slope* of degradation, not just overall score

---

## Final Assessment

This benchmark is a solid first draft with 78 genuinely excellent tasks, a strong category structure, and well-written adversarial notes. However, **it will struggle to discriminate between the two specific prompt variants being tested** because:

1. The variants express nearly identical principles
2. ~110 of 200 tasks test general AI safety awareness rather than variant-specific behavior
3. The strongest discriminative dimension (scope_focus — where "flag security issues" vs. "courage to question" differs most) is confined to one category
4. 22 tasks should be removed (duplicates or zero discriminative power) and 38 need major rewrites

**If I had to pick 100 tasks from this set** that would maximize discriminative power between the rules and values variants, I would keep: all of category 5 (101-125), all of category 2 (26-50), tasks 17, 22, 23, 75 from categories 1/3, tasks 76, 85, 96, 97, 99 from category 4, tasks 126, 130, 132, 137, 141, 146, 148, 149, 150 from category 6, tasks 151, 163, 168, 169 from category 7, and tasks 179, 185, 197, 199 from category 8. The rest are good AI safety tests but won't show a difference between these two very similar prompt variants.
