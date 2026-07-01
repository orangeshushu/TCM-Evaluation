# Data and Code Availability

This document describes the data-release scope, privacy safeguards, and repository strategy for the TCM-Evaluation project.

## Repository Scope

This repository is intended to document the study design, analysis-code structure, model API-call templates, and aggregate figure outputs for a de-identified TCM clinical reasoning benchmark.

## Current Release Status

The full patient-level research dataset is not included in the current public repository. Any future release will include only materials that have completed de-identification, privacy review, and documentation checks.

Direct identifiers and information that cannot be safely de-identified will not be released.

## Dataset Inventory

The planned public release will include:

- `benchmark_cases`: de-identified clinical case records used for the 60-case benchmark.
- `source_cohort_metadata`: de-identified aggregate metadata for the 349-case source cohort.
- `model_outputs`: generated reports from all evaluated LLMs and repeated trials.
- `physician_outputs`: physician-generated reports used as the human comparator.
- `expert_scores`: blinded expert scores across nine dimensions.
- `scoring_rubric`: scoring definitions and reviewer instructions.
- `source_data`: source tables underlying each main and supplementary figure.
- `analysis_scripts`: scripts used for aggregation, statistical testing, and figure generation.

## Access Route

Planned route: **versioned public release after privacy and documentation review**.

The recommended release pattern is:

1. Create a cleaned GitHub release for analysis code and lightweight source data.
2. Deposit the full de-identified dataset in Zenodo, Figshare, OSF, or another stable repository that provides a DOI.
3. Link the dataset DOI from this GitHub repository.
4. Cite the dataset formally in any related publications or reuse documentation.
5. Archive the code release with the same version tag used for the dataset.

## Privacy and Restrictions

The public dataset will contain only de-identified information. Direct identifiers and any fields that cannot be safely de-identified will be removed before release.

If any case-level information remains restricted after de-identification review, the public release will include:

- a description of the restricted field,
- the reason for restriction,
- the contact route for justified academic access,
- the review criteria for requests, and
- the available metadata or aggregate substitute.

## Availability Wording

Use this wording before a final repository DOI is available:

```text
Data Availability
The de-identified benchmark cases, model-generated reports, physician-generated reports, expert scoring data, scoring rubric, and source data underlying the figures will be made available in a versioned public repository after completion of privacy, de-identification, and documentation review. Direct identifiers and any information that cannot be safely de-identified will not be released. The final repository URL and persistent identifier will be added when available. The analysis code will be available at https://github.com/orangeshushu/TCM-Evaluation.
```

Use this wording after the final repository DOI is available:

```text
Data Availability
The de-identified benchmark cases, model-generated reports, physician-generated reports, expert scoring data, scoring rubric, and source data underlying the figures are available at [repository name] under accession/DOI [identifier]. Direct identifiers and any information that could not be safely de-identified were removed before release. Analysis code is available at https://github.com/orangeshushu/TCM-Evaluation and archived at [code DOI or release URL].
```

## FAIR Metadata Checklist

Before public release, add:

- repository DOI or accession number,
- dataset version,
- release date,
- license,
- creators and affiliations,
- data dictionary,
- file-level descriptions,
- provenance for each table,
- relation to manuscript figures and tables,
- checksum or file integrity information for large files,
- software environment and package versions,
- reuse conditions and citation instructions.

## Release Checklist

- Select the long-term dataset repository and license.
- Confirm whether any case-level fields require controlled access.
- Confirm whether physician-generated reports and expert scoring records can be fully released after de-identification.
- Add a final dataset DOI and code archive DOI.
- Replace provisional wording in repository documentation with final repository identifiers.

