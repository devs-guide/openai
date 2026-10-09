Browser-first operating guide for #AGENT on #COMPUTER, with tested capabilities, conservative work queues, and a verification log. **Status: ready for human review.** Ordinary cloud-browser interaction remains the default. The user permits narrow terminal and scripting exceptions for creating or improving browser automation on this cloud computer; those exceptions are recorded separately from browser-interface tests.

This Page is the editable working reference requested for future updates and verifications. It does not configure the browser or start scheduled work.

## Scope and evidence labels

- **#AGENT:** the assistant performing the requested browser work.

- **#DOT:** the application and runtime through which that work is requested.

- **#COMPUTER:** the cloud computer used in the tests.

- **#BROWSER:** its available cloud-browser interface.

- **CONFIRMED:** directly observed in the bounded tests below. Confirmation applies only to the stated action and conditions.

- **USER SUPPLIED OBSERVATION:** terminal output provided by the user. Its reported values and unit conversions are recorded with provenance; capture time, environment identity, current allocation and browser consequences are not independently confirmed by the paste.

- **UNAVAILABLE IN TEST:** a requested control returned an explicit capability-unavailable result.

- **UNTESTED:** no confirming execution or measurement was obtained.

- **PROPOSED RULE:** an operating convention for review, not a measured resource limit or proven performance improvement.

These labels are document conventions. The verification requirement is to keep empirical claims tied to test evidence, rather than label unmeasurable limits as confirmed.

## Browser verification record

**Test window:** October 8, 2026, from 7:14:46 p.m. to 7:16:06 p.m. UTC. Tests used the cloud-browser interface only. No shell, terminal, operating-system probe, raw network client, or browser launch command was used.

| Check | Result | Observed evidence |
| --- | --- | --- |
| Browser inventory | CONFIRMED | The cloud browser and its original tab appeared in the inventory. |
| Create a tab and navigate | CONFIRMED | Example Domain opened and returned readable accessibility state at 7:15:28 p.m. UTC after the authorized retry. |
| Follow an observed link | CONFIRMED | Clicking “Learn more” reached IANA’s Example Domains page in the same tab by 7:15:45 p.m. UTC. |
| Short sequential action batch | CONFIRMED | The link click and fresh accessibility-state read completed sequentially in one call. This is not a concurrency or throughput benchmark. |
| Screenshot observation | CONFIRMED | A rendered IANA page screenshot was returned by 7:15:51 p.m. UTC. |
| Read DOM and wait for a target | CONFIRMED | A DOM snapshot, a wait for the “Example Domains” heading to be visible, and a read of its rendered text succeeded by 7:16:01 p.m. UTC. No added fixed sleep was used. |
| Reuse the current tab | CONFIRMED | Navigation to the observed heading fragment changed the URL and returned updated accessibility state in the same tab. |
| Close temporary tabs | CONFIRMED | Both test-created tabs were closed. The final inventory contained only the original tab at 7:16:06 p.m. UTC. |
| Request a nonvisible tab | UNAVAILABLE IN TEST | The documented visible: false option returned “Capability is not available: visibility” at 7:14:50 p.m. UTC. |

