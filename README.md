# Krux ✝
Krux is an open-source DIY hardware signer for Bitcoin that can sign for multisignature and single-key wallets. It is a low-cost airgapped device built from off-the-shelf parts that communicates with wallet software via QR codes and wipes its memory after every session.

<p align="center">
<img src="https://jreesun.github.io/krux/img/pic-krux-logo.png" width="195">
</p>

---
## Disclaimer
**WARNING**: *This is currently beta-quality software and has not yet been audited by a third party. Use at your own risk!*

---

# Getting Started
Instructions for building and running Krux can now be found on our GitHub Pages site:

https://jreesun.github.io/krux/

# Development
## Running tests
```
poetry install
poetry run pytest --cov=krux --cov-branch --cov-report=html --show-capture=all --capture=tee-sys -r A tests
```

# Inspired by these similar projects:
- https://github.com/SeedSigner/seedsigner for Raspberry Pi (Zero)
- https://github.com/diybitcoinhardware/f469-disco for the F469-Discovery board

# Contributing
Issues and pull requests welcome! Let's make this as good as it can be.

# Get Support
For support installing or using Krux, please join [#krux:matrix.org](https://matrix.to/#/#krux:matrix.org) and ask questions there. We do not use GitHub issues for support requests, only for bug reports and feature requests.

You can also post a question in our [Discussions](https://github.com/jreesun/krux/discussions) forum here on GitHub.

# Give Support
If you would like to support the project, BTC is kindly accepted!

`19f8HVt8LZKzBv8CuBYnxCqn5sd75V658J`
