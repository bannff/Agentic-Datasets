# Security Vulnerability Summary

## Status: ✅ ALL VULNERABILITIES RESOLVED

**Date**: December 7, 2025  
**Package**: agentic-datasets v0.1.0

## Quick Summary

- **Initial Scan**: 4 CVEs found in 2 packages
- **Current Status**: 0 CVEs (all resolved)
- **Action Taken**: Updated pyproject.toml with minimum secure versions

## Vulnerabilities Fixed

### 1. urllib3
- **Before**: 2.0.7 (2 CVEs - Medium severity)
- **After**: 2.6.0 (0 CVEs)
- **Issues Fixed**:
  - Streaming API improperly handles highly compressed data
  - Unbounded number of links in decompression chain

### 2. cryptography
- **Before**: 41.0.7 (2 CVEs - High severity)
- **After**: 46.0.3 (0 CVEs)
- **Issues Fixed**:
  - NULL pointer dereference in pkcs12.serialize_key_and_certificates
  - Bleichenbacher timing oracle attack

## Changes Made

Updated `pyproject.toml` to include:
```toml
dependencies = [
  # ... existing dependencies ...
  # Security: Enforce minimum versions to avoid known vulnerabilities
  "urllib3>=2.6.0",        # Fix CVE-2024: streaming API and decompression chain issues
  "cryptography>=42.0.4",  # Fix CVE-2024: NULL pointer dereference and Bleichenbacher attack
]
```

## Verification

✅ All dependencies scanned - no vulnerabilities found  
✅ Package imports successfully  
✅ CLI commands work correctly  
✅ Tests pass (excluding network-dependent tests)  

## Clean Dependencies

All other scanned dependencies are secure:
- typer 0.20.0 ✓
- pydantic 2.12.5 ✓
- pyyaml 6.0.1 ✓
- datasets 4.4.1 ✓
- huggingface_hub 1.2.1 ✓
- tiktoken 0.12.0 ✓
- datasketch 1.8.0 ✓
- langchain-text-splitters 1.0.0 ✓
- litellm 1.80.8 ✓
- strands-agents 1.19.0 ✓
- strands-agents-tools 0.2.17 ✓

For detailed information, see [SECURITY_VULNERABILITY_REPORT.md](./SECURITY_VULNERABILITY_REPORT.md)

---

**Next Steps**: None required. All vulnerabilities have been resolved.
