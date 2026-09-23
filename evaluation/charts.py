from __future__ import annotations

from html import escape
from pathlib import Path
from typing import Any


COLORS = ["#2563eb", "#7c3aed", "#059669", "#dc2626", "#d97706"]


def _label(value: str) -> str:
    return value.replace("_", " ").title()


def render_test_f1_chart(result: dict[str, Any]) -> str:
    models = list(result["models"].items())
    width = 900
    height = 110 + (len(models) * 75)
    plot_width = 600
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        '<text x="30" y="38" font-family="Arial" font-size="24" font-weight="700" fill="#111827">Untouched Pilot Test F1</text>',
        '<text x="30" y="64" font-family="Arial" font-size="14" fill="#4b5563">Review decision after citation and quotation exclusions</text>',
    ]
    for index, (model_name, model) in enumerate(models):
        y = 95 + (index * 75)
        f1 = float(model["splits"]["test"]["end_to_end_review"]["f1"])
        bar_width = f1 * plot_width
        parts.extend(
            [
                f'<text x="30" y="{y + 22}" font-family="Arial" font-size="15" fill="#111827">{escape(_label(model_name))}</text>',
                f'<rect x="210" y="{y}" width="{plot_width}" height="30" rx="5" fill="#e5e7eb"/>',
                f'<rect x="210" y="{y}" width="{bar_width:.1f}" height="30" rx="5" fill="{COLORS[index % len(COLORS)]}"/>',
                f'<text x="{220 + bar_width:.1f}" y="{y + 21}" font-family="Arial" font-size="14" font-weight="700" fill="#111827">{f1:.4f}</text>',
            ]
        )
    parts.append("</svg>")
    return "\n".join(parts)


def render_category_accuracy_chart(result: dict[str, Any]) -> str:
    models = list(result["models"].items())
    categories = sorted(
        {
            category
            for _, model in models
            for category in model["test_category_analysis"]
        }
    )
    width = 1000
    row_height = 50
    height = 100 + (len(categories) * row_height)
    cell_width = 135
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        '<text x="30" y="36" font-family="Arial" font-size="24" font-weight="700" fill="#111827">Test Accuracy by Case Category</text>',
    ]
    for index, (model_name, _) in enumerate(models):
        x = 300 + (index * cell_width)
        parts.append(
            f'<text x="{x}" y="70" font-family="Arial" font-size="13" fill="#374151">{escape(_label(model_name))}</text>'
        )
    for row_index, category in enumerate(categories):
        y = 90 + (row_index * row_height)
        parts.append(
            f'<text x="30" y="{y + 27}" font-family="Arial" font-size="14" fill="#111827">{escape(_label(category))}</text>'
        )
        for model_index, (_, model) in enumerate(models):
            accuracy = float(model["test_category_analysis"][category]["accuracy"])
            x = 300 + (model_index * cell_width)
            shade = "#dcfce7" if accuracy == 1.0 else "#fee2e2"
            parts.extend(
                [
                    f'<rect x="{x}" y="{y + 5}" width="105" height="32" rx="5" fill="{shade}"/>',
                    f'<text x="{x + 34}" y="{y + 27}" font-family="Arial" font-size="14" font-weight="700" fill="#111827">{accuracy:.2f}</text>',
                ]
            )
    parts.append("</svg>")
    return "\n".join(parts)


def write_charts(result: dict[str, Any], output_dir: Path) -> list[Path]:
    chart_paths = [
        output_dir / "test_model_f1.svg",
        output_dir / "test_category_accuracy.svg",
    ]
    chart_paths[0].write_text(render_test_f1_chart(result), encoding="utf-8")
    chart_paths[1].write_text(render_category_accuracy_chart(result), encoding="utf-8")
    return chart_paths

