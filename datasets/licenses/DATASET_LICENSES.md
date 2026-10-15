# Dataset licences

Register of licences for every dataset source used with EyeDx. **No dataset is
usable until its licence and consent basis are recorded here.** This file is a
template; fill in real values under governance review.

> Do not commit dataset content, keys or credentials. This register records only
> licence metadata.

## Register

| source_id | name | owner | licence | consent basis | retention | approved |
| --- | --- | --- | --- | --- | --- | --- |
| INPUT_REQUIRED | INPUT_REQUIRED | INPUT_REQUIRED | INPUT_REQUIRED | INPUT_REQUIRED | INPUT_REQUIRED | no |

## Licence field guidance

- **licence:** SPDX-style identifier or a clear name of the data-use agreement.
  The value `INPUT_REQUIRED` means the source is not yet cleared and will be
  refused by the importer.
- **consent basis:** the legal/ethical basis permitting this use.
- **retention:** how long data may be retained and when it must be deleted.
- **approved:** set to `yes` only after governance sign-off.

## Rules

1. A source without a recorded licence and consent basis must not be ingested.
2. Licences must permit the intended use (research and, separately, any
   deployment). Flag restrictions on redistribution, commercial use,
   derivatives or redistribution of trained weights.
3. Attribution obligations are tracked in [`attribution.md`](attribution.md).
4. Per-source permissions are summarised in [`usage-rights.csv`](usage-rights.csv).
