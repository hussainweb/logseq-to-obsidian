# Quickstart: Verifying the Refactoring

This refactoring is an internal code quality improvement. As such, there are no new features to "try out." The primary goal is to ensure that the application's behavior remains identical after the changes.

Verification can be done in two main ways:

## 1. Automated Testing

This is the most important verification step.

1.  **Ensure all dependencies are installed**:
    ```bash
    uv sync
    ```

2.  **Run the full test suite using `pytest`**:
    ```bash
    pytest
    ```

**Expected Outcome**: All tests should pass. This confirms that the refactored code continues to meet all existing functional requirements.

## 2. Manual End-to-End Verification

This step provides an extra layer of confidence by comparing the output of the refactored tool against a known-good baseline.

1.  **Run the converter on a sample Logseq graph**:
    ```bash
    # Ensure you have a sample Logseq graph available
    python -m src.logseq_converter.cli --input-dir /path/to/your/logseq-graph --output-dir /path/to/output-before
    ```

2.  **After the refactoring is complete, run the converter again on the same input, pointing to a new output directory**:
    ```bash
    python -m src.logseq_converter.cli --input-dir /path/to/your/logseq-graph --output-dir /path/to/output-after
    ```

3.  **Compare the two output directories**:
    ```bash
    diff -r /path/to/output-before /path/to/output-after
    ```

**Expected Outcome**: The `diff` command should report no differences between the two directories. This proves that the refactoring has not introduced any regressions in the final output.
