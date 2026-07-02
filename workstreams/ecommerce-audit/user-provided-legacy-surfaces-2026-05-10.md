# User-provided legacy_source surfaces for ecommerce audit

Date: 2026-05-10
Status: saved, not yet clicked by Moji in this parent session
Context: Guiding Light provided these as important legacy_source product/sales/backend surfaces while discussing the ecommerce audit and recurring artifactless-agent failure pattern.

## Surfaces

- `http://5.78.136.133/legacy_source/products`
- `http://5.78.136.133/legacy_source/sales`
- `http://5.78.136.133/legacy_source/action-361/70`
- `http://5.78.136.133/legacy_source/action-200`
- `http://5.78.136.133/legacy_source/products/57`
- `http://5.78.136.133/legacy_source/products/57/action-199`
- `http://5.78.136.133/legacy_source/products/57/action-199/250`

## Handling rule

These are authenticated/admin-like legacy_source surfaces. Future audit agents may inspect them only under the existing ecommerce access preflight rules:

- identify environment/auth context first;
- read/observe before mutation;
- do not write to legacy_source;
- do not expose secrets or private customer data in reports;
- record discrepancies between legacy_source docs, observed legacy_source behavior, and ERPNext behavior;
- preserve the distinction between concept translation and code copying.

## Failure Recipe link

The recurring no-artifact/truncated-subagent failure observed during this audit is cataloged in the capabilities framework as:

`/home/guidingl/projects/capabilities-framework/capabilities/failures/artifactless-research-delegation.md`
