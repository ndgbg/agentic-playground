# Annual Forte - Work Contribution

---

## Work Contribution Name

Full-Stack Windows Modernization for AWS Transform

## Work Description

**Situation & Goal:**
Enterprise customers running Windows workloads on AWS consistently told us that modernizing just the .NET application layer wasn't enough. Their applications follow a three-tier architecture — .NET applications, SQL Server databases, and legacy ASP.NET UI — all tightly coupled together. They needed a single, coordinated solution that could transform all tiers end-to-end, not piecemeal tools that left them stitching the pieces together manually. The goal was to build and launch a full-stack Windows modernization capability within AWS Transform that could migrate customers from SQL Server to Amazon Aurora PostgreSQL-Compatible Edition while simultaneously modernizing the dependent .NET application code and UI layer — accelerating modernization by 5x and reducing operating costs by up to 70%.

**My Role & Actions:**
As the IC PMT, I owned the end-to-end product definition, working backwards from customers and driving the initiative from concept through launch at re:Invent 2025. Specifically, I:

- **Drove the working backwards process and prototyping** to validate the vision for a multi-agentic AI system that could coordinate database schema conversion, data migration (via DMS), application code refactoring, and deployment in a unified workflow — a first for AWS Transform.
- **Led cross-functional collaboration across organizational boundaries**, partnering closely with the DMS team and the AWS Transform Platform/Foundation team to integrate SQL Server-to-Aurora PostgreSQL migration capabilities, including intelligent stored procedure conversion, Entity Framework and ADO.NET refactoring, and wave-based transformation planning.
- **Removed blockers across multiple teams and orgs**, taking on a cross-org coordination goal to align priorities, resolve technical dependencies, and keep the program on track for the re:Invent launch window.
- **Shaped the agentic architecture** of a system where specialized AI agents autonomously handle schema conversion, data migration, application code transformation, and deployment validation — with built-in human review checkpoints and auto-remediation loops.

**Risks Taken:**
We committed to building a multi-agentic AI system — multiple specialized agents coordinating across database, application, and UI layers — in a compressed timeline with multiple teams involved. This was technically ambitious: agentic AI for code transformation was nascent, the cross-team integration surface was large, and delivering a cohesive full-stack experience (not just a collection of disconnected tools) required tight coordination under significant schedule pressure. I advocated for this approach because the customer need was clear and the half-measure of shipping disconnected capabilities would have missed the mark.

**Impact & Outcomes:**
- **Launched at re:Invent 2025** as a headline announcement, with VP Asa Kalavade presenting the capabilities. The launch received coverage across major tech outlets and was highlighted in AWS's top re:Invent announcements.
- **25+ customers actively using the service**, running **80+ modernization jobs** — validating the product-market fit and the full-stack approach.
- **Customers like Teamfront modernized 800,000 lines of code in just two weeks** — work that would have previously taken months — demonstrating the 5x acceleration promise.
- **Industry recognition**: customers including Air Canada, Experian, Thomson Reuters, and Verisk are using AWS Transform, with the full-stack Windows modernization capabilities expanding the addressable market to the massive installed base of SQL Server workloads.
- **No additional charge** for the Windows modernization features, making it a high-value on-ramp for customers modernizing off SQL Server licensing costs (up to 70% operating cost reduction).

---
