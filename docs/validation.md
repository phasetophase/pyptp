# Network Validation

The validator module checks network topology and data integrity.

## Basic Usage

```python
from pyptp.validator import CheckRunner
from pyptp.IO.importers.gnf_importer import GnfImporter

# Load and validate network
importer = GnfImporter()
network = importer.import_gnf("network.gnf")
runner = CheckRunner(network)
report = runner.run_all()

# Check results
print(report.summary())  # "Found 3 issues: 2 error, 1 warning"

# Get detailed output
if report.issues:
    print(report.to_json())
```

## Filtering Validators

```python
from pyptp.validator import ValidatorCategory

# Run only core validators
report = runner.run(categories=ValidatorCategory.CORE)

# Run specific validators by name
report = runner.run(include=["cable_node_reference"])

# Exclude specific validators
report = runner.run(exclude=["transformer_node_reference"])
```

## Available Validators

Current built-in validators check:
- Cable node references
- Link node references
- Transformer node references

Need additional validation? Please suggest validators via [GitHub issues] or contribute one yourself via a [Merge Request]!
