# How to Contribute

We'd love to accept contributions to PyPtP in any form. You do not need to be a programming or power system expert to make a contribution. There are just a few small guidelines you need to follow before making a change.

## Ways of Contributing

Contribution does not necessarily mean committing code to the repository. Examples are:

1. **Test and use the library.** Give feedback on the user experience or suggest new features.
2. **Validate the model against other existing libraries.** Provide validation test cases.
3. **Report bugs.** Help us identify issues and edge cases.
4. **Update documentation.** Improve examples, fix typos, clarify explanations.
5. **Improve the Python interface or helper functions.**

A good place to start is to look at issues with the **good first issue** label.

## Before You Contribute

### License

PyPtP is licensed under GPL-3.0-or-later. By contributing, you agree that your code will be distributed under this license and may also be included in derived works under compatible terms.

### Contributor License Agreement (CLA)

**Why do we need a CLA?**

We want PyPtP to be freely available AND sustainable long-term. The CLA allows us to:
- Offer the GPL-3.0-or-later version (free and open source)
- Relicense parts of PyPtP (including community contributions) to allow a closed-source integration or proprietary SDK for a specific client
- Offer paid support and custom client-specific feature development

**You keep your copyright.** You're just giving us permission to use your contribution under both open source and commercial licenses.

**How does it work?**

When you submit your first pull request, the CLA Assistant bot will ask you to confirm the agreement by clicking a checkbox. It takes 30 seconds. See [CLA.md](CLA.md) for the full text.

## Filing Bugs and Feature Requests

You can file bugs and feature requests for the project via [GitHub Issues](https://github.com/phasetophase/pyptp/issues).

**Before filing an issue:**
1. Search existing issues to avoid duplicates
2. For bugs: include minimal reproduction steps and expected vs actual behavior
3. For features: explain the use case and why it's valuable

**Good bug reports include:**
- PyPtP version (`pip show pyptp`)
- Python version
- Operating system
- Minimal code to reproduce the issue
- Expected behavior
- Actual behavior (including error messages)

## Pull Request Process

### Required: Issue First, Then Pull Request

**We require an issue to be created before submitting a pull request.** This helps us:
- Discuss the approach before you invest time coding
- Avoid duplicate work
- Ensure the change aligns with project goals

**Process:**
1. **Create an issue** describing the bug or feature
2. **Wait for maintainer feedback** (we'll respond within a few days)
3. **Fork the repository** and create a topic branch
4. **Make your changes** following our style guide
5. **Submit a pull request** that references the issue

### Review Process

Pull requests will be reviewed by maintainers who may:
- Discuss and offer constructive feedback
- Request changes
- Approve the work

Upon receiving approval, a maintainer will merge your changes.

## Style Guide

### Python Code

This project follows pyright "basic" mode type-checking. And a very strict custom-ruff ruleset.

---

**Thank you for contributing to PyPtP!** 🎉