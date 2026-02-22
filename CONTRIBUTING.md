# Contributing to PromptSmith

Thank you for your interest in contributing to PromptSmith! We welcome contributions from the community to help make "Reasoning as a Service" better for everyone.

## Getting Started

1.  **Fork the repository** on GitHub.
2.  **Clone your fork** locally:
    ```bash
    git clone https://github.com/your-username/PromptSmith.git
    cd PromptSmith
    ```
3.  **Create a virtual environment**:
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate
    ```
4.  **Install dependencies**:
    ```bash
    uv sync
    ```

## Development Workflow

1.  **Create a branch** for your feature or bug fix:
    ```bash
    git checkout -b feature/amazing-feature
    ```
2.  **Make your changes**.
3.  **Run tests** to ensure nothing is broken:
    ```bash
    pytest
    ```
4.  **Commit your changes** with a descriptive message.
5.  **Push to your fork** and submit a **Pull Request**.

## Coding Standards

-   Follow PEP 8 style guidelines.
-   Include docstrings for new functions and classes.
-   Add unit tests for new features.

## Reporting Issues

If you find a bug or have a feature request, please open an issue on GitHub.
