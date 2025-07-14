# scripts/heatmap_utils.py  (RL‑pipeline 2025‑07) — pure‑Matplotlib version
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# ─────────────────────────── helpers ──────────────────────────────────────
def _pivot(df: pd.DataFrame, index: str, col: str, val: str) -> pd.DataFrame:
    """Return pivot table filled with zeros (mean aggregation)."""
    p = df.pivot_table(index=index, columns=col, values=val, aggfunc="mean").fillna(0)
    if col == "time_slot":
        order = [t for t in ["Morning", "Afternoon", "Evening", "Night"] if t in p.columns]
        p = p[order]
    return p


def _draw_heatmap(pivot: pd.DataFrame,
                  title: str,
                  cbar_label: str,
                  out_path: str,
                  fmt: str = ".1f"):
    """Draw and save a numerical heatmap using pure Matplotlib."""
    fig, ax = plt.subplots(figsize=(12, 8))
    mesh = ax.pcolormesh(pivot.values, shading="auto")
    cbar = fig.colorbar(mesh, ax=ax)
    cbar.set_label(cbar_label)

    for i in range(pivot.shape[0]):
        for j in range(pivot.shape[1]):
            ax.text(j + 0.5, i + 0.5,
                    format(pivot.iat[i, j], fmt),
                    va="center", ha="center", fontsize=8)

    ax.set_xticks(np.arange(pivot.shape[1]) + 0.5, pivot.columns, rotation=45, ha="right")
    ax.set_yticks(np.arange(pivot.shape[0]) + 0.5, pivot.index)
    ax.set_xlabel(pivot.columns.name or "")
    ax.set_ylabel(pivot.index.name or "")
    ax.set_title(title, pad=20, fontweight="bold")

    plt.tight_layout()
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.savefig(out_path, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"✅ Saved: {out_path} — shape={pivot.shape}")


# ─────────────────────────── public functions ─────────────────────────────
def _ensure_zone_group(df: pd.DataFrame):
    """Add a `zone_group` column for cleaner heatmaps."""
    if "zone_group" not in df:
        if df["from_zone"].dtype == object:
            df["zone_group"] = df["from_zone"].astype(str).str[:3]
        else:
            df["zone_group"] = pd.qcut(df["from_zone"].astype(int), q=20, labels=False)


def generate_heatmap(df: pd.DataFrame,
                     output_path: str = "outputs/zone_time_heatmap.png"):
    """Average delivery time per zone_group & time_slot."""
    _ensure_zone_group(df)
    time_col = next((c for c in ("predicted_time_min", "actual_time_min") if c in df), None)
    if not time_col or "zone_group" not in df or "time_slot" not in df:
        print("❌ Required columns missing for heatmap.")
        return

    pivot = _pivot(df, "zone_group", "time_slot", time_col)
    _draw_heatmap(
        pivot,
        f"Average Delivery Time by Zone & Time Slot\n(Using {time_col})",
        f"Avg {time_col.replace('_', ' ').title()}",
        output_path,
        fmt=".1f",
    )


def generate_delay_heatmap(df: pd.DataFrame,
                           output_path: str = "outputs/delay_heatmap.png"):
    """Delay probability (>90 min) by zone_group vs categorical feature."""
    _ensure_zone_group(df)
    if "delay_label" not in df:
        df["delay_label"] = (df["actual_time_min"] > 90).astype(int)

    for col, label in [
        ("time_slot", "Time Slot"),
        ("weight_category", "Weight Category"),
        ("distance_category", "Distance Category"),
    ]:
        if col not in df:
            continue
        pivot = _pivot(df, "zone_group", col, "delay_label")
        out = output_path.replace(".png", f"_by_{col}.png")
        _draw_heatmap(
            pivot,
            f"Delay Probability by Zone & {label}\n(Delay > 90 min)",
            "Delay Probability",
            out,
            fmt=".2f",
        )
        return
    print("❌ No suitable categorical column found for delay heatmap.")


def generate_performance_heatmap(df: pd.DataFrame,
                                 output_path: str = "outputs/performance_heatmap.png"):
    """Efficiency (km/min) by zone_group & time_slot."""
    _ensure_zone_group(df)
    if "efficiency_km_per_min" not in df and {"distance_km", "actual_time_min"}.issubset(df):
        df["efficiency_km_per_min"] = df["distance_km"] / (df["actual_time_min"] + 1)

    if "time_slot" not in df:
        print("❌ 'time_slot' missing for performance heatmap.")
        return

    pivot = _pivot(df, "zone_group", "time_slot", "efficiency_km_per_min")
    _draw_heatmap(
        pivot,
        "Delivery Efficiency by Zone & Time Slot\n(Higher = Better)",
        "Efficiency (km/min)",
        output_path,
        fmt=".3f",
    )


def generate_all_heatmaps(df: pd.DataFrame, output_dir: str = "outputs/"):
    """Generate all three heatmaps in one call."""
    print("🎨 Generating full heatmap suite …")
    os.makedirs(output_dir, exist_ok=True)
    _ensure_zone_group(df)
    generate_heatmap(df, os.path.join(output_dir, "zone_time_heatmap.png"))
    generate_delay_heatmap(df, os.path.join(output_dir, "delay_heatmap.png"))
    generate_performance_heatmap(df, os.path.join(output_dir, "performance_heatmap.png"))
    print("✅ All heatmaps generated!")


# ── CLI entry point ───────────────────────────────────────────────────────
if __name__ == "__main__":
    print("🔍 Heatmap utils ready – call generate_all_heatmaps(df).")
