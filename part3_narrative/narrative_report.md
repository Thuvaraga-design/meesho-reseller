# Worked Narrative Report

## Decision Rule
A category is eligible for an automatic flagged-category narrative only when `abs(mom_pct) > 8.0%` and `is_flagged()` returns `"flagged"`. If `abs(mom_pct) < 8.0%`, the category is `"not_flagged"` and no flagged narrative is generated; if `abs(mom_pct) == 8.0%`, the result is `"escalate_exact_boundary"` and must be sent for human review.

## May — Ethnic Wear

### Context
Ethnic Wear revenue is being compared between April and May.

### Insight
Ethnic Wear revenue increased from INR 104520.77 in April to INR 185107.61 in May, a 77.1% month-on-month increase. The category is flagged because the MoM change exceeds the defined threshold.

### Implication
The increase may be associated with stronger customer demand, higher product availability, or successful promotional activity, but the revenue data alone does not establish the cause. The regional manager should check inventory availability, order trends, and relevant sales or campaign records for Ethnic Wear between April and May to identify the factors associated with the increase.

---

## June — Ethnic Wear

### Context
Ethnic Wear revenue is being compared between May and June.

### Insight
Ethnic Wear revenue decreased from INR 185107.61 in May to INR 76371.53 in June, a -58.74% month-on-month change. The category is flagged because the absolute MoM change exceeds the defined threshold.

### Implication
The decline may be associated with reduced customer demand, lower product availability, or weaker promotional activity, but the revenue data alone does not establish the cause. The regional manager should check inventory availability, order trends, and relevant sales or campaign records for Ethnic Wear between May and June to identify the factors associated with the decline.

---

# Refinement Checklist

### 1. Specificity — PASS
The narratives use the correct category, months, revenue figures, and MoM percentages from the verified uploaded data(Part1/2 data).

### 2. Audience Fit — PASS
The narratives focus on the business change and practical next steps that are relevant to a regional manager rather than describing technical implementation details.

### 3. Completeness — PASS
Both narratives contain all three required sections: Context, Insight, and Implication.

### 4. Actionability — PASS
Each implication gives concrete checks for the regional manager, including inventory availability and relevant sales or campaign records, rather than using a vague instruction such as "look into this."


## 3.3 — Chart-Choice Justification

### 1. Which month had the highest total revenue?

I would use a **bar chart** because this is a simple bivariate comparison between the categorical variable **month** and the numerical variable **total revenue**. The chart would show April at INR 419417.43, May at INR 444594.25, and June at INR 398055.24, making it easy to identify that May had the highest total revenue within 10 seconds. The y-axis should start at zero so that the differences in revenue are not visually exaggerated. A 3D chart should be avoided because it can distort the comparison, and no legend is needed because there is only one revenue series.

### 2. What percentage share does Ethnic Wear represent of April's total revenue?

I would use a **pie chart** because this question asks for a part-to-whole relationship: Ethnic Wear's INR 104520.77 is part of April's total revenue of INR 419417.43, representing **24.92%**. This is a simple bivariate part-to-whole comparison rather than a multivariate analysis, and a pie chart allows the share to be understood quickly within 10 seconds. A 3D pie chart should be avoided because it can distort the apparent size of the slice. A y-axis is not applicable to a pie chart, and a legend is unnecessary if the category and percentage are labeled directly.

### 3. How do the four regions compare on total revenue?

I would use a **bar chart** because this is a bivariate comparison between the categorical variable **region** and the numerical variable **total revenue**. The four regional revenues are East at INR 275098.45, North at INR 337125.46, South at INR 316736.68, and West at INR 333106.33. A bar chart makes these four values easy to compare and allows the regional manager to understand the differences within 10 seconds. The y-axis should start at zero to provide an accurate visual comparison, and a 3D chart should be avoided because it can distort bar heights. Since there is only one series, total revenue, a legend is not required; the region names should be shown directly on the axis.


## 3.4 — Masking Policy

### Top-Reseller Narrative

The Part 1 HAVING query identified five top resellers based on total revenue. The external-facing narrative masks each reseller using its region and approved alias rather than exposing the raw reseller name.

- **West region — ALIAS-19:** total revenue of INR 75295.09.
- **West region — ALIAS-22:** total revenue of INR 73882.33.
- **South region — ALIAS-12:** total revenue of INR 69936.46.
- **North region — ALIAS-06:** total revenue of INR 64238.97.
- **North region — ALIAS-05:** total revenue of INR 61825.02.

The regional team can use these masked identifiers to review the corresponding reseller performance while keeping raw reseller names out of any external-facing summary.

### Leak Check

The final narrative is checked against the complete list of raw reseller names using `assert_no_raw_names_leak()`.

Expected result:**True**
