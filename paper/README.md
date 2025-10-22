# LaTeX Paper Compilation Instructions

## Prerequisites
- LaTeX distribution (TeX Live, MiKTeX, or MacTeX)
- Required packages: natbib, hyperref, amsmath, graphicx

## Compilation
To compile the paper to PDF:

```bash
cd paper/
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

Or use the provided script:
```bash
./compile.sh
```

## Alternative: Overleaf
1. Create a new project on [Overleaf](https://www.overleaf.com)
2. Upload all files from the `paper/` directory
3. Compile using the "Compile" button

## File Structure
- `main.tex` - Main LaTeX document
- `references.bib` - Bibliography database
- `README.md` - This file
- `compile.sh` - Compilation script (if provided)

## Troubleshooting
- Ensure all required packages are installed
- Check that `references.bib` is in the same directory as `main.tex`
- Run compilation multiple times if cross-references don't resolve
