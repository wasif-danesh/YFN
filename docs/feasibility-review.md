# Your Friendly Neighbourhood feasibility review

Reviewed 8 September 2026. This is an assessment of the proposed plan, not approval of its pending decisions or an instruction to start development. The existing planning and reference files have not been changed.

**Verdict: the project is achievable. The proposed architecture and three-page journey are appropriate. A two-week Iteration 1 with all four indicators is plausible but remains conditional on early spatial-data validation, team capacity and an agreed scope. The folder does not yet establish delivery readiness.**

The review covered the root instructions and README, all three handover documents, the reference index, both pitch PDFs (including the updated PDF outside the reference folder), the requirements specification, both assessment instruction PDFs and all three wireframes. Relevant embedded architecture and assessment pages were also inspected visually. Official source catalogues, PTAL metadata and sample features, open-space sample records, ABS release information and hosting documentation were checked. There is no application, Git repository or prepared database in the supplied folder. No complete data pipeline, spatial overlay, deployed application or performance test was run.

**What is technically feasible**

| Part | Finding | Remaining evidence needed |
|---|---|---|
| Home, Compare, Area Details | A bounded, conventional web application. Search, two/three selections, four measures and a population chart are manageable. | Mobile layout, keyboard journey, loading/error states and comprehension testing. |
| Nuxt static frontend | Supported architecture. Static files can run JavaScript that requests the separate FastAPI service. | Explicit handling of direct area URLs, prerendered content and comparison state. |
| FastAPI and SQLite | Appropriate for a small, public, read-only indicator dataset. Spatial work stays offline. | Response validation, read-only deployment, query tests and a repeatable database release process. |
| Population | ABS publishes SA2 estimates for 2001–2025, supporting the proposed 2020–2025 interval. | Inspect workbook rows and validate joins to the chosen SA2 master. |
| Rent | The official page exposes the proposed Victoria 2021 SA2 GCP download. | Inspect G02, its dictionary and missing-value rules; validate area coverage. |
| Transport | The live PTAL service exposes polygons and a numeric index, so the proposed spatial processing has a real input. | Verify numeric-field meaning, overlaps, coverage, weighting and the benchmark population. |
| Open space | Accessible polygon records include access and land-category attributes. | Agree eligible categories, establish geographic completeness and validate union/intersection results. |

