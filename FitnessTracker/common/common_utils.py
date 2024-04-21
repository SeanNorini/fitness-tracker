import matplotlib
import numpy as np
from matplotlib.ticker import MaxNLocator, MultipleLocator
import base64

matplotlib.use("Agg")
from matplotlib import pyplot as plt
from io import BytesIO
import base64
import pandas as pd
import matplotlib.dates as mdates


class Graph:
    def __init__(self, graph_data, y_label, kind, start=None, end=None):
        self.graph_data = graph_data
        self.start = start
        self.end = end
        self.y_label = y_label
        self.kind = kind

    def plot_graph(self):
        if self.kind == "bar":
            self.add_start_end_dates_to_graph_data()

        df = pd.DataFrame(
            {
                "Date": self.graph_data["dates"],
                self.y_label: self.graph_data[self.y_label],
            }
        )

        df_full = self.fill_date_indexes(df)
        self.configure_graph_settings(plt, df_full, self.y_label)
        img_base64 = Graph.convert_to_img_base64(plt)
        plt.close()

        return img_base64

    def add_start_end_dates_to_graph_data(self):
        """Adds start and end dates to graph_data if they don't exist"""
        if not self.graph_data["dates"]:
            self.graph_data.update(
                {"dates": [self.start, self.end], self.y_label: [0, 0]}
            )
            return

        if self.graph_data["dates"][0] != self.start:
            self.graph_data["dates"].insert(0, self.start)
            self.graph_data[self.y_label].insert(0, 0)
        if self.graph_data["dates"][-1] != self.end:
            self.graph_data["dates"].append(self.end)
            self.graph_data[self.y_label].append(0)

    def fill_date_indexes(self, df):
        """Fills date index with any missing dates"""
        df.set_index("Date", inplace=True)
        if self.kind == "bar":
            start_date = df.index.min()
            end_date = df.index.max()
            full_date_range = pd.date_range(start=start_date, end=end_date)
            return df.reindex(full_date_range, fill_value=0)
        return df

    def configure_graph_settings(self, plt, df_full, y_label):
        """Configures graph display"""
        plt.figure(figsize=(10, 6))

        if self.kind == "bar":
            df_full[y_label].plot(kind="bar", width=0.8, color="skyblue")
        else:
            df_full[y_label].plot(kind="line", color="skyblue")

        ax = plt.gca()
        if df_full.empty:
            plt.text(
                0.5,
                0.5,
                "No Data",
                fontsize=20,
                ha="center",
                va="center",
                color="#f5f5f5",
                transform=plt.gca().transAxes,
            )
        else:
            self.set_xticks(df_full, ax)
            plt.xticks(
                rotation=45,
                color="#f5f5f5",
                fontsize=24,
            )
            plt.yticks(color="#f5f5f5", fontsize=14)
            ax.tick_params(axis="y", labelsize=24, colors="#f5f5f5")
            ax.yaxis.set_major_locator(MaxNLocator(10))

        plt.gcf().set_facecolor("#212121")
        plt.ylabel(y_label, color="#f5f5f5", fontsize=24)
        ax.set_facecolor("#212121")
        for spine in ax.spines.values():
            spine.set_edgecolor("#f5f5f5")

        plt.tight_layout()

    def set_xticks(self, df, ax):
        min_y, max_y = min(df[self.y_label]), max(df[self.y_label])
        if self.kind == "bar":
            ax.set_xticklabels([date.strftime("%m/%d") for date in df.index])
            if max_y == 0:
                ax.set_ylim(0, 5)
            if len(df) > 7:
                ax.xaxis.set_major_locator(MaxNLocator(10))
        else:
            max_y = 150 if max_y == 0 else max_y
            ax.set_ylim(max(0, min_y * 0.8), max_y * 1.20)
            ax.xaxis.set_major_locator(mdates.AutoDateLocator())
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%m/%d"))

    @staticmethod
    def convert_to_img_base64(plt):
        """Convert graph to base64 to insert on page with javascript"""
        buffer = BytesIO()
        plt.savefig(buffer, format="png", transparent=True)
        buffer.seek(0)
        img_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
        return img_base64

    @staticmethod
    def plot_pie_chart(labels, sizes):
        plt.figure(figsize=(6, 6))
        colors = ["#ff9999", "#66b3ff", "#99ff99"]

        patches, texts, autotexts = plt.pie(
            sizes, labels=labels, colors=colors, autopct="%1.1f%%", startangle=90
        )
        for text in texts:
            text.set_fontsize(24)
            text.set_color("white")

        for autotext in autotexts:
            autotext.set_fontsize(24)

        plt.axis("equal")

        return Graph.convert_to_img_base64(plt)


def is_base64(s):
    """Check if a string is a valid base64 encoded."""
    try:
        if not isinstance(s, str):
            return False

        base64.b64decode(s, validate=True)
        return True
    except ValueError:
        return False
