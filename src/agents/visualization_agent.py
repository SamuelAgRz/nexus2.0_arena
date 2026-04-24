
import pandas as pd
import matplotlib.pyplot as plt

class VisualizationAgent:
    def extract_table(self, dax_result: dict) -> pd.DataFrame:
        try:
            rows = dax_result["results"][0]["tables"][0]["rows"]
            return pd.DataFrame(rows)
        except Exception as exc:
            raise ValueError(f"Could not parse DAX result into a dataframe: {exc}") from exc

    def plot_bar(self, df: pd.DataFrame, x: str, y: str):
        ax = df.plot(x=x, y=y, kind="bar", figsize=(10, 5))
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        plt.show()
        return ax