Nuxt documents static generation into `.output/public`: [official prerendering documentation](https://nuxt.com/docs/4.x/getting-started/prerendering). The design does not require a live Node frontend server.

**Resolve the document conflicts first**

The additional [updated pitch](../Assessment1_Pitch_Report_updated..pdf) is absent from `docs/references/README.md`. Its section 10 still promises housing and population for Iteration 1, whereas the Word specification and handover requirements target all four measures. Its section 6 proposes percentiles for every indicator and rent relative to income; the handover instead proposes raw rent, raw population growth, square metres per resident and only a transport percentile. The updated pitch also uses open space per 1,000 residents while the UI uses per resident.

These are different product commitments, not wording variations. Agree a short baseline naming the Iteration 1 features, each measure and unit, geography and accepted limitations. Mark other versions as proposals or superseded where appropriate. A filename containing “updated” is not evidence of team approval. The simpler handover measures are the more achievable baseline, but changing the pitch commitment should be recorded.

**Transport validation is the main technical dependency**

On the review date the official WFS layer `open-data-platform:ptal_metro` reported 360,662 features. Its schema exposes `sum_ai_8_9` as a numeric double, `category_8_9` as a string and a surface geometry. Three fetched sample records had polygon geometry, a numeric zero and Category 1. This confirms a usable numeric field exists; it does not establish the distribution or coverage of the whole layer.

The [official PTAL fact sheet](https://www.planning.vic.gov.au/__data/assets/pdf_file/0033/762738/PTAL-Fact-Sheet-December-2025.pdf) describes a 200 m grid, scheduled services from 8–9 am on 2 April 2025, and an access index based on walking and waiting. It excludes destination variety, interchange convenience, crowding and temporary disruptions. Match the actual layer release to this documentation before assigning an observation date. A 2026 catalogue update is not evidence of 2026 service conditions.

An area-weighted mean of the verified numeric index is computationally possible, but its suitability as a renter-facing summary remains a project judgement. Do not average category labels. Use spatial indexing and a projected area calculation; first test a small slice containing inner, middle and fringe areas before processing the full layer. Investigate overlaps and uncovered land. Numeric zero in a sampled cell is different from missing spatial coverage.

If a percentile is retained, name it as the project's relative score, not an official PTAL score out of 100. Agree the coverage rule and eligible benchmark set; preserve the benchmark membership or its reproducible definition/hash as well as the count. Test tied values, unavailable values and rating boundaries. Selecting different comparison areas must not change a score.

Evidence: [dataset catalogue](https://discover.data.vic.gov.au/en_AU/dataset/public-transport-accessibility-level-ptal-melbourne-metro), [live field schema](https://opendata.maps.vic.gov.au/geoserver/wfs?service=WFS&version=2.0.0&request=DescribeFeatureType&typeNames=open-data-platform%3Aptal_metro), [three-feature sample](https://opendata.maps.vic.gov.au/geoserver/wfs?service=WFS&version=2.0.0&request=GetFeature&typeNames=open-data-platform%3Aptal_metro&count=3&outputFormat=application%2Fjson).

**Open-space data can be processed, but its meaning needs narrowing**

The [current catalogue](https://discover.data.vic.gov.au/dataset/open-space) explicitly says the source is not maintained and includes public, restricted and private land. Its metadata update date does not make the underlying inventory current. [Live records](https://services5.arcgis.com/DmRfik4clMVydXO3/arcgis/rest/services/VPA_Draft_Open_Space_Data/FeatureServer/0/query?outFields=*&where=1%3D1) expose `OS_ACCESS`, `OS_TYPE`, `OS_CATEGOR` and `OS_STATUS`. Examples distinguish university land with limited access from public parks with open access; another record has open access but a restricted-public-land type. A single ownership or category check will not settle every case.

Agree whether the measure is public open space or vegetated green space: these are not interchangeable. Define the category/access filter and record ambiguous exclusions. Dissolve overlapping eligible geometry before calculating area within each SA2. Keep the open-space observation date and population denominator year visible. Public open-space area per resident does not measure distance to a park, park quality or provision just across the boundary. Geographic completeness cannot be inferred from the percentage of an SA2 occupied by park polygons.

**Population and rent are lower-risk inputs, with material product limitations**

The [ABS Regional Population release](https://www.abs.gov.au/statistics/people/population/regional-population/2024-25) provides the `32180DS0003_2001-25.xlsx` download. The [methodology](https://www.abs.gov.au/methodologies/regional-population-methodology/2024-25) identifies ASGS Edition 3 geography and states that 2025 estimates are preliminary. Use one consistent release for the history and endpoints. Describe growth as estimated historical population change. Six annual observations cover a five-year interval; missing baseline values make the percentage unavailable, and small baselines need careful explanation.

The [Census DataPacks page](https://www.abs.gov.au/census/find-census-data/datapacks) links the proposed `2021_GCP_SA2_for_VIC_short-header.zip`. The files themselves were not profiled in this review. The 2021 rent measure is suitable for a dated historical comparison. It cannot establish what a renter would pay today, and different dwelling mixes can affect area medians. Whether that historical comparison is useful enough to newcomers is a user-testing question, not something technical feasibility can prove.

Keep the 2021 SA2 geography for the baseline and join on codes. Do not silently substitute suburb figures or average suburb medians into an SA2 median. Start with clear official area-name search; verified suburb aliases can follow if time permits. The search design also needs testing with newcomers who may not know any area names.

**Deployment works if the database is packaged with the backend**

The updated pitch's architecture drawing places SQLite outside the Render box. Clarify that the deployed API reads a local database file included in its release; it does not query the team's laptop or treat SQLite as a separate network database server. Keep that file outside the frontend publish directory.

Render's [current free-service documentation](https://render.com/docs/free) says free web services sleep after 15 minutes without traffic and take about a minute to wake. Runtime filesystem changes are lost on restart/redeploy. Packaging an immutable database in each release fits this model; relying on a manually uploaded runtime file does not. A warm response target under one second is not a first-visit guarantee. Choose the service tier with demonstration reliability in mind, and test cold-start behaviour separately.

Choose one route strategy for direct area links, configure the public API URL and CORS, and ensure deployment actually waits for successful checks. If any data is prerendered into frontend pages, coordinate its data version with the API release. These are implementation details to settle, not reasons to change the stack.

**Make the schedule depend on evidence and actual availability**

The parallel frontend/API/data/integration approach is sound. Agree the JSON contract early and use the same database builder and response models for synthetic and real data. Keep the spatial pipeline off the request path. Assign a primary owner and reviewer for each stream, with explicit support for the spatial work. Four team members do not establish how many development hours are available.

Use this as a proposed sequence, not a delivery guarantee:

| Working days | Evidence expected |
|---|---|
| 1–2 | Scope and owners agreed; real source fields inspected; a small spatial calculation attempted; shared JSON examples and database schema fixed. |
| 3–4 | Complete synthetic-data page journey; minimal frontend/API deployment when authorised; first verified real-area outputs. |
| 5–7 | Real-data integration and full eligible-area processing; source and calculation checks; decision on any category that fails validation. |
| 8–10 | User and accessibility testing, defect fixes, report/portfolio completion, deployed verification and presentation rehearsal. |

Reserve contingency inside the team's actual available time. The existing days 11–14 are calendar days, not automatically four extra working days. Prepare assessment evidence throughout development. If a spatial source fails the early check, explicitly renegotiate the affected indicator rather than leaving an entire promised category unavailable. The narrower housing/population release is a credible fallback already present in both pitch versions, subject to the agreed assessment scope.

**Assessment work needs its own owners and tasks**

The copied [Assessment 1 instructions](references/Assessment1_Instructions.pdf), page 3, require at least two datasets and disallow web scraping for acquisition. Official downloads and documented spatial services fit the planned acquisition approach. The [Assessment 2 instructions](references/Assessment2_Instructions.pdf), pages 1–5 and 7–9, require more than the working website: a project overview report, populated Project Governance Portfolio, Trello stories and acceptance criteria, data-governance and security evidence, testing/support materials, a recorded Iteration 1 presentation, feedback and a retrospective. The retrospective is due within three days after OLA feedback. The build accounts for 40% of the displayed rubric, so the other deliverables are substantial work.

Use the stated OLA hosting correction in the handover rather than reinstating Monash-server development. Other assessment requirements remain relevant. Verify actual submission dates in the course portal; the copied documents specify teaching weeks. No claim of assessment compliance or a particular grade can be made from this folder alone.

**Decision before committing to all four indicators**

Proceed with the project concept and architecture. Commit to the full Iteration 1 target only after the team has an agreed scope, enough allocated hours, a working sample calculation from each spatial source, defensible measure definitions, and tasks covering assessment evidence. The key validation is a small real-data journey early in development. A polished mockup alone would not resolve the remaining risks.
