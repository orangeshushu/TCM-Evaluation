# Data Availability Plan

This document describes the planned data and code release for the TCM-Evaluation project.

## Target Journal

The project is being prepared for submission to **npj Digital Medicine**. Nature Portfolio policy requires a Data Availability statement that makes the conditions of access to the minimum dataset needed to interpret, verify, and extend the research transparent to readers.

## Current Release Status

The full dataset is not yet public because the manuscript is still under review/pre-publication preparation. The complete de-identified research package will be released after manuscript acceptance and before or at publication.

This repository currently documents the study and will be used as the public project landing page.

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

Planned route: **public repository release after manuscript acceptance**.

The recommended release pattern is:

1. Create a cleaned GitHub release for analysis code and lightweight source data.
2. Deposit the full de-identified dataset in Zenodo, Figshare, OSF, or another stable repository that provides a DOI.
3. Link the dataset DOI from this GitHub repository.
4. Cite the dataset formally in the manuscript reference list or Data Availability section.
5. Archive the accepted code release with the same version tag used for the manuscript.

## Privacy and Restrictions

The public dataset will contain only de-identified information. Direct identifiers and any fields that cannot be safely de-identified will be removed before release.

If any case-level information remains restricted after de-identification review, the public release will include:

- a description of the restricted field,
- the reason for restriction,
- the contact route for justified academic access,
- the review criteria for requests, and
- the available metadata or aggregate substitute.

## Draft Manuscript Wording

Use this wording before the final repository DOI is available:

```text
Data Availability
The de-identified benchmark cases, model-generated reports, physician-generated reports, expert scoring data, scoring rubric, and source data underlying the figures will be made publicly available after manuscript acceptance and before or at publication in a versioned public repository. Direct identifiers and any information that cannot be safely de-identified will not be released. The final repository URL and persistent identifier will be added upon acceptance. The analysis code will be available at https://github.com/orangeshushu/TCM-Evaluation.
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

## Risk Flags to Resolve Before Acceptance

- Select the long-term dataset repository and license.
- Confirm whether any case-level fields require controlled access.
- Confirm whether physician-generated reports and expert scoring records can be fully released after de-identification.
- Add a final dataset DOI and code archive DOI.
- Replace provisional wording in the manuscript and README with final repository identifiers.

