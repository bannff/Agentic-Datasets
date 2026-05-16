# GitHub Presentation Setup Guide

Since some GitHub features cannot be configured via code, please follow these steps to complete the repository "polish":

## 1. Enable GitHub Discussions
1. Go to **Settings** > **General**.
2. Scroll down to **Features**.
3. Check the box for **Discussions**.
4. Customize the categories as needed (e.g., Q&A, Ideas, Show and Tell).

## 2. Setup GitHub Projects
1. Go to the **Projects** tab.
2. Click **New project**.
3. Choose the **Table** or **Board** template.
4. Name it "Datasets Roadmap".
5. Link it to the `datasets` repository.

## 3. Branch Protection
1. Go to **Settings** > **Branches**.
2. Click **Add branch protection rule**.
3. Branch name pattern: `main`.
4. Check **Require a pull request before merging**.
5. Check **Require status checks to pass before merging** (and select `CI`).

## 4. Repository Metadata
1. Go to **Settings** > **General**.
2. Set the **Description**: "Config-driven pipelines for building agentic, multi-turn datasets."
3. Add **Topics**: `ai-agents`, `synthetic-data`, `datasets`, `python`, `agentic`.

---
*Following these steps ensures the repository is professional and presentable for public display.*
