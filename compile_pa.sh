#!/bin/bash
ok=0; fail=""
for d in build/paA*; do
  (cd "$d" && pdflatex -interaction=nonstopmode p.tex >/dev/null 2>&1 && pdflatex -interaction=nonstopmode p.tex >/dev/null 2>&1)
  if [ -f "$d/p.pdf" ] && [ "$(grep -c '^!' $d/p.log)" -eq 0 ]; then ok=$((ok+1)); else fail="$fail $(basename $d)"; fi
done
echo "clean=$ok"
echo "failed:$fail"
