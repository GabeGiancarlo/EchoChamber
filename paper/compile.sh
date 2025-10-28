#!/bin/bash

# LaTeX Compilation Script
# This script compiles the main.tex file to PDF

echo "Compiling LaTeX document..."

# Check if pdflatex is available
if command -v pdflatex &> /dev/null; then
    echo "Using local pdflatex..."
    pdflatex main.tex
    bibtex main
    pdflatex main.tex
    pdflatex main.tex
    echo "Compilation complete! Check main.pdf"
else
    echo "pdflatex not found locally."
    echo ""
    echo "To compile this paper, you have several options:"
    echo ""
    echo "1. Install LaTeX locally:"
    echo "   - macOS: brew install --cask mactex"
    echo "   - Ubuntu: sudo apt-get install texlive-full"
    echo "   - Windows: Install MiKTeX"
    echo ""
    echo "2. Use Overleaf (recommended for beginners):"
    echo "   - Go to https://www.overleaf.com"
    echo "   - Create a new project"
    echo "   - Upload all files from this directory"
    echo "   - Click 'Compile'"
    echo ""
    echo "3. Use online LaTeX editors:"
    echo "   - ShareLaTeX"
    echo "   - LaTeX Base"
    echo ""
    echo "The paper is ready to compile - all required files are present:"
    echo "  - main.tex (main document)"
    echo "  - references.bib (bibliography)"
    echo "  - README.md (instructions)"
fi
