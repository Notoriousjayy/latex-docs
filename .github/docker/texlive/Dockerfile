# Pinned CI toolchain for latex-docs.
#
# Provisioning TeX Live through apt costs several minutes on every shard
# runner. Because that cost is paid once per shard, it scales linearly with
# matrix width and quickly dominates short incremental builds. This image
# freezes the exact package set so shards pay only an image pull.
#
# Rebuild and publish it with .github/workflows/build-ci-image.yml, then set
# `container-image` on the reusable workflow to the published tag. Always use
# an explicit version tag in production CI, never `latest`: the tag feeds the
# build fingerprint and cache keys, so a moving tag would silently invalidate
# or, worse, silently reuse results across different toolchains.

FROM ubuntu:24.04

ARG DEBIAN_FRONTEND=noninteractive

# Keep this list in sync with .github/actions/setup-latex/action.yml.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        texlive-latex-recommended \
        texlive-latex-extra \
        texlive-fonts-recommended \
        texlive-fonts-extra \
        texlive-pictures \
        texlive-science \
        texlive-bibtex-extra \
        texlive-plain-generic \
        texlive-luatex \
        texlive-xetex \
        latexmk \
        biber \
        python3 \
        python3-pygments \
        ghostscript \
        git \
        make \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Fail the image build rather than the document build if a required input is
# missing from the frozen package set.
RUN kpsewhich binhex.tex >/dev/null \
    && pdflatex --version | head -1 \
    && latexmk --version | head -1 \
    && pygmentize -V

LABEL org.opencontainers.image.title="latex-docs CI toolchain" \
      org.opencontainers.image.description="Pinned TeX Live + Pygments toolchain for latex-docs builds"
