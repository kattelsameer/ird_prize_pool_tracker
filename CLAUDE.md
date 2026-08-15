# Master Autonomous Engineering Specification

## Nepal IRD Prize Pool Consumer Tracker

> **Document purpose:** Authoritative instruction set for autonomous development. Source of truth for product intent, engineering process, testing, Git workflow, and definition of done.

---

## Quick Navigation & Table of Contents

### Core Sections

* **[§1 Executive Objective](#1-executive-objective)** — Product vision and success criteria
* **[§2–5 Key Principles](#2-critical-operating-principle)** — Operating philosophy and decision framework

### Product & Domain (§6–10e)

* **[§6 Product Background](#6-product-background)** — Consumer tracking application, data distinctions
* **[§7 Government Website Research](#7-government-website-research)** — IRD system overview
* **[§8 Government API](#8-actual-government-api)** — Official data-fetch request and integration
* **[§9 Research Deliverable](#9-research-deliverable)** — Domain findings structure
* **[§10 Product Name](#10-product-name)** — Naming conventions and project setup
* **[§10a Domain Context](#10a-domain-context-the-nepal-ird-prize-pool-system)** — Nepal IRD Prize Pool system details
* **[§10b Fiscal Year System](#10b-nepal-fiscal-year--calendar-system)** — Bikram Sambat calendar and FY mechanics
* **[§10c Data Structures](#10c-prize-pool-data-structures--terminology)** — API response and coupon formats
* **[§10d Regulatory & Compliance](#10d-regulatory--compliance-considerations)** — Privacy laws and data handling
* **[§10e Implementation Decisions](#10e-implementation-decision-framework)** — Q&A for common ambiguities

### Engineering & Architecture (§11–46)

* **[§11–18 Git & Development Workflow](#11-repository-initialization)**
  * [§11 Repository Initialization](#11-repository-initialization)
  * [§12–14 Branching & Git Strategy](#12-git-branching-strategy)
  * [§15–18 Feature & Integration Gates](#15-feature-development-gate)

* **[§19–46 Architecture, Data Models & UI](#19-architecture)**
  * [§19 System Architecture](#19-architecture)
  * [§20–21 Frontend & Backend](#20-frontend)
  * [§22–28 Database & Data Models](#22-database)
  * [§29–36 Matching Engine, Dashboard, Explorer](#29-matching-engine)
  * [§37–43 Sync, API & Error Handling](#37-synchronization-architecture)
  * [§44–46 UX & Accessibility](#44-ux-principles)

### Testing, Docker & Release (§48–79)

* **[§48–54 Testing Strategy](#48-testing-philosophy)** — Philosophy, backends, frontend, E2E, integration
* **[§55–60 Docker & Deployment](#55-docker)** — Containerization, testing, build strategy
* **[§61–72 Release & Verification](#61-documentation)**
  * [§61–62 Documentation & Development Sequence](#61-documentation)
  * [§63–72 Agent Coordination & Acceptance Criteria](#63-agent-coordination)
* **[§73–79 Final Release Process](#73-final-release-process)** — Release gates, verification, completion

---

## Phase Checklist

Track progress through these major phases:

* [ ] **Phase 1**: Research (§7-9)
* [ ] **Phase 2**: Product/Architecture planning (§19-46)
* [ ] **Phase 3**: Repository setup (§11)
* [ ] **Phase 4**: Backend foundation
* [ ] **Phase 5**: Government integration
* [ ] **Phase 6**: Matching engine
* [ ] **Phase 7**: Coupon management
* [ ] **Phase 8-11**: Dashboard, notifications, explorer, settings
* [ ] **Phase 12-14**: Testing, integration, Docker
* [ ] **Phase 15**: Release to master
* [ ] **Phase 16**: Final documentation

---

## Critical Rules (Quick Reference)

**§69 — Timezone:** Always use `Asia/Kathmandu` for Nepal-local logic. Test midnight/boundaries/fiscal-year transitions.

**§70 — Fiscal Year:** Nepal fiscal years (e.g., `2083-84`) are NOT calendar years. Understand IRD's association before implementing matching.

**§65 — Language:** Distinguish "coupon matches published data" from "consumer is guaranteed a prize." Use careful language.

**§66 — Data Integrity:** Store raw source data + normalized data + source identifiers for traceability. This enables debugging and future API changes.

**§67 — API Design:** Use an adapter layer between IRD responses and internal models. Reduces blast radius if IRD API changes.

**§68 — Sync Failures:** Retain existing data, record failure, expose status, log error, retry where appropriate. Never delete data on sync failure.

---

## 1. Executive Objective

Build a complete, production-quality web application that helps consumers in Nepal track their purchase coupons and determine whether those coupons match prize-pool results published by the Nepal Inland Revenue Department (IRD).

The application should obtain prize-pool information from the actual IRD system, store and normalize that information locally, allow a consumer to enter and manage their own coupons, and automatically determine whether their coupons match published prize-pool records.

The application must provide an excellent user experience around the most important question:

> **“Do any of my coupons have a result that I need to act on?”**

This is an **implementation task**, not a design exercise.

The expected outcome is:

> **A working, tested, Dockerized application running from the project directory on the local machine.**

Do not stop at research, planning, scaffolding, or partial implementation.

---

## 2. Critical Operating Principle

### You are responsible for the entire engineering lifecycle

Act as a coordinated team consisting of:

* Product researcher
* Product manager
* UX/UI designer
* Software architect
* Frontend engineer
* Backend engineer
* Database engineer
* Integration engineer
* QA engineer
* Automation/E2E engineer
* DevOps engineer
* Security reviewer
* Technical writer

You may use multiple agents/subagents internally when useful.

Agents should have **clear responsibilities and boundaries**.

For example:

```text
Research Agent
    ↓
Architecture Agent
    ↓
Backend Agent
    ↓
Frontend Agent
    ↓
Integration Agent
    ↓
QA Agent
    ↓
Release/DevOps Agent
```

Agents should not independently redefine product requirements.

The main agent remains responsible for:

* coordinating work
* resolving conflicts
* reviewing agent output
* ensuring consistency
* running final integration
* verifying the final product

---

## 3. Autonomous Execution

### 3.1 Make decisions, don't wait for approval

Decide architecture, schema, UI, frameworks, branch names, test strategy, implementation order independently. Only ask if the decision is impossible without user input.

Use research and engineering judgment.

### 3.2 Resolve ambiguity with this priority

1. Actual IRD system/government data behavior
2. Explicit requirements in this spec
3. Standard software engineering practices
4. Simplest maintainable solution
5. Document the assumption

**Do not stop work because something is ambiguous** — research and decide.

---

## 4. Required vs Flexible Decisions

### Must implement

React, FastAPI, SQLite (initially), Docker, IRD integration, daily sync, Nepal timezone, coupon CRUD, matching, dashboard, notifications, settings, search/filter, tests, E2E, Git workflow (feature/bugfix branches, `master` stable, `develop` integration).

### Decide yourself (after research)

Component libraries, CSS framework, state management, API clients, ORM details, exact schema, route names, scheduler tech, Docker topology, test libraries, folder structure, design system, notification implementation.

**Principle:** No complexity for its own sake.

---

## 5. Source of Truth (priority order)

1. Actual IRD behavior/data (most authoritative)
2. This specification
3. Verified implementation findings
4. Established software engineering practices
5. Reasonable assumptions

**If IRD contradicts this spec → adapt the implementation and document it. Never fabricate data.**

---

## Product Definition (Sections 6–10e)

---

## 6. Product Background

The application is an **independent consumer tracking application**.

It is not intended to replace the IRD system.

It should consume and organize publicly available government prize-pool information and compare it with information entered by the consumer.

The application should clearly distinguish:

### Government data

Information obtained from the IRD source.

### User data

Information entered by the consumer.

### Application-derived information

Examples:

* matched
* not matched
* claim approaching
* claim expired
* notification generated

This distinction is important for user trust.

---

## 7. Government Website Research

Government website:

[https://prize.ird.gov.np](https://prize.ird.gov.np)

Before coding, study the site thoroughly enough to understand the domain.

Research:

* purpose of the prize pool
* coupon structure
* prize structure
* transaction periods
* prize-pool periods
* fiscal-year conventions
* network/payment-provider terminology
* winning-record structure
* claim periods
* claim deadlines
* publication timing
* any additional consumer-facing information
* how the government site displays results
* any relevant API endpoints
* network requests made by the site
* pagination/filtering behavior
* response structure

Do not assume the website's visible HTML contains all the information.

Inspect the actual API/network behavior where appropriate.

---

## 8. Actual Government API

The government data-fetch request will be supplied here:

```bash
curl 'https://prize.ird.gov.np/api/v1/public/winners?limit=6&offset=0' \
  -H 'Accept: */*' \
  -H 'Accept-Language: en-US,en;q=0.9,de;q=0.8,ca;q=0.7,th;q=0.6' \
  -H 'Connection: keep-alive' \
  -b '_ga=GA1.1.1478837941.1786435100; _ga_CK0L6TF2HX=GS2.1.s1786435100$o1$g1$t1786435272$j21$l0$h0; TS99c56678027=08aec0fa41ab2000b8c89d3280b99764bc304cb13019e8b9034de2603f129f119d2888d0638fdd760879086e411130007154fa092a784c3788b568fb6bc9aa826f3f5c921b525ddf055cd74435d882c5f0fe12622f87160ad9396ee8a18af553' \
  -H 'Sec-Fetch-Dest: empty' \
  -H 'Sec-Fetch-Mode: cors' \
  -H 'Sec-Fetch-Site: same-origin' \
  -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36 OPR/134.0.0.0' \
  -H 'sec-ch-ua: "Not;A=Brand";v="8", "Chromium";v="150", "Opera";v="134"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "macOS"'
```

The implementation must be based on the actual request and response.

The backend should encapsulate this integration behind a dedicated service.

For example conceptually:

```text
IRD API
   ↓
IRD Client
   ↓
Response Validation
   ↓
Normalization
   ↓
Persistence
   ↓
Matching Engine
```

Do not allow IRD-specific response structures to leak throughout the application.

---

## 9. Research Deliverable

Before significant implementation, produce an internal research summary containing:

### A. Domain understanding

What the IRD prize pool actually represents.

### B. Data model

What information IRD actually publishes.

### C. Matching rules

Exactly how a user coupon can be considered a match.

### D. Date logic

How transaction dates relate to prize-pool periods.

### E. Fiscal-year logic

How fiscal years are represented and used.

### F. Claim logic

How claim validity/deadline information works.

### G. Network logic

Whether network/provider affects matching.

### H. API behavior

Request format, response format, pagination, errors, and limitations.

### I. Risks

Potential data quality and integration problems.

### J. Product improvements

Anything the consumer would need that was not explicitly mentioned in this specification.

Then use these findings to refine implementation.

---

## 10. Product Name

After research, choose a professional product/project name. Current Suggestion : Nepal IRD Prize Pool Consumer Tracker

The name should:

* be memorable
* be consumer-friendly
* describe the product reasonably well
* not falsely imply government ownership
* not imply official IRD endorsement

---

## 10a. Domain Context: The Nepal IRD Prize Pool System

The application integrates with Nepal's **Taxpayer Incentive Gift Program** (करदाता प्रोत्साहन उपहार कार्यक्रम), operated by the Inland Revenue Department (IRD) under the Ministry of Finance.
> You may add these info in certain section in the web app. A a information Page with all the detail as ell as you have described here.. with proper links and processes

### Program Overview

**Purpose:**

* Incentivize tax compliance and invoice collection
* Build culture of formal transactions
* Increase market transparency
* Promote digital payment adoption
* Reward ordinary consumers for demanding bills

**Launch Date:** Shrawan 21, 2083 (August 7, 2026)

**Status:** Active; first draw announced with 16 winners (15 daily + 1 bumper prize)

### Prize Structure

**Draw Schedule:**

Draws occur **every 1st and 16th of the Nepali calendar month**.

Each fortnightly draw awards:

* 15 daily-prize winners
* 1 bumper-prize winner

**Prize Tiers:**

| Category | Frequency | Individual Prize | Net After Tax |
| ---------- | ----------- | ------------------ | ---------------- |
| Daily Prize | Every draw | Rs 133,334 | Rs 100,000 (25% tax) |
| Bumper Prize | Every draw | Rs 1,000,000 | Rs 750,000 (25% tax) |

**Odds:** Random selection from all eligible coupons; purchase amount does **not** affect odds (Rs 100 bill = Rs 50,000 bill in terms of winning probability).

### Coupon Entry Methods

**Two parallel pathways:**

**1. Digital Transactions (Automatic)**

* Transactions via QR codes, mobile wallets, or bank transfers automatically generate coupons
* Supported platforms: eSewa, Khalti, IME Pay, bank mobile apps
* IRD verifies against merchant PAN records automatically
* No consumer action required
* Auto-enrolled from Shrawan 1, 2083 onward

**2. Cash Purchases (Manual Entry)**

* Consumer buys goods/services in Nepal for personal use
* Minimum transaction value: Rs 100+
* Consumer obtains original paper invoice
* Consumer manually registers bill at prize.ird.gov.np
* **Requires original physical bill for claim verification** (no photocopies accepted)

**Critical Implementation Detail:** These two pathways create parallel data pipelines. Deduplication logic must handle the same coupon potentially appearing in both digital and manual entry systems.

### Claim Process

**Claim Window:** Exactly **15 calendar days** from draw announcement date

**Claim Method:** **In-person only** at designated Inland Revenue Office (no online claims)

**Required Documentation:**

1. Original physical invoice (bill) — **photocopies not accepted**
2. Official government photo ID (citizenship, national ID, passport, or driving license)
3. Valid Personal Account Number (PAN) — **mandatory**
4. Bank account details (account number and bank name for prize deposit)

**Tax Treatment:**

* Daily winner: Rs 133,334 → net Rs 100,000 (25% contingency profit tax)
* Bumper winner: Rs 1,000,000 → net Rs 750,000 (25% tax)
* Processing time: 3-7 working days after claim submission

**If claim deadline expires:** Prize goes permanently to Prime Minister's Disaster Relief Fund (no reclaim possible).

**Implication for application:** Must calculate and prominently display claim deadline countdown. Flag approaching deadlines (e.g., "3 days remaining"). This is a hard deadline with permanent loss consequence.

### Data Quality Realities

**Identified challenges:**

| Issue | Impact |
| ------- | -------- |
| Dual entry methods | Auto-digital + manual-cash coupons in same system; inconsistent data pathways |
| Portal validation gaps | System accepts bills outside correct draw window without validation |
| Manual entry errors | Consumers may enter wrong dates, codes, or amounts |
| Invoice mismatch | Physical bill required for claim even for auto-digital entries; system of record split |
| Code format inconsistency | Codes may have whitespace, case variations, padding differences |
| Missing field values | Not all prize records contain all fields (network, category details, etc.) |

**Application strategy:** Store both raw IRD response and normalized data. Preserve original values for audit trail. Gracefully handle sparse data.

---

## 10b. Nepal Fiscal Year & Calendar System

**Critical understanding required:** Nepal does **not** use the Gregorian calendar for fiscal purposes. Fiscal-year matching logic depends on correct calendar conversion and date handling.

### Bikram Sambat Calendar

**Calendar System:** Bikram Sambat (BS) — lunar-solar calendar traditional to Nepal

**Offset:** Nepal's Bikram Sambat is approximately **56 years and 8.5 months ahead** of the Common Era (AD/CE)

**Conversion:** Gregorian 2026 ≈ Bikram Sambat 2083

### Nepal Fiscal Year Format

**Representation:** `YYYY-YY` in Bikram Sambat (e.g., `2083-84`)

**Fiscal Year Dates:**

* **Starts:** Shrawan 1 (mid-July, Gregorian)
* **Ends:** Ashadh 31 (mid-July following year, Gregorian)
* **Example:** FY 2083/84 = July 17, 2026 to July 15, 2027

### Nepali Calendar Months

For prize-pool and transaction-period logic:

| Nepali Month | Gregorian Equivalent | BS Month # |
| -------------- | --------------------- | ----------- |
| Shrawan | July-August | 1 |
| Bhadra | August-September | 2 |
| Ashwin | September-October | 3 |
| Kartik | October-November | 4 |
| Mangsir | November-December | 5 |
| Poush | December-January | 6 |
| Magh | January-February | 7 |
| Falgun | February-March | 8 |
| Chaitra | March-April | 9 |
| Baisakh | April-May (Nepali New Year) | 10 |
| Jyestha | May-June | 11 |
| Ashadh | June-July | 12 |

### Critical Implementation Requirements

**1. All date/time logic MUST explicitly use:**

* Timezone: `Asia/Kathmandu`
* Calendar: Bikram Sambat (not Gregorian)
* Fiscal year: In BS format (`2083-84`), not calendar year

**2. Test the following boundary cases:**

* Mid-July transition between fiscal years
* Exact fiscal-year boundary dates
* Nepali month boundaries
* Date near Nepali New Year (mid-April)
* Asia/Kathmandu midnight (±timezone offset from UTC)

**3. Do not:**

* Assume system locale is Kathmandu time
* Convert dates to calendar year for internal logic
* Use Gregorian fiscal-year assumptions
* Store dates without explicit timezone
* Compare dates without calendar-system awareness

**Example scenario:** A transaction on July 16, 2026 (Gregorian) falls in the previous fiscal year (2082-83 in BS). A transaction on July 17, 2026 falls in fiscal year 2083-84. The coupon matching logic must handle this correctly.

---

## 10c. Prize Pool Data Structures & Terminology

### API Response Structure

**Endpoint:** `https://prize.ird.gov.np/api/v1/public/winners?limit=6&offset=0`

**Response contains:**

* Top-level fiscal years list (`fiscal_years[]`)
* Prize categories list (`categories[]`)
* Draws array (`draws[]`) with nested winners

**Pagination:** offset-based (provide `limit` and `offset` parameters; response includes `has_more` flag)

### Draw Record Structure

Each draw record contains:

* `draw_id` — unique identifier for this draw
* `draw_title_en` / `draw_title_np` — bilingual draw descriptions
* `eligible_from` — transaction start date (Gregorian; convert to BS for internal logic)
* `eligible_to` — transaction end date
* `published_at` — when results were announced
* `claim_deadline` — hard deadline for in-person claims (15 days from announcement)
* `claim_open` — whether claims are currently being accepted
* Nested `winners[]` array (see below)

### Winner Record Structure

Each winner entry contains:

* `winner_rank` — position in draw (1st, 2nd, ... 15th, or "BUMPER")
* `prize_fiscal_year_code` — fiscal year in which the winning transaction occurred (e.g., `2083-84`)
* `prize_coupon_number` — the actual coupon code that matched
* Additional metadata (category, prize amount, etc.)

### Coupon Code Format

**Format:** 12-digit alphanumeric code

**Example:** `007 315 254 493BUMPER`

**Characteristics:**

* May contain spaces (normalize by removing)
* Case-sensitive (normalize to consistent case)
* One coupon = one draw entry, regardless of purchase amount
* Uniquely identifies a transaction

### Key Terminology

**Prize Coupon Number:** The actual 12-digit code that won; links to a specific transaction

**Prize Fiscal Year:** The fiscal year in which the winning transaction occurred (BS format, e.g., `2083-84`)

**Eligible Period:** Date range during which transactions are eligible for a specific draw (`eligible_from` to `eligible_to`)

**Draw Period:** The specific 1st-to-16th or 16th-to-1st window during which eligible transactions were received

**Claim Period:** The 15-day window starting from `published_at` during which winners can claim prizes in-person

### Data Preservation

Store:

* **Raw IRD response payload** — enables audit trail and future API changes
* **Normalized data** — for application matching logic
* **Source identifiers** — tracks which record came from which API response/sync

This enables debugging and adaptation if IRD API structure changes.

---

## 10d. Regulatory & Compliance Considerations

### Nepal Privacy & Data Protection Framework

Nepal is in an **evolving regulatory environment** with multiple, sometimes overlapping, privacy and data-protection requirements:

**Applicable Laws:**

1. **Constitution of Nepal 2015** (Article 27): Guarantees right to privacy as fundamental right

2. **Individual Privacy Act, 2075 (2018):** Primary privacy law covering data protection; requires informed consent before data collection

3. **Data Act, 2079 (2022):** Data governance and protection authority framework; came into force October 13, 2022

4. **Electronic Transactions Act 2063 (2006):** Digital transaction legality and security standards

**Current Status:** No standalone dedicated data-protection regulator fully operational yet. Data Protection Authority is ramping up under Data Act 2079. No statutory breach-notification requirement currently in force.

### Data Handling Requirements

**1. Consent-Based Collection (Mandatory)**

* Obtain explicit informed consent before storing any personal data
* Document all consent (PAN, bank details, transaction history, etc.)
* Provide clear explanation of what data is collected and why

**2. Data Minimization**

* Collect only data necessary for application function (coupon matching, claim tracking)
* Do not over-collect; avoid unnecessary personal information
* Design to minimize sensitive-data exposure

**3. Security Measures**

* Implement encrypted local storage (SQLite can be encrypted)
* Use secure API communications (HTTPS/TLS mandatory)
* Implement access controls on sensitive data (PAN, bank details)
* Maintain secure session management
* Regular security review of personal-data handling

**4. Personal Data Protection**

* **Do not transmit PAN or bank details to IRD** (those are only needed at claim time, in-person)
* Store locally with encryption if needed
* Do not log or expose sensitive data in error messages, logs, or debugging output
* Implement "right to deletion" — allow consumers to delete personal data on request

**5. Third-Party Sharing**

* Do NOT share consumer data with third parties without explicit consent
* Keep data isolated to this application
* Document all data-sharing decisions

**6. User Rights**

* Provide ability to view personal data stored
* Provide ability to export personal data
* Provide ability to delete personal data
* Provide clear privacy policy

### Important Product Distinctions

The application must clearly separate three types of information:

**Government Data** (published by IRD):

* Prize-pool results
* Winner lists
* Coupon matches
* Claim deadlines
* These are public information published by IRD

**User Data** (entered by consumer locally):

* Coupons they own
* Their personal information
* Their transaction history
* Stored locally in the application

**Application-Derived Data** (calculated by the application):

* Matching results
* Claim status (active/expiring/expired)
* Notifications
* These are insights generated by comparing government + user data

The UI must clearly distinguish these. For example, a winning coupon should show:

* [Government icon] Coupon matches published prize-pool result
* [User icon] Your coupon: ABC123
* [Application icon] Claim deadline: 5 days remaining

Do **not** imply:

* Government endorsement of the application
* Official IRD status
* Government ownership

**Implication:** Design the UI and data model to support this distinction cleanly.

### Regulatory Risk Mitigation

* Document all privacy/data handling assumptions in README
* Plan for future Data Protection Authority guidance evolution
* Design architecture to support future authentication/consent flows (may be required)
* Do not hardcode regulatory assumptions; make them adaptable
* Consider future regulations around consumer consent and data storage

---

## 10e. Implementation Decision Framework

This section provides guidance for common implementation ambiguities not fully specified elsewhere.

### Matching Logic Questions

**Q: What fields determine a match?**

* **Answer (from research):** A coupon matches if:
  1. The normalized coupon code matches a prize-coupon-number in IRD results
  2. The transaction date falls within the eligible period for that draw
  3. The fiscal year matches (or is implicit in the draw period)
  4. Network/provider is optional (do not reject matches due to missing network if coupon code is exact match)

**Q: Can a coupon have multiple matches?**

* **Answer:** Unlikely but possible if same coupon code appears in multiple draws. Handle gracefully; allow multiple results.

**Q: What if IRD data has duplicate coupons with different prize amounts?**

* **Answer:** Store all occurrences; display all matches to user. Log the duplication as a data anomaly. Retain raw data for audit.

### Date Handling Questions

**Q: How to validate that a transaction date is "in the correct fiscal year"?**

* **Answer:** A transaction belongs to fiscal year FY if:
  * Gregorian date >= July 17 AND Gregorian date <= July 15 (next calendar year), converted to Bikram Sambat
  * Or use direct Bikram Sambat date range: Shrawan 1 to Ashadh 31 (BS calendar)
  * Always use `Asia/Kathmandu` timezone for boundary checking

**Q: How to handle a transaction on exactly July 17 vs July 16?**

* **Answer:** Test against actual IRD data. Document the boundary. Do not assume; verify against actual draws.

**Q: How to implement the 15-day claim deadline countdown?**

* **Answer:**
  1. Retrieve `published_at` timestamp from IRD response (convert to Nepal time if needed)
  2. Calculate deadline = `published_at` + 15 calendar days
  3. Display countdown in Asia/Kathmandu time
  4. Test mid-midnight transitions and date boundaries

### API Integration Questions

**Q: What happens if the API paginates in an unexpected order?**

* **Answer:** Pagination is offset-based. Assume no guaranteed order. Use deduplication by coupon-code + draw-id to handle repeated requests across pagination. Design sync to be idempotent.

**Q: How to detect "new" vs "updated" records in subsequent syncs?**

* **Answer:** Unique key is (prize_coupon_number, draw_id). If this combination exists, it's an update (or duplicate); if not, it's new. Preserve both occurrences in raw data for audit.

**Q: What if the API returns incomplete data in pagination?**

* **Answer:** Treat as partial sync. Merge with existing data. Do not assume missing records are "no longer winners."

### Sync Strategy Questions

**Q: Should the daily scheduler run at exactly midnight Kathmandu time?**

* **Answer:** Yes. Because:
  1. New draws are announced on the 1st and 16th of the Nepali month
  2. Results are typically posted within 24 hours
  3. Midnight is a natural sync point
  4. Use `Asia/Kathmandu` timezone explicitly; do not rely on system locale

**Q: What if a sync fails? Should we retry immediately?**

* **Answer:** No. Implement exponential backoff. Retain all existing data. Record failure. Retry after 1 hour, then 4 hours, then 24 hours. Never assume "no winners" due to sync failure.

**Q: Should we deduplicate across syncs?**

* **Answer:** Yes. A coupon that matched in Sync 1 should not generate a duplicate notification in Sync 2. Track (prize_coupon_number, draw_id) as unique key. Only notify on NEW matches or status changes (e.g., claim expiring).

### Notification Strategy Questions

**Q: When should we send a notification?**

* **Answer:**
  1. **New match:** Coupon now has a match (not in previous sync)
  2. **Claim deadline approaching:** Less than 2 days remaining
  3. **Claim deadline expired:** Deadline has passed, prize forfeited
  4. **New government data available:** Sync completed with new prize periods
  5. **Sync failed (after retries):** User should know data may be stale

**Q: Should a "sync completed" notification appear for every sync?**

* **Answer:** No. Only if:
  * New prize periods were added, OR
  * New matches found, OR
  * Existing matches' claim status changed (expiring/expired), OR
  * A previous failure was resolved

**Do not** notify on "routine" syncs with no changes. That creates noise.

### UI/UX Questions

**Q: How should we display a match where the physical bill is required but the coupon was auto-enrolled?**

* **Answer:**
  * Display: "Coupon matches published prize-pool result"
  * Also display: "To claim, you must provide the original bill"
  * Provide clear instructions for in-person claim process
  * Do not imply the prize is "guaranteed" — it requires documentation

**Q: How to handle "no results" state?**

* **Answer:**
  * For "no coupons": "Add your first coupon to track prize-pool results"
  * For "no matches": "No matching prize-pool results found for your coupons yet"
  * For "sync failed": "Government data could not be updated. Existing data is still available."
  * Do not show "no winners" without clarifying it's a "no matches" not a "no prizes"

---

## Git & Development Workflow (Sections 11–18)

---

## 11. Repository Initialization

Initialize Git immediately after creating the project. (already done for now)

Create:

```text
master
develop
```

with `master` representing stable production-ready code and `develop` representing the active integration branch.

you can create a gitignore file as required

Do not conduct normal development directly on either permanent branch.

---

## 12. Git Branching Strategy

### 12.1 Branch hierarchy

```text
master
  ↑
develop
  ↑
feature/*
bugfix/*
```

---

### 12.2 `master`

`master` is the stable release branch.

It must:

* always be buildable
* always pass required tests
* contain only stable code
* never contain knowingly broken functionality

Never develop directly on `master`.

---

### 12.3 `develop`

`develop` is the active integration branch.

It contains completed features that have individually passed their feature-level verification.

`develop` is where cross-feature integration is tested.

---

## 13. Feature Branches

Every feature gets its own branch.

Create from `develop`.

Naming:

```text
feature/<short-description>
```

Examples:

```text
feature/coupon-management
feature/ird-sync
feature/matching-engine
feature/dashboard
feature/notifications
feature/settings
feature/prize-pool-explorer
```

Workflow:

```bash
git checkout develop
git pull
git checkout -b feature/<feature-name>
```

A feature branch should represent one coherent feature.

---

## 14. Bug-Fix Branches

Every bug fix gets its own branch.

If the bug belongs to an active feature:

```text
feature/<feature>
        ↓
bugfix/<bug>
```

If the bug exists in integrated `develop`:

```text
develop
   ↓
bugfix/<bug>
```

Naming:

```text
bugfix/<short-description>
```

Every significant bug fix should include a regression test.

---

## 15. Commit Strategy

Use logical, atomic commits.

Examples:

```text
feat: add coupon management
feat: implement IRD prize pool sync
test: add matching engine tests
fix: handle transaction period boundary
test: add regression coverage for duplicate records
docs: document IRD synchronization
```

Do not create one giant commit for the entire project.

Never commit:

* secrets
* credentials
* `.env` files containing secrets
* `node_modules`
* virtual environments
* unnecessary build artifacts
* temporary files
* local IDE state

---

## 16. Feature Development Gate

A feature is not ready for `develop` simply because its code is written.

Before merging:

1. Requirements implemented.
2. Manual feature test completed.
3. Unit tests pass.
4. Integration tests pass.
5. Relevant frontend tests pass.
6. Relevant E2E tests pass.
7. Regression tests pass.
8. Lint passes.
9. Type checking passes.
10. Build passes.
11. Docker build passes if relevant.
12. No obvious errors remain.

Only then merge into `develop`.

---

## 17. Develop Integration Gate

Once multiple features exist in `develop`, test the interactions between them.

This is a separate testing stage.

For example:

```text
Coupon Management
       +
IRD Synchronization
       +
Matching Engine
       +
Notifications
       +
Dashboard
```

must be tested as a single integrated system.

Passing individual feature tests does **not** mean the integrated application works.

---

## 18. Master Release Gate

Only merge:

```text
develop → master
```

after:

* full backend test suite passes
* full frontend test suite passes
* full E2E suite passes
* regression tests pass
* lint passes
* type checking passes
* production build succeeds
* Docker build succeeds
* Dockerized smoke tests pass
* critical consumer journey passes
* synchronization works
* database migrations work
* no blocking issues remain

`master` must represent stable code.

---

## Architecture, Data Models & UI (Sections 19–46)

---

## 19. Architecture

Use the following conceptual architecture:

```text
                    ┌─────────────────────┐
                    │    React Frontend   │
                    └──────────┬──────────┘
                               │
                               │ REST/HTTP
                               ▼
                    ┌─────────────────────┐
                    │     FastAPI API     │
                    └──────────┬──────────┘
                               │
             ┌─────────────────┼─────────────────┐
             │                 │                 │
             ▼                 ▼                 ▼
       Coupon Service    Matching Service   Notification
             │                 │             Service
             │                 │                 │
             └─────────────────┼─────────────────┘
                               │
                               ▼
                        ┌────────────┐
                        │   SQLite   │
                        └─────┬──────┘
                              ▲
                              │
                    ┌─────────┴─────────┐
                    │   Sync Service    │
                    └─────────┬─────────┘
                              │
                              ▼
                        ┌────────────┐
                        │ IRD API    │
                        └────────────┘
```

The exact implementation can differ, but the separation of responsibilities should remain.

---

## 20. Frontend

Use:

* React
* TypeScript
* responsive design
* accessible UI
* clean component architecture

The frontend should not contain core business rules that belong on the backend.
make a separate frontend container that communicates with the backend+data container so that later if i

>Note: create a mobile i can reuse the backend layer and replace the frontend layer

For example, the frontend should display the result of the matching engine rather than independently implementing a second matching algorithm.

---

## 21. Backend

Use:

* Python
* FastAPI
* Pydantic
* SQLAlchemy or equivalent

Organize the backend into clear layers such as:

```text
API
Services
Domain/business logic
Repositories/data access
Models
External integrations
```

Do not put all business logic into route handlers.

---

## 22. Database

Use SQLite initially.

Use migrations.

Prefer Alembic or equivalent.

Design the schema so it can later move to PostgreSQL without rewriting the application architecture.

Use indexes for:

* coupon code
* normalized coupon code
* transaction date
* fiscal year
* network
* prize-pool period
* matching status

---

## 23. Consumer Profile

Create a consumer profile concept.

Do not collect unnecessary personal data.

If authentication is not required for the initial product, keep it local/simple rather than introducing unnecessary authentication infrastructure.

Design the data model so authentication can be introduced later.

---

## 24. Coupon Model

At minimum investigate these fields:

```text
id
coupon_code
normalized_coupon_code
coupon_id
transaction_date
fiscal_year
network
created_at
updated_at
```

Add fields if research indicates they are necessary.

---

## 25. Coupon ID

Generate:

```text
<fiscal-year>-<coupon-code>
```

Example:

```text
2083-84-ABC123
```

Do not require manual entry.

The original coupon code should still be preserved for display.

Normalization should be used for matching/searching without destroying the original value.

---

## 26. Coupon Management UI

Consumers must be able to:

* add
* edit
* delete
* search
* filter
* view
* inspect matching status

Transaction date should support a calendar picker and sensible manual input.

Fiscal year should use a dropdown.

Network should use a configurable dropdown.

---

## 27. Government Prize Pool Model

Create a normalized representation of government data.

Potential fields include:

```text
source_record_id
prize_pool_period
publication_date
transaction_start
transaction_end
coupon_code
normalized_coupon_code
fiscal_year
network
prize_category
prize_amount
claim_start
claim_deadline
source
raw_data
created_at
updated_at
```

Do not assume every field exists.

Only use fields supported by the actual IRD source.

---

## 28. Data Normalization

Government data may have inconsistencies.

Normalize carefully:

* whitespace
* case
* date formats
* fiscal-year representation
* network naming
* numeric values

Never alter the authoritative raw value unnecessarily.

Where useful, store both:

```text
original_value
normalized_value
```

This is particularly important for coupon codes.

---

## 29. Matching Engine

Create a dedicated service.

Conceptually:

```text
User Coupon
    ↓
Normalize
    ↓
Find relevant prize-pool periods
    ↓
Compare coupon
    ↓
Validate date relationship
    ↓
Validate fiscal year if applicable
    ↓
Validate network if applicable
    ↓
Produce Match Result
```

The exact algorithm must be determined from IRD research.

Do not guess.

---

## 30. Match Status

Use clear states where appropriate.

Potential states:

```text
NOT_CHECKED
NO_MATCH
MATCHED
CLAIM_ACTIVE
CLAIM_EXPIRING
CLAIM_EXPIRED
```

Adapt to the actual business rules.

Do not confuse:

> “matched with published data”

with:

> “guaranteed prize payment”.

---

## 31. Dashboard

The dashboard should prioritize action.

Potential sections:

### Attention / Notice Area

Immediately display things requiring attention.

### Winning Coupons

Prominent section for matched coupons.

### Summary

Useful statistics.

### Recent Updates

Recent prize-pool synchronization/publication information.

### Sync Status

Last successful synchronization.

Do not make the dashboard primarily a collection of decorative charts.

---

## 32. Notice System

The dashboard should contain prominent notices for important events.

Examples:

> Your coupon matches a published prize-pool result.

> Your claim deadline is approaching.

> Your claim period has expired.

> New government prize-pool information is available.

> Government synchronization failed.

The notice system should prioritize urgency.

---

## 33. Notifications

Place a notification indicator in the top-right navigation.

Notifications may include:

* new match
* claim deadline approaching
* expired claim
* new synchronized data
* synchronization error
* newly eligible coupon

Avoid duplicate notifications.

A synchronization process should not generate the same notification repeatedly unless the underlying event has genuinely changed.

---

## 34. Claim Deadline Logic

If government data contains claim validity information:

Calculate/display the user's current claim status.

For example:

```text
Claim Active
Claim Deadline Approaching
Claim Expired
```

The application should calculate this using Nepal time.

Use the government's authoritative deadline.

Do not invent deadlines.

---

## 35. Prize Pool Explorer

Create a dedicated page for government prize-pool data.

Support:

* search
* filtering
* sorting
* pagination
* date ranges
* fiscal year
* network
* prize category
* prize amount
* claim status
* coupon code

All large-data filtering should happen server-side.

---

## 36. Settings

Create a Settings page.

Potential configuration:

### Networks

Add/edit/deactivate network options.

### Fiscal Years

Manage available fiscal-year values where appropriate.

### Notifications

Configure notification preferences where useful.

### Synchronization

Display synchronization state and provide manual sync where appropriate.

Do not turn Settings into a dumping ground for technical configuration.

Only expose settings meaningful to users/admins.

---

## 37. Synchronization Architecture

Use a dedicated synchronization service.

Conceptually:

```text
Scheduler
    ↓
Sync Job
    ↓
IRD Client
    ↓
HTTP Request
    ↓
Response Validation
    ↓
Normalization
    ↓
Deduplication
    ↓
Database Upsert
    ↓
Matching Refresh
    ↓
Notification Generation
    ↓
Sync Result
```

A failed sync should not destroy existing data.

---

## 38. Daily Scheduler

The scheduled sync must execute:

> Every day at 12:00 AM `Asia/Kathmandu`.

Do not rely on the operating system's local timezone.

Test the scheduler explicitly.

The Docker environment may use UTC.

The application must still schedule based on Nepal time.

---

## 39. Sync Reliability

Consider:

* retries
* timeout
* backoff
* duplicate execution
* partial responses
* malformed data
* government downtime
* API schema changes
* empty responses
* connection errors

Do not retry indefinitely.

Do not hammer the government service.

---

## 40. Sync Observability

Record:

```text
sync_started_at
sync_finished_at
status
records_received
records_inserted
records_updated
records_skipped
error_message
```

This can be represented through a sync history table if appropriate.

---

## 41. API

Expose clean REST APIs for:

### Profile

```text
GET /api/profile
PUT /api/profile
```

### Coupons

```text
GET /api/coupons
POST /api/coupons
GET /api/coupons/{id}
PUT /api/coupons/{id}
DELETE /api/coupons/{id}
```

### Prize Pools

```text
GET /api/prize-pools
GET /api/prize-pools/{id}
```

### Matches

```text
GET /api/matches
GET /api/wins
GET /api/claims
```

### Notifications

```text
GET /api/notifications
POST /api/notifications/{id}/read
POST /api/notifications/read-all
```

### Settings

```text
GET /api/settings
PUT /api/settings
```

### Synchronization

```text
GET /api/sync/status
POST /api/sync
```

Adapt the final routes based on implementation needs.

---

## 42. API Requirements

APIs should support:

* validation
* pagination
* filtering
* sorting
* useful HTTP status codes
* structured errors
* OpenAPI documentation

Do not expose database models directly if a proper API schema is more appropriate.

---

## 43. Error Handling

The application should never fail silently.

Examples:

### Government API unavailable

Show:

> Government data could not be synchronized. Existing data is still available.

### No matches

Show:

> No matching prize-pool result was found for your coupons.

### No coupons

Show an actionable empty state:

> Add your first coupon to start tracking prize-pool results.

### Database error

Show a generic user-safe message and log the technical details.

---

## 44. UX Principles

The application should feel:

* trustworthy
* simple
* modern
* calm
* clear
* useful

Avoid:

* unnecessary animations
* excessive dashboards
* technical terminology
* clutter
* excessive configuration
* unnecessary popups

The consumer should understand the application without reading documentation.

---

## 45. Accessibility

Implement:

* semantic HTML
* labels
* keyboard navigation
* focus management
* accessible dialogs
* screen-reader-friendly statuses
* meaningful error messages

Do not rely solely on color.

For example, a winning state should use:

* icon
* text
* status
* visual treatment

rather than color alone.

---

## 46. Mobile

The most important flows must work on mobile:

* dashboard
* notification
* winner card
* adding coupon
* editing coupon
* filtering
* viewing claim deadline

Use responsive layouts rather than simply shrinking the desktop UI.

---

## 47. Security

Implement:

* backend validation
* safe database queries
* proper CORS
* environment variables
* safe error responses
* no secrets in Git
* dependency review
* minimal logging of personal information
* no unnecessary tracking

---

## Testing Strategy (Sections 48–54)

---

## 48. Testing Philosophy

Testing is not an afterthought.

Every important feature should have multiple layers of testing:

```text
Unit Test
    ↓
Integration Test
    ↓
Feature Test
    ↓
E2E Test
    ↓
Integrated System Test
    ↓
Release Smoke Test
```

A feature should not rely only on an E2E test.

---

## 49. Backend Tests

Test:

* models
* repositories
* API routes
* validation
* matching
* date calculations
* fiscal years
* notifications
* synchronization
* deduplication
* migrations
* error handling

---

## 50. Matching Tests

At minimum test:

1. Exact winning coupon.
2. Non-winning coupon.
3. Same coupon in another period.
4. Date before period.
5. Date after period.
6. Exact period boundaries.
7. Fiscal-year boundary.
8. Network mismatch.
9. Missing network.
10. Missing government fields.
11. Duplicate government records.
12. Duplicate user coupon.
13. Active claim.
14. Expired claim.
15. Claim deadline boundary.
16. Government record update.

---

## 51. Synchronization Tests

Test:

* successful request
* timeout
* network failure
* malformed response
* empty response
* duplicate records
* updated records
* new records
* partial data
* idempotent repeated sync
* sync failure preserving existing data

Automated tests should use fixtures/mocks.

Do not depend on live IRD availability.

---

## 52. Frontend Tests

Test:

* dashboard
* coupon forms
* coupon list
* filters
* notifications
* winner card
* claim deadline
* settings
* error states
* loading states
* empty states

---

## 53. End-to-End Testing

Use a browser automation framework such as Playwright.

At minimum test:

```text
Open app
   ↓
Add coupon
   ↓
Verify coupon
   ↓
Search/filter
   ↓
Run deterministic sync
   ↓
Load prize pool
   ↓
Match coupon
   ↓
Display winner
   ↓
Display claim deadline
   ↓
Display notification
   ↓
Refresh
   ↓
Verify persistence
```

---

## 54. Do Not Make E2E Tests Depend on Live IRD

Automated tests must use deterministic fixtures.

The live IRD service should only be used for:

* development verification
* integration verification where appropriate
* manual validation

This prevents external downtime from breaking the test suite.

---

## Docker, Release & Verification (Sections 55–79)

---

## 55. Docker

The entire system must run in Docker.

Provide:

```text
Dockerfile(s)
docker-compose.yml
.env.example
```

Use persistent storage for SQLite.

Provide health checks.

The basic startup should be simple:

```bash
docker compose up --build
```

---

## 56. Docker Testing

Do not only test development servers.

Test the actual Dockerized application.

Verify:

* frontend starts
* backend starts
* database initializes
* migrations execute
* API works
* frontend communicates with backend
* scheduler starts correctly
* volumes persist
* application survives restart
* health checks work

---

## 57. Production Build

Verify production builds.

The application should not depend on development-only behavior.

Check:

* frontend production build
* backend startup
* Docker image
* environment configuration
* database migration
* static assets
* API connectivity

---

## 58. Demo/Test Data

Create deterministic fixtures representing:

* normal coupon
* winning coupon
* expired claim
* active claim
* multiple fiscal years
* multiple networks
* multiple prize periods

Never label test data as real government data.
> you can make a demo mode with thei test data. so that you can load the UI and check if everything is as expected or not. this will do 2 things -  test the system data and logic , help test the UI and its reponsiveness

---

## 59. Performance

Use:

* indexes
* server-side filtering
* pagination
* efficient queries
* efficient matching
* appropriate caching

Avoid fetching all coupons/prize-pool records into the browser.

---

## 60. Logging

Log useful operational events:

```text
Application started
Sync started
Sync completed
Sync failed
Records received
Records inserted
Records updated
Matching completed
Unexpected error
```

Do not log sensitive personal data unnecessarily.

---

## 61. Documentation

The repository must include a strong README.

Document:

* product purpose
* architecture
* prerequisites
* installation
* Docker usage
* local development
* environment variables
* migrations
* testing
* E2E testing
* synchronization
* matching logic
* Git workflow
* troubleshooting
* assumptions
* known limitations

---

## 62. Recommended Development Sequence

1. **Research** — Study IRD system (§7-9)
2. **Product/Architecture** — Data model, matching rules, sync, API, UI, test strategy
3. **Repository** — Create `master` + `develop` branches (§11)
4. **Backend Foundation** — Database, migrations, models, API (§21-22)
5. **Government Integration** — IRD client, normalization, sync, scheduler (§37-40)
6. **Matching Service** — Matching logic, statuses, claim calculations (§29-30)
7. **Coupon Management** — CRUD, validation, filtering (§26)
8. **Dashboard** — Summary, notices, winning coupons (§31)
9. **Notifications** — Notification system (§33)
10. **Prize Explorer** — Browsing, filtering (§35)
11. **Settings** — Configuration page (§36)
12. **Testing** — Complete unit/integration/E2E tests (§48-54)
13. **Integration Testing** — Merge features → `develop`, test interactions (§17)
14. **Docker** — Build and test Docker image (§55-56)
15. **Release** — Regression suite, merge to `master` (§18, §73)
16. **Documentation** — Finalize README and assumptions (§61)

*Change this only with strong justification.*

---

## 63. Agent Coordination

If using multiple agents, assign work explicitly.
> Important: Spawning multiple agent might hit the token limit. so work on at max 3 agents. see if their task is completed or not and if all are tested merged and ready to proceed or not. doing so we will not hit org limit and loose agent progress in the middle of a feature or a task.

For example:

### Research Agent

Responsible for:

* IRD website research
* API research
* data-model findings
* matching rules
* domain terminology

Must produce findings before implementation depends on them.

### Backend Agent

Responsible for:

* database
* migrations
* API
* synchronization
* matching
* notifications

Must not redefine frontend UX requirements.

### Frontend Agent

Responsible for:

* UI
* navigation
* dashboard
* coupon management
* prize explorer
* notifications
* settings

Must consume the agreed backend contracts.

### QA Agent

Responsible for:

* test planning
* test implementation
* regression testing
* E2E testing
* edge cases

### DevOps Agent

Responsible for:

* Docker
* Compose
* health checks
* environment configuration
* deployment readiness

### Main Agent

Responsible for:

* coordination
* architecture consistency
* requirement interpretation
* integration
* final verification

---

## 64. Agent Handoff Rules

Agents should not assume another agent's work is correct.

Before depending on another agent's output:

* inspect the implementation
* run relevant tests
* verify contracts
* resolve inconsistencies

Do not blindly merge incompatible implementations.

---

## 65. Important Product Logic Rule

The application must distinguish between:

> **“The user's coupon matches information published by IRD.”**

and:

> **“The government has guaranteed this consumer a prize.”**

The application should only make the first type of claim unless the government source explicitly supports the latter.

Use careful language.

---

## 66. Government Data Integrity

Government data is authoritative for what it publishes, but the application should preserve traceability.

Where appropriate store:

* source record identifier
* source timestamp
* raw source payload
* normalized data

This makes debugging and future changes easier.

---

## 67. Handling Government API Changes

Assume the government API may change.

Design the integration so that:

```text
IRD response
     ↓
Adapter
     ↓
Internal normalized model
```

rather than:

```text
IRD response
     ↓
every application component
```

This reduces the blast radius of API changes.

---

## 68. Handling Sync Failures

If synchronization fails:

### Do

* retain previous data
* record failure
* expose status
* log error
* retry where appropriate

### Do not

* delete existing prize-pool data
* mark all coupons as non-winning
* show misleading “no winners” information
* crash the application

---

## 69. Important Date Rule

All date/time logic must explicitly define timezone behavior.

Use:

```text
Asia/Kathmandu
```

for Nepal-local business logic.

Test:

* midnight
* end-of-day
* period boundaries
* claim deadline boundaries
* fiscal-year transitions

Avoid naive datetime comparisons where timezone ambiguity can occur.

---

## 70. Important Fiscal-Year Rule

Do not treat Nepal fiscal years as ordinary Gregorian calendar years.

For example:

```text
2083-84
```

must remain a distinct fiscal-year representation.

Understand how IRD associates fiscal years with transactions/prize pools before implementing matching logic.

---

## 71. Final QA Persona

Before release, behave like a real consumer.

Ask:

### First impression

Can I understand the application immediately?

### Coupon entry

Can I add a coupon without confusion?

### Data

Can I see what the government has published?

### Matching

Can I easily understand whether I have a match?

### Winning

Would I immediately notice if I had won?

### Claim

Would I understand the deadline?

### Notifications

Are notifications useful rather than noisy?

### Filtering

Can I find an old coupon quickly?

### Reliability

What happens if government synchronization fails?

### Mobile

Can I perform the important actions on my phone?

### Trust

Can I distinguish government data from application-generated information?

Fix any issues discovered.

---

## 72. Final Acceptance Criteria

✅ **Complete only when ALL of the following are true:**

### Product

* [ ] Product name selected.
* [ ] Consumer profile implemented.
* [ ] Coupon management implemented.
* [ ] Prize-pool explorer implemented.
* [ ] Matching implemented.
* [ ] Dashboard implemented.
* [ ] Notifications implemented.
* [ ] Claim status implemented.
* [ ] Settings implemented.
* [ ] Search/filtering implemented.

### Government Integration

* [ ] IRD website researched.
* [ ] IRD API researched.
* [ ] Actual integration implemented.
* [ ] Data normalized.
* [ ] Data persisted.
* [ ] Duplicate records handled.
* [ ] Sync failure handled.
* [ ] Sync status tracked.
* [ ] Daily Nepal-time synchronization implemented.

### Matching

* [ ] Correct coupon matching.
* [ ] Correct period matching.
* [ ] Correct date handling.
* [ ] Correct fiscal-year handling.
* [ ] Correct network handling where applicable.
* [ ] Claim deadline handling.
* [ ] Boundary cases tested.

### Backend

* [ ] FastAPI implemented.
* [ ] Database implemented.
* [ ] Migrations implemented.
* [ ] API documented.
* [ ] Validation implemented.
* [ ] Error handling implemented.
* [ ] Logging implemented.

### Frontend

* [ ] React implemented.
* [ ] Responsive UI.
* [ ] Mobile support.
* [ ] Accessible forms.
* [ ] Loading states.
* [ ] Error states.
* [ ] Empty states.
* [ ] Winning state.
* [ ] Notification state.

### Testing

* [ ] Backend unit tests pass.
* [ ] Backend integration tests pass.
* [ ] Frontend tests pass.
* [ ] E2E tests pass.
* [ ] Regression tests pass.
* [ ] Full integration tests pass.
* [ ] Production build passes.

### Docker

* [ ] Docker build passes.
* [ ] Docker Compose works.
* [ ] Database persists.
* [ ] Health checks pass.
* [ ] Dockerized application manually tested.

### Git

* [ ] `master` exists.
* [ ] `develop` exists.
* [ ] Features use `feature/*`.
* [ ] Bug fixes use `bugfix/*`.
* [ ] Features branch from `develop`.
* [ ] Bug fixes branch from appropriate source.
* [ ] Features individually tested before `develop`.
* [ ] Bug fixes individually tested.
* [ ] Integrated testing completed on `develop`.
* [ ] Full regression testing completed.
* [ ] Only stable code merged into `master`.

### Documentation

* [ ] README complete.
* [ ] Architecture documented.
* [ ] Setup documented.
* [ ] Docker documented.
* [ ] Testing documented.
* [ ] Sync documented.
* [ ] Matching rules documented.
* [ ] Assumptions documented.
* [ ] Limitations documented.

---

## 73. Final Release Process

The final release must follow:

```text
                    ┌─────────────────┐
                    │   Research      │
                    └────────┬────────┘
                             ↓
                    ┌─────────────────┐
                    │    Planning     │
                    └────────┬────────┘
                             ↓
                    ┌─────────────────┐
                    │ Feature Branch  │
                    └────────┬────────┘
                             ↓
                    ┌─────────────────┐
                    │ Implementation  │
                    └────────┬────────┘
                             ↓
                    ┌─────────────────┐
                    │ Feature Testing │
                    └────────┬────────┘
                             ↓
                    ┌─────────────────┐
                    │     develop     │
                    └────────┬────────┘
                             ↓
                    ┌─────────────────┐
                    │ Integration     │
                    │ Testing         │
                    └────────┬────────┘
                             ↓
                    ┌─────────────────┐
                    │ Full Regression │
                    └────────┬────────┘
                             ↓
                    ┌─────────────────┐
                    │ Docker / Smoke  │
                    │ Testing         │
                    └────────┬────────┘
                             ↓
                    ┌─────────────────┐
                    │ Release Review  │
                    └────────┬────────┘
                             ↓
                    ┌─────────────────┐
                    │     master      │
                    └─────────────────┘
```

---

## 74. Final Git Verification

Before declaring completion:

```bash
git status
git branch
git log --oneline --decorate --graph --all
```

Verify:

* no unexpected uncommitted changes
* no secrets
* no temporary files
* `master` is stable
* `develop` contains integrated work
* feature branches were used
* bug-fix branches were used
* history is understandable

---

## 75. Final Application Verification

Actually run the application.

Do not infer success from source code.

Verify the running application:

```text
Application starts
        ↓
Frontend loads
        ↓
Backend responds
        ↓
Database works
        ↓
Profile works
        ↓
Coupon creation works
        ↓
Coupon editing works
        ↓
Coupon deletion works
        ↓
Filtering works
        ↓
Prize pool loads
        ↓
Sync works
        ↓
Matching works
        ↓
Winner appears
        ↓
Notification appears
        ↓
Claim deadline appears
        ↓
Refresh preserves data
        ↓
Docker restart preserves required state
```

---

## 76. Do Not Leave Known Broken Areas

Before completion, search the project for:

```text
TODO
FIXME
HACK
placeholder
mock
dummy
not implemented
coming soon
```

Review every result.

Do not leave unfinished functionality disguised as completed functionality.

Test/demo mocks are acceptable only where explicitly intended for automated testing.

---

## 77. Final Report

Only after everything is actually complete, provide a concise final report.

Include:

### Project

* final name
* path
* repository status

### Research

* key IRD findings
* important implementation implications

### Architecture

* frontend
* backend
* database
* synchronization
* matching

### Features

* coupon management
* dashboard
* prize-pool explorer
* matching
* notifications
* claims
* settings

### Testing

Report actual results.

For example:

```text
Backend tests: PASS
Frontend tests: PASS
E2E tests: PASS
Integration tests: PASS
Lint: PASS
Type check: PASS
Production build: PASS
Docker build: PASS
Docker smoke test: PASS
```

Do not fabricate numbers.

### Git

Report:

* current branch
* `master` status
* `develop` status
* feature/bugfix workflow used

### Limitations

Explain limitations caused by:

* government API behavior
* unavailable data
* source limitations
* deliberate scope decisions

### Startup

Explain how to run:

```bash
docker compose up --build
```

or the actual final command if different.

### Testing Execution

Explain how to run the test suite.

---

## 78. Absolute Completion Rule

The task is **not complete** when:

* the plan is written
* the architecture is designed
* the code compiles
* the UI looks good
* individual tests pass
* Docker builds

The task is complete only when:

> **The application is implemented, integrated, Dockerized, tested, manually verified, documented, and stable enough for `master`.**

---

## 79. Highest-Priority Instruction

### Build the application, don't just describe how to build it

The required behavior is:

```text
Research
→ Understand
→ Decide
→ Implement
→ Test
→ Debug
→ Integrate
→ Verify
→ Dockerize
→ Regression Test
→ Release
→ Document
```

Do not repeatedly ask the user what to do next.

Do not stop after completing one phase.

Do not leave implementation work for the user.

Do not tell the user to manually perform routine engineering steps that you can perform yourself.

Make reasonable decisions autonomously.

When something fails:

> **Investigate → fix → test again.**

When something is ambiguous:

> **Research → decide → document → continue.**

When a feature is complete:

> **Test it → merge it → integration-test it.**

When the system is ready:

> **Run the complete release verification → merge only stable code into `master`.**

The final objective is a **real, working, end-to-end consumer application**, not a demonstration of what could be built.

---

## Summary: Your Mission

You are building a **consumer-facing web application** that integrates with the Nepal IRD prize pool system. The application must:

1. **Retrieve prize-pool data** from the actual IRD API (§8, §37-40)
2. **Normalize and persist** government data locally (§27-28, §66)
3. **Allow consumers** to enter and manage their coupons (§26)
4. **Match coupons** against government results automatically (§29-30, §50)
5. **Display winning matches, claim deadlines, and notifications** clearly (§31-34)
6. **Sync daily at midnight Nepal time** (§38)
7. **Work on mobile and desktop** with full accessibility (§45-46)
8. **Run in Docker** out of the box (§55)
9. **Be tested end-to-end** before release (§48-54)

**Core principle:** Make it obvious to the consumer whether they won. Everything else serves that goal.

**Your definition of done:** A fully implemented, tested, Dockerized application merged into `master` with complete documentation. Not a design, not a prototype — a shipping product.

**When stuck:** Refer back to the source of truth hierarchy (§5) and the critical rules (Quick Reference, above).

---
