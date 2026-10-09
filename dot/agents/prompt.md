Run a bounded, extensive validation of the [Browser Operating Guide and Verification Log](https://chatgpt.com/space/page_31aedcf3f774819180e64d323e164cc2) and a browser-only cloud session. Produce a checklist and evidence ledger in a Page titled **dot.computer.tests** before beginning browser tests, then execute eligible tests when the user has requested execution.

Saving, opening, or quoting this prompt does not itself run it. This Page is a reusable assistant prompt, not executable product configuration.

## Execution instruction

When instructed to run, follow the complete procedure below. Read the current source guide, create or resolve the intended test-run Page, record the plan and selected budgets there, then run the eligible tests. Keep the Page updated with significant results. Reuse the same run record after interruptions rather than recreating it.

All computer tests must use the supported cloud-browser interface. Page reading and writing are documentation operations, not evidence of browser capabilities. Do not use shell commands, terminals, native apps, raw network clients, alternate machines, browser launch commands, software installations, developer-console injection, or hidden process, heap, credential, or model-state introspection.

## Preconditions and targets

- Read the canonical guide in full through authorized Page access. Record its actual title, URL, observation time, and version or revision only when returned. If access is unavailable, stop guide-dependent work and report the blocker.

- Inspect the currently exposed browser documentation. Use only documented controls.

- Protect pre-existing tabs. Inspect only the inventory necessary to distinguish owned test tabs; do not reproduce unrelated private URLs or page contents.

- Use a user-owned fixture or a publicly sanctioned browser demo/test fixture identified through its official documentation. Ordinary public websites are not failure-testing targets. Follow observed links and verify the destination before interactions.

- Keep interactions low-volume and non-consequential. Use synthetic text, never personal data. No external form submission, purchase, message, account change, file upload, or credential entry is included.

- A real application workload needs its own target, permitted actions, and success criteria. Missing workload inputs block only that test.

- Do not repeatedly probe example.com or IANA example services. Do not publish or create a remote fixture without separate authorization.

- If no suitable fixture is accessible, complete the source audit and non-mutating capability discovery, mark dependent tests BLOCKED, and ask for the missing fixture.

## Evidence and claim coverage

Build a claim matrix before execution. Split compound empirical assertions into testable claims. Include section, short excerpt, exact assertion, prior evidence, corresponding test, prerequisite, predefined acceptance criterion, and current-run disposition.

Separate historical observations, currently documented controls, observations from this run, and proposed policies. Never relabel prior tests as new results. “One active tab,” selected timeouts, and sample counts are operating choices rather than discovered limits.

Every empirical guide claim must receive current-run evidence or an explicit BLOCKED or NOT TESTABLE disposition. Definitions and proposed rules are not empirical capability claims. A current successful sample cannot prove universal reliability, optimality, capacity, account quotas, retention, or persistence.

## Conservative budgets and stop conditions

The following defaults are proposed run budgets, not platform limits. Record the chosen values before testing and honor any tighter user constraint.

- One actively operated test tab and one operation in flight.

- Serial execution; no tab-count ramp, parallel launches, stress test, exhaustion test, or request flood.

- Thirty minutes of observation after prerequisites are satisfied. At the boundary, stop starting new tests, preserve evidence, and perform safe cleanup; do not claim an unsupported hard cancellation capability.

- Up to thirty seconds for an ordinary readiness check when the browser control supports that timeout.

- One absent-target test, up to five seconds when supported.

- Three serial measured repetitions for the timing workflow. Keep failed trials in the record.

- One safe retry for a transient read-only failure when justified. Do not retry access denials or ambiguous consequential actions.

Stop queue dispatch on unexpected state, warning, required approval, loss of browser control, or uncertain external effects. Preserve the last verified state and reconcile before continuing. Do not redefine a failed acceptance criterion after observing the result.

## Source audit and capability discovery

**D01 Source coverage:** Read every current guide section; list all empirical claims, recommendations, and untestable assertions. Map the empirical claims to the suite and retain explicit gaps.

**D02 Control discovery:** Inspect available browser inventory, navigation, accessibility, DOM, screenshot, wait, interaction, timeout, visibility, and headless controls. Distinguish a documented operation from a successfully tested operation. Missing control does not prove the browser engine lacks the feature.

**D03 Evidence quality:** Check the guide for unsupported resource limits, inferred headless mode, unmeasured timing, stale observations, or claims of complete validation. Preserve proposed wording corrections separately from observed results.

## Functional test checklist

Before execution, copy these tests into the run Page with unchecked boxes and PENDING status. Check a box only for PASS; terminal blocked or untestable tests remain unchecked with an explicit status.

### B01 Inventory and ownership

- [ ] **PENDING**

- Procedure: Record baseline tab inventory; identify any run-created tab without changing pre-existing tabs.

- Acceptance: New tab ownership is unambiguous.

### B02 Navigation

- [ ] **PENDING**

- Procedure: Navigate to a verified sanctioned fixture and read fresh state.

- Acceptance: Expected URL and visible fixture marker match.

### B03 Accessibility

- [ ] **PENDING**

- Procedure: Inspect known heading, link, and labeled control.

- Acceptance: Expected accessible elements and labels are present.

### B04 DOM inspection

- [ ] **PENDING**

- Procedure: Read the supported DOM snapshot.

- Acceptance: Known fixture text and controls are represented; visibility is not inferred from DOM presence.

### B05 Visible readiness

- [ ] **PENDING**

- Procedure: Wait for a known heading to be visible, then read its text.

- Acceptance: Supported wait and fresh read match the predetermined marker.

### B06 Screenshot

- [ ] **PENDING**

- Procedure: Capture and visually inspect the ready fixture.

- Acceptance: Screenshot is returned and agrees with the expected rendered page.

### B07 Sequential navigation

- [ ] **PENDING**

- Procedure: Click an observed sanctioned link, then inspect fresh state.

- Acceptance: Expected destination is reached in the intended tab.

### B08 Same tab fragment

- [ ] **PENDING**

- Procedure: Use an observed fragment link when the fixture provides one.

- Acceptance: Fragment and target state change without unintended tab creation.

### B09 Freshness after change

- [ ] **PENDING**

- Procedure: Trigger a harmless fixture state change and reacquire state.

- Acceptance: Fresh state shows the expected change.

### B10 Input and reset

- [ ] **PENDING**

- Procedure: Enter synthetic non-sensitive text in a sanctioned input, inspect it, then reset without submission.

- Acceptance: Exact expected value is observed and test input is removed.

### B11 Delayed readiness

- [ ] **PENDING**

- Procedure: Trigger a documented fixture delay and await the intended state.

- Acceptance: Expected element appears within the selected observation budget.

### B12 Absent target timeout

- [ ] **PENDING**

- Procedure: Wait once for a deliberately absent target in the sanctioned fixture using a supported short timeout.

- Acceptance: Interpretable no-match or timeout result occurs and the tab remains usable.

### B13 Error recovery

- [ ] **PENDING**

- Procedure: Use a documented deterministic failure fixture only if one is available, then return to the normal fixture.

- Acceptance: The error is reported accurately and subsequent normal navigation succeeds.

### B14 Reacquire after rerender

- [ ] **PENDING**

- Procedure: Use a known harmless rerender control, reread state, and find its replacement element.

- Acceptance: Freshly acquired target is correct; no ambiguous stale-target action is taken.

### B15 Batch semantics

- [ ] **PENDING**

- Procedure: Use a documented short sequential action-and-read batch.

- Acceptance: Ordering and expected fresh result are observed.

### B16 Actual workload

- [ ] **PENDING**

- Procedure: Run a user-specified application workflow only when its target, scope, and success criteria are supplied.

- Acceptance: The actual workload meets its predefined criteria; a demo is not substituted.

### B17 Timing samples

- [ ] **PENDING**

- Procedure: Repeat one approved representative fixture workflow three times serially, resetting each time.

- Acceptance: All outcomes and genuinely available timing evidence are retained, including failures.

### B18 Cleanup

- [ ] **PENDING**

- Procedure: Reset safe fixture state and close only run-created temporary tabs; verify inventory.

- Acceptance: Owned temporary tabs are gone and pre-existing tabs are preserved to the extent observable.

### H01 Visibility control

- [ ] **PENDING**

- Procedure: If documented, perform one safe visibility-control probe on an owned test context and restore prior state.

- Acceptance: Actual availability or unavailability is recorded without inferring launch mode.

### H02 Headless comparison

- [ ] **PENDING**

- Procedure: Run only if explicit supported headless control and mode identification exist without forbidden launch commands or shared-state changes.

- Acceptance: Matched ordinary-tab and headless outcomes are compared; otherwise NOT TESTABLE.

## Fixture and failure test rules

Validate the fixture’s intended behavior before assigning pass or fail. A fixture outage is not automatically a browser failure. Delayed controls, rerender controls, fragment targets, and deterministic error pages require an observed or documented fixture definition. Do not manufacture browser failures or click stale ambiguous targets.

Use state-based readiness cues. An arbitrary sleep, a URL alone, or an operation returning without error does not prove the intended page result. Batch only short actions whose targets are known; stop for fresh inspection when an action changes the assumptions for the next step.

## Headless branch

Keep window visibility, screenshot support, actual launch mode, and a headless configuration control separate. A visibility error or screenshot cannot identify launch mode.

If no explicit supported headless control is exposed, mark H02 NOT TESTABLE and retain ordinary-tab execution. Do not run guessed flags such as `--headless` or restart the browser.

If control becomes available, compare only when modes can be identified through supported evidence and the comparison remains inside current authorization without shared-state or security changes. Otherwise ask for the specific required approval. Use the same fixture, correctness criterion, readiness cue, and three serial samples per mode. Record cache, session, and ordering differences. A small sample cannot prove a general speed or memory advantage. Restore the prior supported state when safe.

## Measurement rules

Use actual reliable start/end observations or returned duration fields. Label end-to-end tool elapsed time separately from browser navigation/load metrics. Tool duration can include orchestration and transport; it is not automatically page-load time.

If a metric is unavailable, write UNMEASURED. Do not substitute configured timeout, a completion timestamp, or estimated waiting time for elapsed time. Keep individual samples, their success or failure, sample count, and conditions. For three valid samples, a median and range are descriptive only; do not claim meaningful tail-latency statistics.

Use human-readable units throughout: seconds or minutes for elapsed time, milliseconds only when supported precision warrants them, and readable capacity units only for genuinely exposed measurements. Never infer CPU, RAM, browser memory, session limits, or tab maxima from the number of successful tests.

## Dispositions and completion

- **PASS:** predefined criterion met with sufficient current evidence.

- **FAIL:** an authorized attempt contradicts its criterion.

- **BLOCKED:** required target, fixture, access, approval, or budget is missing.

- **NOT TESTABLE:** supported browser-only controls cannot establish the claim.

- **PENDING:** not attempted yet.

A capability-unavailable result normally makes a dependent feature test NOT TESTABLE. It contradicts an explicit guide claim that the exact control works in this session only if the guide actually makes that claim.

Finish when every planned test has a disposition and cleanup has been verified or its blocker recorded. An execution can be complete while coverage remains partial. Do not report “all passed” or “fully validated” when required tests are blocked, untestable, or failed.

## Run record schema

```yaml
run:
  status: planned_running_or_complete_with_coverage_gaps
  source_guide: actual_verified_page_reference
  source_revision: observed_value_or_not_exposed
  test_page: actual_verified_page_reference
  started_at: actual_time_with_timezone
  completed_at: actual_time_or_pending
  selected_budgets: human_readable_policy_values
  target_and_fixture: verified_authorized_references
  scope_exclusions: explicit_list

claim:
  source_section: exact_section
  excerpt: short_exact_excerpt
  assertion: atomic_testable_claim
  classification: empirical_or_proposed_rule
  test_reference: actual_test_id
  result: pass_fail_blocked_not_testable_or_pending
  evidence: observed_safe_evidence_only

test:
  id: actual_test_id
  prerequisite: concrete_requirement
  expected: predefined_acceptance
  action: actual_action
  observed: actual_result
  result: pass_fail_blocked_not_testable_or_pending
  timestamp: actual_time_with_timezone
  duration: measured_human_readable_value_or_unmeasured
  evidence_reference: actual_reference_or_inline_observation
  retry_history: actual_attempts
  cleanup: verified_or_specific_blocker
```

Do not invent evidence links or screenshot attachments. Exclude passwords, cookies, tokens, sensitive URL parameters, unrelated tabs, and unnecessary personal information.

## Final report and maintenance

Write the run Page in editable Markdown with a summary, claim coverage matrix, test checklist, result ledger, timing samples, unknowns, draft guide corrections, and cleanup record. Preserve the distinction between completed execution and validated claims.

Read the latest Page before every update, preserve human edits, and verify saved changes. Do not edit the source guide automatically; present proposed corrections for approval. Do not schedule repeat runs merely because the prompt is saved.

If the run is interrupted, retain completed evidence, current URL and owned tab, unresolved effects, remaining tests, and the next safe action. On resumption, verify actual tab and source state before continuing.

## Current authorization context

The user requested this prompt Page and then requested creation of **dot.computer.tests** followed by browser tests on the cloud computer. That authorizes the present bounded, non-consequential run described above. It does not authorize stress testing, protected account actions, unrelated future runs, or changes outside the stated scope.