The observed destination was [IANA Example Domains](https://www.iana.org/help/example-domains#example-domains). The test establishes these browser operations on simple public pages, not reliability on other sites. It was a one-time check; the example service is not a recurring test or monitoring target.

## Headless mode and ordinary tab fallback

**Headless launch control: UNTESTED and not exposed in the returned browser documentation.** No supported headless launch switch was available to exercise. The requested `--headless` behavior therefore cannot be marked confirmed or placed on the active execution path.

The failed visibility option does not establish that the existing browser is headless or headful. A successful DOM read or screenshot does not establish its launch mode either. A hidden tab and a headless browser must not be treated as interchangeable controls in this specification.

**Confirmed fallback:** ordinary cloud-browser tabs, using the tested accessibility or DOM reads, link interaction, state-based waits, and screenshot observations. Explicitly forcing a visible window or changing launch mode was not verified.

**Proposed conditional branch:** if a supported headless control becomes available later, run a small comparison against the ordinary-tab workflow before enabling it. Compare task-correct output, required content, interaction completion, authentication behavior when authorized, and recovery. Do not assume lower resource use or faster execution. If required evidence is missing, stop that path and inspect the ordinary tab. Reconcile any possible external action before repeating it.

### User reported data URL restriction

**USER SUPPLIED OBSERVATION:** on October 8, 2026, at approximately 8:47 p.m. UTC, the user reported that the exact URL `data:text/html, <html contenteditable>` was blocked.

The attempted surface, exact error message, and execution time were not supplied. No independent retry was performed. This establishes the reported outcome for that attempted URL, not a verified cause or a universal restriction covering every data URL.

Do not treat this data URL as an available editable-page test fixture. It does not complete the blocked input, state-change, or other fixture tests.

### Chrome version reference capture

**Reference status: user-supplied About Version text received; direct capture remains blocked.** On October 8, 2026, at 8:13:46 p.m. UTC, the cloud-browser navigation interface rejected `chrome://version/` because its URL policy permits HTTP and HTTPS. No direct About Version screenshot or text was captured by the assistant. The temporary blank tab was closed and cleanup verified. Later, the user supplied the version-page text at approximately 8:26 p.m. UTC; its capture time was not stated.

The browser inventory label and the supplied About Version record are separate evidence sources. The pasted record identifies Chromium and its reported configuration. Its matching version string agrees with the separately tested command-line binary, but does not prove that both observations concern the same running process or executable instance.

#### User supplied About Version facts

| Field | Supplied value | Scope |
| --- | --- | --- |
| Browser version | Chromium 154.0.8037.57 | Exact reported application version; not inferred from the user agent. |
| Build | Official Build, built on Debian GNU/Linux 13 trixie, x86_64 | “Official Build” is the supplied label; a release channel is not separately identified. |
| Operating system | Linux | As reported on About Version. |
| JavaScript engine | V8 15.4.80.11 | Reported engine version. |
| Revision | 73c14f6228d7cd537c855007e8f88678969cc0eb-refs/branch-heads/8037@{#1293} | Exact supplied identifier, retained without interpretation. |
| Executable path | /usr/lib/chromium/chromium | Reported location; no additional file inspection performed. |
| Profile path | /home/agent/.config/chromium/Default | Reported active profile location; not permission to read, copy, edit, or reuse it. |
| Requested window size | 1,364 by 1,024 | Command-line setting; not a measured content viewport or device-pixel ratio. |
| Variations source | command line or about flags | Supplied label only. |
| Encoded command-line variations | Truncated in the supplied text | Cannot reliably decode or reconstruct the missing content. |
| Active variation IDs | Opaque IDs supplied | No experiment meanings or effective feature behavior inferred. |

**Exact supplied user-agent string:**

```text
Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
```

The user-agent version is less specific than the About Version application version.

**Selected command-line observations:**

- No `--headless` token appears in the supplied command line. Record “no explicit headless flag shown,” rather than claim that a mode switch was tested.

- `--ozone-platform=x11` and the requested window size are present. They are configuration evidence, not an independently inspected window or measured viewport.

- `--remote-debugging-pipe` is present. This does not establish an available assistant connection or authorize taking over the pipe.

- `--user-data-dir` points to the reported Chromium configuration directory. This identifies a reported managed profile location, not a custom configuration destination.

- `--disable-gpu` and `--enable-gpu-rasterization` both appear. Effective hardware acceleration was not measured; do not resolve it from flag names alone.

- `--disable-dev-shm-usage` and `--force-color-profile=srgb` appear. Effective allocation and rendering behavior were not measured.

- A proxy setting, automation-related setting, disabled-feature list, and first-run/crash UI controls appear. The full managed command line is not provided here as a relaunch recipe; proxy details and opaque settings are not copied into new tests.

Version strings, identifiers, and paths retain their exact syntax. Their numbers are identifiers rather than capacity measurements.

#### User supplied local debugging metadata

**Source:** the user pasted a `curl http://localhost:9222/json/version` response on October 8, 2026, at approximately 8:37 p.m. UTC. The command execution time was not supplied. No request to this endpoint or connection to its debugger was made by the assistant.

| Returned field | Reported value |
| --- | --- |
| Browser | Chrome/154.0.8037.57 |
| Protocol-Version | 1.3 |
| V8-Version | 15.4.80.11 |
| WebKit-Version | 537.36, revision 73c14f6228d7cd537c855007e8f88678969cc0eb |
| User-Agent | Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36 |
| webSocketDebuggerUrl | A loopback WebSocket browser-debugging address was returned on port 9222. Its session-specific identifier is omitted from this reusable guide. |

**Recorded fact:** the pasted output reports a successful metadata response from that loopback endpoint in the user’s terminal context. Reachability from the assistant’s command or browser interfaces was not tested. “localhost” identifies the caller’s own network context; it is not a portable connection address across computers or execution contexts.

The browser version, V8 version, user agent, and revision agree with the corresponding previously supplied About Version fields. This is consistency between supplied records, not independent proof of process identity, headless mode, or ongoing availability.

The returned debugger address is not an instruction or authorization to connect, enumerate private tabs, inspect profiles, execute protocol commands, or bypass the browser interface’s URL restrictions. Protocol version 1.3 is a reported identifier, not a verified catalogue of usable commands. Do not treat the address as a persistent configuration value.

The command prompt’s `/workspace/.agents` location does not establish that this directory configures or controls the endpoint. No configuration file, listener setting, browser security setting, or debugging connection was changed.

#### Attached internal URL inventory

The attached **Pasted text.txt** was read in full. It contains a Chrome internal-URL catalog, not the About Version fields. This is a separate **USER SUPPLIED OBSERVATION**.

| Inventory category | Reported examples or text | Meaning for this guide |
| --- | --- | --- |
| Browser information and diagnostics | `chrome://version`, `chrome://gpu`, `chrome://system`, `chrome://policy`, `chrome://sandbox` | Names appear in the catalog; successful opening and assistant access were not demonstrated. |
| Settings and user-data pages | Settings, history, downloads, extensions, password and profile-related entries | Presence is not permission to inspect private data or change settings. |
| Internal debugging section | “Internal debugging pages are currently disabled.” | Preserve the section-specific statement; do not infer that every catalog URL is disabled. |
| Debug command section | The catalog warns that listed commands crash or hang the renderer; restart, quit, and memory-pressure entries also appear | Excluded from this non-destructive test plan. Catalog membership is not an instruction to open them. |
| Other internal schemes | `chrome-untrusted://` entries appear | Presence does not override the automation interface’s permitted URL schemes. |

The catalog is evidence of listed names and accompanying warnings only. It does not confirm availability, permissions, successful navigation, headless compatibility, GPU support, or the effectiveness of any setting. No URL in the attachment was opened as part of incorporating this reference.

#### User reported terminal launch

The user subsequently reported that running `chromium` from their terminal opened or reopened the browser for ordinary browser use. The pasted stderr contains repeated missing-system-D-Bus-socket messages and an unsuccessful UPower properties call.

**Recorded outcome: user-reported ordinary-browser launch succeeded despite those messages.** The log alone does not establish launch success; that outcome comes from the user’s accompanying observation. The provided command contains no explicit headless flag. No exit code, successful page-navigation trace, new-process verification, or proof of replacement of the existing process was supplied.

This does not contradict the assistant’s separate isolated headless attempts: those failed during process-singleton socket creation in their execution context. The reason the contexts behaved differently has not been established. Do not infer that D-Bus errors are always harmless, that installing D-Bus fixes the headless failure, or that a bare launch is a safe automated restart procedure. No relaunch was performed by the assistant in response to this report.

**Interpretation and reuse rules:**

- A version reference applies to the captured browser session and time, not every later session.

- Record current launch-mode evidence separately from whether the automation interface exposes a mode-switch control.

- The presence of a headless-related flag would be evidence of that reported launch configuration, not proof that the assistant can relaunch, switch modes, or create another session.

- The absence of a headless string alone is insufficient here to assert headed mode.

- Compare ordinary-tab and headless behavior only through a supported control, with matched workload and measured outcomes.

- A file under `/workspace`, a hardware feature, or a version number cannot substitute for the missing headless control.

- Do not prescribe launch flags, browser-version-specific workarounds, or compatibility guarantees before the relevant build and supported control are established.

### Limited command line exception and headless launch result

#### User reported package update failure

**USER SUPPLIED OBSERVATION:** received October 8, 2026, at approximately 8:49 p.m. UTC. The user supplied an attempted shell chain with three stages connected by `&&`: update package lists, install fontconfig, then launch a headless Chromium DOM dump to `page.html`.

The supplied output reports:

```text
W: Unable to read /etc/apt/apt.conf.d/80-applied-apt-retries - open (13: Permission denied)
E: List directory /var/lib/apt/lists/partial is missing. - Acquire (2: No such file or directory)
```

**Disposition: package-update stage failed.** In the displayed `&&` chain, failure of the update prevents the later installation and Chromium command from running. The output contains package-manager errors, not a Chromium launch result; a numeric command exit status was not supplied.

Consequently, this record does not establish:

- successful fontconfig installation, its prior presence or absence, or that it is required to solve the browser issue;

- whether the proposed D-Bus environment assignment affects Chromium;

- success or failure of the proposed headless, GPU, shared-memory, or image-loading options;

- Wikipedia access, DOM output, or the existence/content of `page.html`;

- a universal prohibition on all package operations or a network-failure cause.

The proposed, unreached Chromium stage included `--no-sandbox`. That is a security-weakening option, not a validated optimization or an approved default for this guide. It was not run by the assistant. No package installation, permission repair, privilege change, browser launch, or further retry was performed in response to this supplied fact.

**User direction, October 8, 2026:** browser interaction remains the default. Terminal and scripting have limited use cases for creating or improving browser automation on the cloud computer. The user specifically requested a command equivalent to `google-chrome-stable --headless=new --disable-gpu --dump-dom` against the Google Chrome Wikipedia article. This permitted an isolated command-line launch test; it did not authorize a new coding workflow, changes to the existing browser service, security weakening, or unrestricted terminal work.

**New observation:** the separately invoked installed executable was `/usr/bin/chromium`, reporting **Chromium 154.0.8037.57**. The command names `google-chrome-stable` and `google-chrome` were not found in the executable search. This identifies the tested command-line binary only; it does not establish the version of the existing browser automation session.

[Chrome’s official headless documentation](https://developer.chrome.com/docs/automation-and-testing/headless) describes launching Chrome with a headless command-line flag. Product documentation does not establish that this environment permits a new process to launch successfully.

**Equivalent command template for the attempted test, not a successful recipe:**

```bash
/usr/bin/chromium --headless=new --disable-gpu \
  --user-data-dir="<new-isolated-test-profile>" \
  --no-first-run --no-default-browser-check \
  --dump-dom https://en.wikipedia.org/wiki/Google_Chrome \
  > "<new-test-output-directory>/page.html"
```

Each attempt used a new task-specific profile and output directory. The angle-bracket paths above are placeholders for those separate locations; do not reuse the existing browser profile.

| Attempt | Observed result | Output |
| --- | --- | --- |
| Initial isolated launch | Aborted before navigation with SIGABRT after approximately one hundred seventeen milliseconds | page.html existed but was empty |
| One reviewed retry outside the command sandbox | Same startup failure after approximately one hundred fifteen milliseconds | Separate page.html also empty |

The fatal message was **“socket() failed: Operation not permitted”**, reported during process-singleton initialization. Earlier stderr also reported crashpad directory/database errors. The reviewed retry did not resolve the startup failure. These short elapsed durations measure failed process startup, not browser page loading.

**Conclusion:** isolated command-line headless startup is BLOCKED in the tested environment. Wikipedia navigation, DOM extraction, rendering correctness, headless resource use, and speed relative to ordinary tabs remain untested. An empty output file is not a successful dump.

No sandbox-disabling, certificate-bypass, or web-security-disabling flag was added. No dependencies were installed, no browser security settings were changed, and the existing browser profile/session was not used. Do not add security-weakening flags as a workaround for this result.

**Permitted planning pattern:** a narrow, explicitly scoped browser-automation diagnostic may use a separate process, a fresh profile, a bounded run, and retained evidence. Validate launch before interpreting navigation results; validate actual page content before treating a DOM file as successful. A terminal exception does not turn failed launches into a verified headless capability or automatically revise the browser-only test suite.

## Resource and capacity boundaries

Browser-only capability tests did not measure CPU allocation, RAM allocation, per-tab memory, disk capacity, network throughput, GPU capability, browser version, or process counts. At the user’s request, the following terminal observations are now included as a separate, explicitly attributed machine snapshot. They do not become browser-tested limits or authorize shell-based execution.

### User supplied machine observations

**Provenance:** terminal output supplied by the user on October 8, 2026, at approximately 8:10 p.m. UTC; workspace listing supplied at approximately 8:11 p.m. UTC. The command execution time was not included. These are **USER SUPPLIED OBSERVATIONS**, transcribed and interpreted here, not commands independently rerun by the assistant or browser performance tests. This distinction preserves the requested browser-only execution scope.

#### Processor snapshot

| Property | Reported value | Browser planning interpretation |
| --- | --- | --- |
| Architecture and modes | x86_64; thirty-two-bit and sixty-four-bit modes | Architecture reported by the operating system, not a verified browser build or launch capability. |
| Address sizes | Forty-six physical bits; forty-eight virtual bits | Address-width metadata, not installed RAM or an allocation allowance. |
| Byte order | Little Endian | Representation metadata; no concurrency implication. |
| Online logical CPUs | Nine, numbered zero through eight | Visible CPU count; dedicated cores and enforced CPU quota remain unknown. |
| Vendor and model | AuthenticAMD; AMD EPYC 9V74 80-Core Processor | Preserve the model string. “80-Core” does not mean eighty cores are allocated to this session. |
| Reported topology | One thread per core; nine cores per socket; one socket | Reported topology only; not independently verified physical-host topology. |
| Family, model and stepping | Family twenty-five; model seventeen; stepping one | Identification metadata, not browser performance measurements. |
| BogoMIPS | 5,192.27 | Kernel calibration value; do not treat as browser operations per second. |
| Selected reported flags | hypervisor, aes, avx, avx2, avx512f, avx512_bf16 | Reported CPU features, not proof of browser use, speed, compatibility, or headless availability. |

The [upstream lscpu manual](https://github.com/util-linux/util-linux/blob/master/sys-utils/lscpu.1.adoc) documents the reported CPU/topology information and cautions about virtualized environments. [Linux calibration code](https://raw.githubusercontent.com/torvalds/linux/master/init/calibrate.c) identifies the calibration context for BogoMIPS.

#### Memory snapshot

The pasted `free -m` values use mebibytes. Readable conversions below are rounded, not new measurements.

| Field | Reported value in readable units |
| --- | --- |
| Total usable memory | Approximately 9.73 GiB |
| Used | Approximately 1.72 GiB |
| Free | Approximately 8.06 GiB |
| Available | Approximately 8.01 GiB |
| Shared | Thirty-three MiB |
| Buffers and cache | Two hundred forty-two MiB |
| Swap total, used and free | Zero |

Modern procps defines “used” as total minus available; the supplied values match that calculation. These fields are not all independent buckets that can be added together. “Available” is an estimate for new applications without swapping, not a reservation for browser tabs. The command version was not supplied. See the [upstream free manual](https://github.com/procps-ng/procps/blob/master/man/free.1).

**Planning rule:** do not divide the reported available memory by an invented per-tab allowance. Current per-tab memory, the browser’s enforceable memory ceiling, other workloads, and future available memory are unmeasured. With no reported swap, do not assume swap provides a fallback for memory pressure.

#### Filesystem snapshot

The pasted `df -h` uses rounded, power-of-two human-readable units. The displayed capacities are filesystem reports, not guarantees of durability, write permission, or browser storage allocation. See [GNU df documentation](https://www.gnu.org/s/coreutils/manual/html_node/df-invocation.html).

| Mount reported by the user | Type | Displayed size | Displayed used | Displayed available | Displayed utilization |
| --- | --- | --- | --- | --- | --- |
| / | tmpfs | About 4.9 GiB | About 1.2 MiB | About 4.9 GiB | One percent |
| /usr | overlay | About thirty-two GiB | About one hundred fifty MiB | About thirty GiB | One percent |
| /dev | tmpfs | About 4.9 GiB | Zero | About 4.9 GiB | Zero percent |
| /dev/tty | tmpfs | Sixty-four MiB | Zero | Sixty-four MiB | Zero percent |
| /dev/shm | tmpfs | About 4.9 GiB | Zero | About 4.9 GiB | Zero percent |
| /tmp | tmpfs | About 4.9 GiB | Zero | About 4.9 GiB | Zero percent |
| /run | tmpfs | About 4.9 GiB | Zero | About 4.9 GiB | Zero percent |
| /dev/shm/codex-orbit-desktop | shm | About 4.9 GiB | About 3.2 MiB | About 4.9 GiB | One percent |

Repeated tmpfs capacities must not be added as independent RAM allocations. Their contents use memory-backed storage; mount ceilings do not reserve that amount in advance. Temporary files can therefore compete with application memory. The sixty-four-MiB row belongs to `/dev/tty`, not `/dev/shm`. This capture does not support assuming a sixty-four-MiB shared-memory limit. See [Linux tmpfs documentation](https://kernel.org/doc/html/v6.10/filesystems/tmpfs.html).

**Planning rule:** avoid accumulating unnecessary downloads, screenshots, or temporary profiles. Do not relocate browser profiles or caches, change shared-memory behavior, or introduce browser flags on the strength of this listing. No storage-path change is authorized or tested here.

#### Workspace entries and possible configuration records

The user’s `ls -a` output at `/workspace` names `.agents`, `.codex`, `.git`, `library-files`, `scratch`, and `shared`, plus the ordinary current/parent entries `.` and `..`. No entry contents, file types, permissions, ownership, or persistence were inspected.

| Candidate or observed name | Evidence and allowed interpretation |
| --- | --- |
| /workspace/.agents | Listed; plural spelling. Purpose and any configuration consumer are unverified. |
| /workspace/.codex | Listed. No browser configuration loading or permission to modify it is established. |
| /workspace/.git | Listed. No browser settings role is established. |
| /workspace/library-files | Listed. Storage behavior, scope and persistence are unverified by this listing. |
| /workspace/scratch | Listed; a possible location for an explicitly requested task artifact only after access is verified. |
| /workspace/shared | Listed; no sharing audience or durable-storage guarantee is inferred from the name. |
| .agent and .history | Not present in the supplied workspace listing. Existence elsewhere, creation permission, and any loader remain unverified. |
| .config | Not shown under /workspace. The later About Version text reports /home/agent/.config/chromium as its profile root; write permission and custom configuration loading remain unverified. |

**Proposed artifact names only:** `browser-session.yaml`, `browser-test-results.md`, and `browser-checkpoint.md`. These would be task records, not automatically loaded settings. A configuration becomes operational only when its actual consumer, supported schema, exact destination, permissions, and successful loading are verified. Do not repurpose a listed hidden entry or use a filename to infer a startup hook.

No local configuration file was created, read, or modified for this update. The editable Page remains the established documentation location. Shell history is not a suitable assumed configuration store.

#### Resource based browser policy

The supplied snapshot supports describing a nine-logical-CPU environment with approximately 9.73 GiB of reported usable RAM and approximately 8.01 GiB available at capture time. It does not establish nine concurrent browsers, a particular number of safe tabs, or a guaranteed memory allowance.

Retain the proposed one-active-item queue, tab reuse, short sequential batches, state-based waits, and cleanup. Increase concurrency or batch size only after an accessible representative workload provides evidence within a separately bounded test. These rules are conservative choices, not proven optimal settings.

**Headless consequence:** none of the CPU, memory, filesystem, or workspace-entry outputs establishes an installed Chrome version, actual launch mode, a supported mode-switch control, or a headless memory/speed advantage. Do not add `--headless` to the active execution plan solely from these observations.

| Requested limit | Verified value |
| --- | --- |
| Maximum simultaneously open tabs | UNTESTED |
| Maximum safe parallel browser actions | UNTESTED |
| Optimal batch size | UNTESTED |
| Safe requests per minute | UNTESTED |
| Sustained task throughput | UNTESTED |
| Browser memory ceiling or overload threshold | UNTESTED |
| Session lifetime or idle timeout | UNTESTED |
| Persistence after browser or environment restart | UNTESTED |
| Account-wide concurrent chats or computer sessions | UNTESTED |
| Active context capacity or history retention | UNTESTED |

No numeric maximum is inferred from the successful small test. There is no verified “fully optimized” configuration or guarantee against overload. The policies below deliberately limit concurrent work without claiming that those limits are platform maxima.

## Conservative queue and batching policy

**Proposed rules for review:**

- Operate one task tab at a time. Reuse that tab for sequential pages when the workflow permits.

- Keep a single active queue item. Leave later items queued until the current item is verified, blocked, or explicitly skipped.

- Start with one logical interaction followed by a fresh state check. The successful link-click-and-read test is the demonstrated pattern.

- Group only short actions whose inputs and targets have already been observed and whose order is known. Await each action before the next.

- End the batch before any step that depends on newly discovered page content, a navigation outcome, a warning, a login, or a permission decision.

- Do not issue competing navigations, clicks, or writes against the same tab.

- Keep source URL, intended action, expected result, observed result, and completion state with each queue item.

- Close only task-created temporary tabs, after preserving the evidence needed for the result. Do not close unrelated tabs.

**Confirmed scope:** short sequential batching and tab reuse worked in the test. A larger batch, multiple active tabs, or parallel jobs was not benchmarked. “One” is the proposed starting policy, not a discovered browser limit.

## Readiness cues and pacing

**Confirmed cue:** the target heading becoming visible was successfully used before reading its text.

**Proposed rules:** use the expected page state as the primary completion condition. After a navigation or interaction, inspect the returned URL and relevant content. For a form or other consequential operation, require the specific result that establishes success; a generic page load is insufficient.

Readiness signals such as a button becoming enabled, a dialog closing, a result row appearing, or a spinner disappearing remain site-specific and untested here. Verify whichever signal a future task relies on.

Do not use an arbitrary delay as proof of completion. No optimal fixed delay was measured. If a tool exposes a timeout, choose it from the task’s deadline and observed site behavior, and label it as a selected budget. Do not present that budget as the platform’s timeout limit.

**Backpressure policy:** stop adding work when a state check fails, a permission prompt appears, the page stops responding, or a result is ambiguous. Preserve the queue and inspect the current tab before retrying. Slow responses alone do not identify CPU or memory exhaustion. Do not launch extra tabs to compensate for an unexplained slowdown.

## Choosing text inspection or screenshots

Accessibility state, DOM snapshot inspection, and screenshots all succeeded on the tested pages.

**Proposed selection rule:** inspect text and controls through the available accessibility or DOM representation when that is sufficient to answer the task. Use a screenshot when layout, visual appearance, missing controls, or a mismatch between text and rendered state matters.

This is an evidence-selection policy. The test did not measure whether either representation uses less browser memory, bandwidth, time, or context. Do not claim a quantified efficiency gain. Reinspect after changes instead of acting on stale element references or old images.

## Failure handling and cleanup

**Observed recovery:** the first ordinary navigation encountered a dismissed permission check. After authorization was clarified, the same action was retried once and succeeded. The first attempt had left a blank test tab; it was found and closed during cleanup. This result does not authorize retries after a denial or prove that every failed navigation leaves no state behind.

**Proposed handling:**

- Missing capability: stop using that control and report its exact unavailable status.

- Unexpected page state: stop the batch, obtain fresh state, and rebuild only the remaining actions.

- Permission or authentication requirement: pause dependent work and obtain the required user action. Do not try to bypass it.

- Possible external side effect: verify destination state before a repeat submission, purchase, message, upload, or edit.

- Suspected overload: stop queue dispatch; inspect current state; preserve results; close only unnecessary task-owned tabs when safe. Resource-pressure recovery remains untested.

- Rate-limit or service error: follow the actual service response. No requests-per-minute allowance or universal retry interval is assumed.

No forced restart of the existing browser, cache deletion, cookie clearing, settings change, installation, or security-weakening launch flag is included in the default browser profile. Separately authorized isolated command-line diagnostics are documented in the limited-exception section.

## Browser task contract

The following YAML is a human-reviewable specification, not an executable configuration. Human-readable quantities are strings; a future implementation must validate and convert them explicitly. Placeholders are required inputs, not operational defaults.

```yaml
profile: browser_first_with_narrow_explicit_exceptions
review_status: required
execution_surface: cloud_browser
shell_and_terminal: limited_to_explicit_browser_automation_tasks
native_app_automation: excluded
raw_network_clients: excluded
browser_launch_commands: isolated_explicit_tests_only
headless_control: not_verified
ordinary_tab_workflow: confirmed_on_simple_public_pages

resource_reference:
  evidence_class: user_supplied_terminal_observation
  capture_time: not_supplied
  visible_logical_cpus: nine
  reported_total_memory: "approximately 9.73 GiB"
  reported_available_memory: "approximately 8.01 GiB at capture"
  reported_swap: zero
  guaranteed_browser_allocation: unknown
  safe_parallel_tab_count: unmeasured
  tmpfs_capacities_additive: false
  workspace_config_consumer: unverified

browser_version_reference:
  direct_capture_status: blocked_by_navigation_protocol_policy
  supplied_reference: user_pasted_about_version
  reported_session_version: "Chromium 154.0.8037.57"
  reported_javascript_engine: "V8 15.4.80.11"
  reported_launch_flags: no_explicit_headless_token
  internal_url_inventory: user_attachment_read
  separately_invoked_binary: "Chromium 154.0.8037.57"
  isolated_headless_launch: blocked_before_navigation
  actual_launch_mode: not_independently_verified
  ordinary_terminal_launch: user_reported_success
  headless_mode_switch: not_exposed_in_inspected_interface

task:
  goal: REQUIRED
  starting_url: REQUIRED
  authorized_scope: REQUIRED
  expected_result: REQUIRED
  completion_evidence: REQUIRED
  stopping_condition: REQUIRED

queue_policy:
  classification: proposed_rule
  active_items: one
  actively_operated_task_tabs: one
  order: sequential
  starting_batch: one_logical_interaction_then_fresh_state
  parallel_dispatch: disabled
  next_item_requires: current_item_verified_or_explicitly_resolved

readiness:
  confirmed_signal: observed_heading_visible
  site_specific_signal: REQUIRED_WHEN_DIFFERENT
  fixed_delay_optimum: untested
  timeout_budget: REQUIRED_IF_A_TIMEOUT_IS_NEEDED

headless_branch:
  enabled: false
  enable_when: supported_control_and_task_specific_comparison_pass
  fallback: ordinary_tab_inspection
  before_repeating_side_effect: verify_destination_state

evidence:
  record: action_target_result_time_and_scope
  durations: seconds_or_minutes_with_units
  capacities: human_readable_units_only_when_measured
  unknowns: explicitly_unverified

cleanup:
  preserve_results_first: true
  close_task_created_temporary_tabs: true
  close_unrelated_tabs: false
```

## Queue record and resumable checkpoint

**Proposed states:** QUEUED → INSPECTING → ACTING → VERIFYING → COMPLETE. Use WAITING for an identified pending condition, BLOCKED for missing access or a required decision, and FAILED only with an explicit unresolved outcome. WAITING and BLOCKED are not completion.

```yaml
checkpoint:
  task_goal: REQUIRED
  source_page: REQUIRED
  last_verified_url: REQUIRED
  last_verified_page_state: REQUIRED
  current_queue_item: REQUIRED
  completed_items: []
  remaining_items: []
  evidence_references: []
  uncertain_external_actions: []
  blocker: none_or_specific_blocker
  next_safe_action: REQUIRED
  resume_checks:
    - verify_browser_and_tab_still_exist
    - reread_current_page_state
    - verify_source_and_task_scope_are_current
    - reconcile_any_uncertain_external_action
  excluded_data:
    - passwords
    - authentication_tokens
    - cookies
    - unnecessary_personal_information
```

Browser-session persistence and complete cross-session recall were not tested. The checkpoint is therefore a proposed recovery record, not a guarantee that a tab, login, source, or earlier conversation will remain available.

## Capabilities requiring separate tests

Authentication, file downloads, file uploads, form submission, rich web applications, cross-site workflows, browser extensions, multiple simultaneous tasks, headless execution, rendering equivalence, sustained throughput, and recovery under resource pressure are **UNTESTED**.

Before depending on one of these capabilities, define a small task-specific test with an authorized destination, expected result, evidence, and stopping condition. Avoid stress tests or repeated public-site probing as a substitute for a measured capacity specification. A successful test on one application does not establish support for another.

## Verification and update procedure

**Proposed maintenance procedure:**

- Read the latest Page before changing it and preserve unrelated human edits.

- Identify the exact claim to verify, its current evidence, and the smallest safe test.

- Record the date and time, browser surface, target, observed result, and limits of the observation.

- Mark successful observations CONFIRMED only within their tested scope. Keep proposed operating rules separate.

- Record failed or unavailable checks without converting them into universal product limitations.

- Replace a factual claim when new evidence supersedes it and append a concise change entry.

- Require explicit review before treating a changed operating profile as adopted. Page edits do not create scheduled verification jobs.

## Change history

**October 8, 2026, package-stage failure:** Added the user’s package-manager errors and the shell-chain stopping condition. Recorded that the later installation and headless stage were not tested by this output; no browser capability or test result was promoted.

**October 8, 2026, data URL observation:** Added the user-reported block of `data:text/html, <html contenteditable>`, with exact scope and missing context preserved. No retry or test-status promotion occurred.

**October 8, 2026, local metadata reference:** Added the user-supplied loopback browser-version response, matching version fields, and source-context limitations. Omitted the session-specific debugger identifier. No endpoint or debugger connection was attempted.

**October 8, 2026, supplied browser references:** Added the user’s About Version text, separately read internal-URL inventory, and reported successful ordinary terminal launch despite D-Bus errors. Updated version-reference and profile-location facts while retaining provenance, the direct-capture restriction, and the separate failed headless-test evidence. No internal URL, live profile, debugging connection, or browser setting was operated.

**October 8, 2026, command-line exception:** Recorded the user’s browser-first preference with narrow terminal/scripting exceptions. Tested a separately invoked Chromium binary twice using isolated profiles, including one reviewed retry. Both attempts failed before navigation; no successful headless DOM or performance result was obtained. Existing browser-interface findings remain separate.

**October 8, 2026:** Created the browser-only working Page from the new capability tests and the requested operating scope. Added verification results, a headless-control gap, ordinary-tab fallback, sequential queue policy, readiness cues, and recovery records. Excluded earlier shell-derived specifications from browser capacity claims.

**October 8, 2026, later update:** Added user-supplied CPU, memory, filesystem and workspace observations with human-readable units and source qualification. Added browser-planning implications without inventing per-tab allowances or concurrency limits. Recorded the blocked Chrome About Version capture, verified temporary-tab cleanup, pending reference fields, and the continued absence of a verified headless-switch control. No local files, configuration or browser settings were changed.

## Human review

- [ ] Review the proposed one-active-item and one-task-tab starting policy.

- [ ] Review the evidence boundaries and untested capabilities.

- [ ] Supply an actual target application before task-specific tuning.

- [ ] Define that task’s result, authorized actions, and stopping condition.

- [ ] Review the operating profile before adoption.

No maximum capacity, optimal throughput, guaranteed persistence, or headless capability has been established.
