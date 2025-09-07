# Random Entropy Seed Generator  
<strong>Ensemble Methods for High-Quality TRNG-based Entropy</strong>

---

## Overview  
This project provides a framework for generating high-quality random entropy seeds using 
<strong>True Random Number Generators (TRNGs)</strong> combined through 
<strong>ensemble methods</strong>.  

Unlike pseudo-random number generators (PRNGs), TRNGs leverage unpredictable physical phenomena 
(e.g., thermal noise, oscillator jitter, or photon detection) to produce non-deterministic outputs.  

By applying ensemble techniques, this framework aggregates outputs from multiple TRNG sources, 
mitigating bias, reducing correlations, and ensuring stronger entropy suitable for cryptographic, 
security, and simulation use cases.  

---

## Features  
- ✅ Aggregation of multiple TRNG sources for robust entropy  
- ✅ Ensemble methods: majority voting, weighted mixing, XOR folding, and statistical normalization  
- ✅ Configurable entropy pool size for seed generation  
- ✅ Built-in entropy quality estimation (NIST SP 800-90B style statistical checks)  
- ✅ Output as seed material for PRNGs, key derivation, or secure token generation  

---

## Architecture  
```text
TRNG Source 1 ─┐
TRNG Source 2 ─┼─► Ensemble Layer ─► Entropy Pool ─► SHA-3 Hash ─► High-Strength Seed
TRNG Source 3 ─┘
