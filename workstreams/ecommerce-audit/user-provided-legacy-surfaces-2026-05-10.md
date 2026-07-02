# User-provided catalog_data surfaces for ecommerce audit

Date: 2026-05-10
Status: saved, not yet clicked by Moji in this parent session
Context: Guiding Light provided these as important catalog_data product/sales/backend surfaces while discussing the ecommerce audit and recurring artifactless-agent failure pattern.

## Surfaces

- `catalog_data/products`
- `catalog_data/sales`
- `catalog_data/action-361/70`
- `catalog_data/action-200`
- `catalog_data/products/57`
- `catalog_data/products/57/action-199`
- `catalog_data/products/57/action-199/250`

## Handling rule

These are authenticated/admin-like catalog_data surfaces. Future audit agents may inspect them only under the existing ecommerce access preflight rules:

- identify environment/auth context first;
- read/observe before mutation;
- do not write to catalog_data;
- do not expose secrets or private customer data in reports;
- record discrepancies between catalog_data docs, observed catalog_data behavior, and ERPNext behavior;
- preserve the distinction between concept translation and code copying.

## Failure Recipe link

The recurring no-artifact/truncated-subagent failure observed during this audit is cataloged in the capabilities framework as:

`/home/guidingl/projects/capabilities-framework/capabilities/failures/artifactless-research-delegation.md`
