"""Render the documentation's display math to self-hosted SVG files.

The docs used to load MathJax and require.js from a third party CDN to render
LaTeX in the browser. To remove that live third party code (the same class of
risk as the polyfill.io supply chain attack), display equations are pre rendered
to static SVGs committed in the repo, and inline math is written as plain HTML.

This is a dev only build tool. It is never shipped to the site and adds no
runtime dependency for visitors. It only needs matplotlib:

    poetry run pip install matplotlib   # or add to the docs/dev extras
    poetry run python render_docs_math.py

Source of truth is the markdown itself: every display equation is an image whose
alt text is the original LaTeX, e.g.

    ![S = -\\sum_{i=1}^{n} p_i \\log(p_i)](img/math/eq-01.svg){ .math-display }

The script parses those references and (re)generates the referenced SVG from the
alt text, so editing a formula means editing the LaTeX in the markdown and re
running this script.
"""

import os
import re

import matplotlib

matplotlib.use("svg")
import matplotlib.pyplot as plt

# Markdown files that contain display math, relative to this script.
DOCS = [
    os.path.join("docs", "getting-started", "features", "entropy.en.md"),
]

# matplotlib's mathtext does not support \text{...}; map it to upright text and
# keep a thin space so units like "bits" do not touch the preceding number.
TEXT_RE = re.compile(r"\\text\{\s*([^}]*?)\s*\}")

# ![<latex>](<...>.svg){ ... .math-display ... }
IMG_RE = re.compile(
    r"!\[(?P<latex>[^\]]*)\]\((?P<path>[^)]*\.svg)\)\{[^}]*\.math-display[^}]*\}"
)


def texify(latex):
    return TEXT_RE.sub(lambda m: r"\;\mathrm{" + m.group(1) + "}", latex)


def render(latex, out_path, fontsize=18):
    fig = plt.figure()
    fig.text(0, 0, "${}$".format(texify(latex)), fontsize=fontsize)
    fig.savefig(
        out_path,
        format="svg",
        bbox_inches="tight",
        pad_inches=0.05,
        transparent=True,
        # Drop the timestamp so re running produces byte stable output.
        metadata={"Date": None},
    )
    plt.close(fig)


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    total = 0
    for doc in DOCS:
        doc_path = os.path.join(here, doc)
        doc_dir = os.path.dirname(doc_path)
        with open(doc_path, encoding="utf-8") as handle:
            text = handle.read()
        for match in IMG_RE.finditer(text):
            latex = match.group("latex")
            out_path = os.path.normpath(os.path.join(doc_dir, match.group("path")))
            os.makedirs(os.path.dirname(out_path), exist_ok=True)
            render(latex, out_path)
            total += 1
            print("rendered", os.path.relpath(out_path, here))
    print("done:", total, "equations")


if __name__ == "__main__":
    main()
