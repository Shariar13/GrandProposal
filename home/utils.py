from typing import List
import matplotlib.pyplot as plt
import pandas as pd
import os


class TableGenerator:
    """
    Generates HTML tables for web display and matplotlib charts for export.
    """

    # =========================
    # HTML TABLES
    # =========================
    @staticmethod
    def generate_objectives_table(objectives: List[str]) -> str:
        rows = ''.join([f'<tr><td>{i}</td><td>{obj}</td></tr>' for i, obj in enumerate(objectives, 1)])
        return f'''
<table class="academic-table">
<thead><tr><th>Obj. #</th><th>Description</th></tr></thead>
<tbody>{rows}</tbody>
</table>'''

    @staticmethod
    def generate_timeline_table() -> str:
        return '''
<table class="academic-table">
<thead><tr><th>Phase</th><th>Timeline</th><th>Key Deliverables</th></tr></thead>
<tbody>
<tr><td>Phase 1</td><td>Months 1-12</td><td>Prototype, Dataset, Tech Report</td></tr>
<tr><td>Phase 2</td><td>Months 13-24</td><td>Experiments, Publications, System</td></tr>
<tr><td>Phase 3</td><td>Months 25-36</td><td>Validation, Deployment, Final Report</td></tr>
</tbody>
</table>'''

    @staticmethod
    def generate_budget_table() -> str:
        return '''
<table class="academic-table">
<thead><tr><th>Category</th><th>Percentage</th><th>Justification</th></tr></thead>
<tbody>
<tr><td>Personnel</td><td>60%</td><td>PI + 2 Grad Students</td></tr>
<tr><td>Equipment & Computing</td><td>20%</td><td>HPC, Software, Hardware</td></tr>
<tr><td>Travel & Conferences</td><td>10%</td><td>Dissemination</td></tr>
<tr><td>Other Direct Costs</td><td>10%</td><td>Publications, Data</td></tr>
</tbody>
</table>'''

    @staticmethod
    def generate_risk_table() -> str:
        return '''
<table class="academic-table">
<thead><tr><th>Risk</th><th>Level</th><th>Mitigation Strategy</th></tr></thead>
<tbody>
<tr><td>Technical challenges</td><td>Medium</td><td>Iterative development, alternatives</td></tr>
<tr><td>Resource constraints</td><td>Low</td><td>Cloud computing, HPC access</td></tr>
<tr><td>Timeline delays</td><td>Medium</td><td>Buffer periods, agile approach</td></tr>
<tr><td>Personnel turnover</td><td>Low</td><td>Cross-training, documentation</td></tr>
</tbody>
</table>'''

    # =========================
    # CHARTS FOR EXPORT
    # =========================
    @staticmethod
    def generate_budget_chart(path: str = "budget_chart.png"):
        categories = ["Personnel", "Equipment", "Travel", "Other"]
        percentages = [60, 20, 10, 10]
        plt.figure(figsize=(6, 6))
        plt.pie(percentages, labels=categories, autopct="%1.1f%%", startangle=140)
        plt.title("Budget Allocation")
        plt.savefig(path, bbox_inches="tight")
        plt.close()
        return os.path.abspath(path)

    @staticmethod
    def generate_timeline_chart(path: str = "timeline_chart.png"):
        df = pd.DataFrame({
            "Phase": ["Phase 1", "Phase 2", "Phase 3"],
            "Start": [1, 13, 25],
            "End": [12, 24, 36],
        })
        plt.figure(figsize=(8, 4))
        for i, row in df.iterrows():
            plt.barh(row["Phase"], row["End"] - row["Start"], left=row["Start"])
        plt.xlabel("Months")
        plt.ylabel("Phases")
        plt.title("Project Timeline (Gantt Style)")
        plt.savefig(path, bbox_inches="tight")
        plt.close()
        return os.path.abspath(path)


class TextHelper:
    """Helper for text formatting and analysis"""

    @staticmethod
    def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
        """Truncate text safely for table cells."""
        if len(text) <= max_length:
            return text
        return text[: max_length - len(suffix)] + suffix

    @staticmethod
    def format_list(items: List[str], conjunction: str = "and") -> str:
        """Format a list into human-readable string."""
        if not items:
            return ""
        if len(items) == 1:
            return items[0]
        if len(items) == 2:
            return f"{items[0]} {conjunction} {items[1]}"
        return ", ".join(items[:-1]) + f", {conjunction} {items[-1]}"

    @staticmethod
    def word_count(text: str) -> int:
        """Count words in text."""
        return len(text.split())

    @staticmethod
    def estimate_pages(text: str, words_per_page: int = 400) -> int:
        """Estimate number of pages based on word count."""
        words = TextHelper.word_count(text)
        return max(1, (words + words_per_page - 1) // words_per_page)

    @staticmethod
    def reading_time(text: str, wpm: int = 250) -> str:
        """Estimate reading time in minutes for given text."""
        words = TextHelper.word_count(text)
        minutes = max(1, words // wpm)
        return f"~{minutes} min read"