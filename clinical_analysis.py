import matplotlib
matplotlib.use('Agg')
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Set overall seaborn aesthetic theme
sns.set_theme(style="whitegrid")
plt.rcParams.update({
    'font.sans-serif': 'Segoe UI',
    'font.family': 'sans-serif',
    'figure.titlesize': 14,
    'axes.titlesize': 12,
    'axes.labelsize': 11
})

# 1. Load clinical data handling TCGA missing placeholders
na_tokens = ["'--", "--", "not reported", "Not Reported", "unknown", "Unknown"]
df = pd.read_csv("clinicaldata/clinical.tsv", sep="\t", low_memory=False, na_values=na_tokens)

print(f"Total records loaded: {df.shape[0]} rows, {df.shape[1]} columns")

# 2. Patient-level deduplication
# A patient (case) can have multiple diagnosis or treatment entries.
df_patients = df.drop_duplicates(subset=["cases.case_id"]).copy()
print(f"Unique patient cohort size: {len(df_patients)}")

# Cast and clean key demographic and clinical metrics
df_patients["Age"] = pd.to_numeric(df_patients["demographic.age_at_index"], errors="coerce")
df_patients["Vital Status"] = df_patients["demographic.vital_status"].fillna("Unknown")
df_patients["Race"] = df_patients["demographic.race"].str.title().fillna("Not Reported")
df_patients["Sex"] = df_patients["demographic.sex_at_birth"].str.title().fillna("Not Reported")
df_patients["Primary Diagnosis"] = df_patients["diagnoses.primary_diagnosis"].fillna("Other")

# Simplify pathologic stages (group sub-stages like IIA/IIB into Stage II for higher-level clarity)
def clean_stage(val):
    if not isinstance(val, str):
        return np.nan
    val = val.strip()
    if val.startswith("Stage I") and not val.startswith("Stage IV"):
        if val.startswith("Stage IA") or val.startswith("Stage IB") or val == "Stage I":
            return "Stage I"
        elif val.startswith("Stage IIA") or val.startswith("Stage IIB") or val == "Stage II":
            return "Stage II"
        elif val.startswith("Stage IIIA") or val.startswith("Stage IIIB") or val.startswith("Stage IIIC") or val == "Stage III":
            return "Stage III"
        elif val.startswith("Stage IV"):
            return "Stage IV"
    elif val == "Stage IV":
        return "Stage IV"
    elif val in ["Stage X", "Stage Tis"]:
        return "Other"
    return val

df_patients["Simplified Stage"] = df_patients["diagnoses.ajcc_pathologic_stage"].apply(clean_stage)

# ----------------- Visualizations ----------------- #
fig, axes = plt.subplots(2, 3, figsize=(18, 10))
fig.suptitle("TCGA Breast Cancer Clinical Dataset - Comprehensive Exploratory Data Analysis", fontsize=16, fontweight='bold', y=0.98)

# 1. Age Distribution by Vital Status (Histplot + KDE)
sns.histplot(
    data=df_patients,
    x="Age",
    hue="Vital Status",
    kde=True,
    element="step",
    bins=25,
    palette={"Alive": "#2b5c8f", "Dead": "#d95f02"},
    ax=axes[0, 0]
)
axes[0, 0].set_title("1. Patient Age Distribution by Vital Status")
axes[0, 0].set_xlabel("Age at Diagnosis / Index (Years)")
axes[0, 0].set_ylabel("Patient Count")

# 2. Vital Status Count Plot
sns.countplot(
    data=df_patients,
    x="Vital Status",
    hue="Vital Status",
    legend=False,
    palette={"Alive": "#4daf4a", "Dead": "#e41a1c"},
    ax=axes[0, 1]
)
axes[0, 1].set_title("2. Patient Survival / Vital Status")
axes[0, 1].set_xlabel("Vital Status")
axes[0, 1].set_ylabel("Patient Count")
for p in axes[0, 1].patches:
    axes[0, 1].annotate(f'{int(p.get_height())}', (p.get_x() + p.get_width() / 2., p.get_height() / 2),
                        ha='center', va='center', color='white', fontweight='bold', fontsize=12)

# 3. Pathological Stage Distribution (Simplified)
stage_counts = df_patients["Simplified Stage"].value_counts().reindex(["Stage I", "Stage II", "Stage III", "Stage IV"]).dropna()
sns.barplot(
    x=stage_counts.index,
    y=stage_counts.values,
    hue=stage_counts.index,
    legend=False,
    palette="Blues_r",
    ax=axes[0, 2]
)
axes[0, 2].set_title("3. AJCC Pathologic Stage Distribution")
axes[0, 2].set_xlabel("Tumor Stage")
axes[0, 2].set_ylabel("Patient Count")
for p in axes[0, 2].patches:
    axes[0, 2].annotate(f'{int(p.get_height())}', (p.get_x() + p.get_width() / 2., p.get_height() + 5),
                        ha='center', va='bottom', fontsize=10, fontweight='semibold')

# 4. Age Distribution Across AJCC Stages (Boxplot with Jitter Stripplot)
stage_order = ["Stage I", "Stage II", "Stage III", "Stage IV"]
df_staged = df_patients[df_patients["Simplified Stage"].isin(stage_order)]
sns.boxplot(
    data=df_staged,
    x="Simplified Stage",
    y="Age",
    hue="Simplified Stage",
    legend=False,
    order=stage_order,
    palette="Set2",
    boxprops=dict(alpha=0.7),
    ax=axes[1, 0]
)
sns.stripplot(
    data=df_staged,
    x="Simplified Stage",
    y="Age",
    order=stage_order,
    color="black",
    size=3,
    alpha=0.3,
    jitter=0.2,
    ax=axes[1, 0]
)
axes[1, 0].set_title("4. Age Variation by Cancer Stage")
axes[1, 0].set_xlabel("Pathologic Stage")
axes[1, 0].set_ylabel("Age (Years)")

# 5. Cohort Racial Demographics (Horizontal Barplot)
top_races = df_patients["Race"].value_counts().head(4)
sns.barplot(
    y=top_races.index,
    x=top_races.values,
    hue=top_races.index,
    legend=False,
    palette="viridis",
    ax=axes[1, 1]
)
axes[1, 1].set_title("5. Cohort Racial Representation")
axes[1, 1].set_xlabel("Patient Count")
axes[1, 1].set_ylabel("Race")
for p in axes[1, 1].patches:
    axes[1, 1].annotate(f'{int(p.get_width())}', (p.get_width() - 50, p.get_y() + p.get_height() / 2.),
                        ha='right', va='center', color='white', fontweight='bold', fontsize=10)

# 6. Top Treatment Modalities (from whole clinical dataset)
treatment_counts = df["treatments.treatment_type"].dropna().value_counts().head(6)
sns.barplot(
    y=treatment_counts.index,
    x=treatment_counts.values,
    hue=treatment_counts.index,
    legend=False,
    palette="mako",
    ax=axes[1, 2]
)
axes[1, 2].set_title("6. Common Treatment Regimens Administered")
axes[1, 2].set_xlabel("Treatment Events / Records")
axes[1, 2].set_ylabel("Treatment Type")
for p in axes[1, 2].patches:
    axes[1, 2].annotate(f'{int(p.get_width())}', (p.get_width() - 70, p.get_y() + p.get_height() / 2.),
                        ha='right', va='center', color='white', fontweight='bold', fontsize=9)

plt.tight_layout()
plt.savefig("clinical_data_visualization.png", dpi=300, bbox_inches='tight')
print("Successfully generated and saved 'clinical_data_visualization.png'!")
