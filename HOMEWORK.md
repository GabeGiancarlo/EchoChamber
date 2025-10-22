# Homework: Research Paper Structure and Literature Review Workflow

## Deliverables

### 1. AI Literature Review Workflow
**File:** [prompts/literature-review.prompt.md](prompts/literature-review.prompt.md)

This workflow automates the literature review process for research on Wikipedia bot activity, automation bias, and AI-generated content. It extracts key information from academic papers to support research on how automated agents influence knowledge representation on Wikipedia.

### 2. LaTeX Research Paper
**Directory:** [paper/](paper/)

The paper structure includes:
- `main.tex` - Main LaTeX document with abstract, introduction, methodology, results, and conclusion
- `references.bib` - Bibliography with 5+ relevant references
- `README.md` - Compilation instructions

**Compiled PDF:** [paper/main.pdf](paper/main.pdf) (to be generated)

### 3. Repository Structure
The repository has been reorganized according to professional research standards:

```
EchoChamber-2/
├── data/          # datasets and data files (week7_results.json)
├── src/           # analysis scripts and code (week7.py, test_wikipedia_api.py, etc.)
├── paper/         # LaTeX paper files
├── literature/     # literature review files (literature-review.md)
├── prompts/       # AI agent workflows (literature-review.prompt.md)
├── figures/       # generated visualizations (empty, ready for plots)
├── static/        # web interface files (HTML, CSS, JS)
├── .gitignore     # git exclusions for LaTeX, Python, system files
└── README.md      # project documentation
```

## Reflection

### How did creating the AI workflow change your thinking about literature review?

Creating the AI workflow forced me to think more systematically about what information I actually need from research papers. Rather than just reading papers passively, the workflow requires me to identify specific research questions, methodologies, and findings that are relevant to my Wikipedia automation bias research. This structured approach helps ensure I extract actionable insights rather than just general knowledge.

The workflow also highlighted the importance of cross-paper synthesis - identifying common themes, conflicting findings, and research gaps across multiple studies. This systematic approach should lead to more comprehensive literature reviews that actually inform the research direction.

### What challenges did you encounter with LaTeX?

The main challenges were:
1. **Bibliography management** - Ensuring proper citation formatting and cross-references
2. **Package dependencies** - Making sure all required LaTeX packages are available
3. **Compilation workflow** - Understanding the multi-step process (pdflatex → bibtex → pdflatex → pdflatex)
4. **Cross-platform compatibility** - Different LaTeX distributions may have different package availability

The solution was to provide clear compilation instructions and suggest Overleaf as an alternative for users who don't have LaTeX installed locally.

### What are the next steps for your paper?

1. **Expand the literature review** - Use the AI workflow to analyze more papers and build a comprehensive related work section
2. **Add detailed methodology** - Include more specifics about data collection, bot detection algorithms, and bias measurement techniques
3. **Expand results section** - Add more detailed analysis of the 445 Wikipedia edits, including statistical significance tests
4. **Add figures and tables** - Create visualizations showing bot activity patterns, bias indicators, and topic comparisons
5. **Refine the discussion** - Connect findings to broader implications for knowledge platforms and automated content moderation
6. **Peer review** - Get feedback from collaborators and potentially external reviewers

The foundation is now in place with a well-structured repository, automated literature review workflow, and initial paper draft that can be iteratively improved throughout the semester.
