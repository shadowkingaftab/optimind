# Known limitations

A living list of limitations and biases relevant to the screening dataset and
model. Review before any evaluation claim. These reduce confidence; they are not
optional caveats.

## Data limitations

- **Representativeness:** site/device/age/sex distribution is INPUT_REQUIRED.
  Under-represented subgroups limit generalisation claims.
- **Label noise:** annotations are a screening reference, not a diagnosis;
  inter-rater agreement is INPUT_REQUIRED.
- **Image quality:** low-quality, ungradable or artefact-heavy images may be
  under- or over-represented; see the cleaning report.
- **Duplicates/near-duplicates:** mitigated by checksum and dHash checks, but no
  detector is perfect.

## Methodological limitations

- **Screening, not diagnosis.** Outputs flag images for human review; they do not
  establish a diagnosis.
- **Threshold dependence.** Sensitivity/specificity depend on thresholds that
  must be set per deployment and population.
- **Calibration.** Probability estimates require recalibration per site/device.
- **Subgroup performance.** Metrics must be reported by subgroup; aggregate
  metrics can hide disparity.

## Usage limitations

- Not validated for clinical deployment or regulatory use.
- Not for use outside the licensed population and acquisition conditions.
- External validation is required before any claim of generalisability.
