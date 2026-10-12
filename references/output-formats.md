# Output Format Templates

Standard templates for the Lecture Notes Tutor skill. Trim to fit the depth the user
chose, but keep the structure consistent so returning users know where everything is.

> **Language rule**: all headings and labels below are written in English.
> Always render them in the explanation language at runtime — translate naturally
> (headings, labels, section names), keeping the structure identical.

---

## 1. Study outline template

```markdown
# 📚 Study Outline — <courseware name>

**Topic in one sentence**: <what this courseware covers>
**X pages total, suggested N batches**

## Module 1: <title> (pages 1–8)
- Point 1
- Point 2 ⭐ key point
- Point 3 ⚠️ difficult point

## Module 2: <title> (pages 9–20)
- …
```

⭐ key points: exam hotspots or repeatedly emphasized content.
⚠️ difficult points: abstract or easily-confused concepts.

---

## 2. Per-page explanation template (chat)

```markdown
📄 Page X | <page title>
━━━━━━━━━━━━━━
📌 Key point: <one-sentence summary>
📖 Explanation: <plain-language detail; describe figures: "this figure shows…">
🔑 Key terms: <term — meaning> (bilingual for foreign-language courseware)
⭐ Exam angle: <how it could be tested> (optional)
🔗 Context: <link to neighboring pages> (optional)
🖼 Figure: <embedded image or "see exported doc" + how-to-read note>
```

---

## 3. Quiz template

```markdown
## ✍️ Practice Quiz — <module name>

### Basic
1. (Multiple choice) …… A. … B. … C. … D. …
2. (Fill in the blank) ……
3. (True/False) ……

### Applied
4. (Short answer) ……
5. (Calculation / analysis) ……

### Challenge
6. (Synthesis / open-ended) …… (marked: extension beyond the courseware)

---
## 🔑 Answers & Explanations
1. B — because …… (see page X)
2. ……
```

In interactive mode, send the questions only; grade question-by-question afterwards.

---

## 4. Resource recommendation template

```markdown
## 🔗 Further Learning

| Resource | Link | Why (maps to…) |
|---|---|---|
| MIT OCW: xxx | https://… | Covers Module 2 in more depth, with worked examples |
| Video "xxx" | https://… | 10-minute animation explaining ⚠️ topic xxx |
| Textbook "xxx", ch. 3 | …… | Pages 9–15 of the deck come from this chapter; good exercises |

> Note: links may change or expire — check the live page.
```

---

## 5. Exported document structure (md / docx / pdf)

```markdown
# Review Notes — <courseware name>

> Source: <file> (X pages) | Date: <date> | Language: <explanation language>

## 1. Course Outline
<as template 1>

## 2. Page-by-page Walkthrough
### Pages 1–5 — <module title>
#### 📄 Page 1 <title>
- **Key point**: ……
- **Explanation**: ……
- **Key terms**: ……

![Figure from page 1](images/slide01_img1.png)
*Caption: one sentence describing what the figure shows.*

(…remaining pages…)

## 3. Practice Quiz
<questions from template 3>

## 4. Answers & Explanations
<separate chapter so self-testing works>

## 5. Further Learning
<as template 4>

## 6. Glossary (optional)
| Term | Meaning | Page |
```

Figures are always referenced from the `images/` subfolder (output of
extract_images.py) so the note renders identically as md / HTML / Word / PDF.

---

## 6. Rules for illustrated explanations

**When to include a figure**:
- The page's core information lives in the figure (data charts, flowcharts,
  architecture diagrams, schematics, formula-derivation graphics) → always include and explain
- Purely decorative images (covers, backgrounds, clip art) → skip
- Text alone fully covers the page → optional

**Figure source priority**:
1. Original figures extracted from the courseware (extract_images.py for PPTX)
2. PDF courseware (no batch extraction): reference "see figure on page X of the
   courseware" and explain in words; draw an **SVG** diagram for key concepts
   (vector art, works in md/docx/pdf)
3. Mermaid is for chat and md preview only; convert to SVG or text before Word/PDF export

**Every figure needs a caption**: one sentence on what it shows and where to look.
