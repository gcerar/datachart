import json
import warnings

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

from utils.colors import create_color_cycle
from utils.stats import get_min_max_values
from utils.attrs import (
    configure_axes_spines,
    configure_axis_ticks,
    get_subplot_config,
    get_attr_value,
    get_area_config,
    get_grid_config,
    get_text_config,
    get_line_config,
    get_bar_config,
    get_hist_config,
)

from typing import List

from schema.constants import Figsize

from config import config

# ================================================
# Helper Functions
# ================================================


def get_chart_data(attr: str, chart: dict) -> np.array:
    """
    Generate a numpy array of data from a given chart dictionary.

    Parameters:
        attr (str): The attribute to extract from the chart data.
        chart (dict): The chart dictionary containing the data.

    Returns:
        np.array: An array of values extracted from the chart data, or None if no values are found.
    """
    attr_label = get_attr_value(attr, chart, attr)

    if isinstance(chart["data"], dict):
        return chart["data"][attr_label] if attr_label in chart["data"] else None

    if isinstance(chart["data"], list):
        data = np.array([d[attr_label] for d in chart["data"] if attr_label in d])
        return data if len(data) > 0 else None

    return None


def assert_chart_config(chart_config: dict, supported_chart_config: List[str]) -> None:
    """Assert that the chart config is supported."""
    for key, val in chart_config.items():
        if key not in supported_chart_config and val:
            warnings.warn(
                f"Warning: chart_config['{key}'] is present but is not supported. Ignoring flag..."
            )


def custom_color_cycle(as_subplots: bool, n_charts: int):
    # get the color cycle
    color_name = (
        config["color.general.singular"]
        if as_subplots
        else config["color.general.multiple"]
    )
    max_colors = 1 if as_subplots else n_charts
    return create_color_cycle(color_name, max_colors)


# ================================================
# Main Chart Wrapper Definition
# ================================================


def chart_wrapper(func):
    def wrapper(attrs):
        # check how many data point are there
        if not isinstance(attrs["charts"], dict) and not isinstance(
            attrs["charts"], list
        ):
            raise ValueError("Parameter `attrs['charts']` is not correctly structured")

        # retrieve attributes
        charts = attrs.get("charts")

        title = attrs.get("title", None)
        xlabel = attrs.get("xlabel", None)
        ylabel = attrs.get("ylabel", None)
        figsize = attrs.get("figsize", Figsize.DEFAULT)

        sharex = attrs.get("sharex", False)
        sharey = attrs.get("sharey", False)
        max_cols = attrs.get("max_cols", 4)
        show_grid = attrs.get("show_grid", None)
        as_subplots = attrs.get("as_subplots", False)

        # common draw configuration
        show_xaxis_labels = attrs.get("show_xaxis_labels", True)
        show_yaxis_labels = attrs.get("show_yaxis_labels", True)
        show_yerr = attrs.get("show_yerr", None)

        # line chart draw configuration
        show_area = attrs.get("show_area", None)

        # bar chart draw configuration
        orientation = attrs.get("orientation", None)

        # hist chart draw configuration
        n_bins = attrs.get("n_bins", None)

        # format the data into a 1D array
        charts = charts if isinstance(charts, list) else [charts]
        charts = np.array(charts)

        # get the number of rows and columns of the chart
        subplot_config = get_subplot_config(
            as_subplots, n_charts=charts.shape[0], max_cols=max_cols
        )

        figure, axes = plt.subplots(
            **subplot_config,
            figsize=figsize,
            sharex=sharex,
            sharey=sharey,
            squeeze=False,
            constrained_layout=True,
        )

        # prepare the axes based on the draw type
        axes = (
            [axes[0, 0] for _ in range(charts.shape[0])]
            if not as_subplots
            else axes.flatten()
        )

        # hide all axes
        for ax in axes:
            ax.axis("off")

        for chart, ax in zip(charts, axes):
            # configure the axes and their ticks
            configure_axes_spines(ax, config)
            configure_axis_ticks(
                ax, config, "xaxis"
            ) if show_xaxis_labels else ax.xaxis.set_visible(False)
            configure_axis_ticks(
                ax, config, "yaxis"
            ) if show_yaxis_labels else ax.yaxis.set_visible(False)

            # graph configuration using actions
            config_actions = [
                ("subtitle", ax.set_title),
                ("xlabel", ax.set_xlabel),
                ("ylabel", ax.set_ylabel),
            ]

            for attr, action in config_actions:
                if attr in chart:
                    action(chart[attr], **get_text_config(config, attr))

        # draw the charts
        func(
            axes,
            charts,
            chart_config={
                # common chart configuration
                "as_subplots": as_subplots,
                "grid": show_grid,
                "yerr": show_yerr,
                # line chart configuration
                "area": show_area,
                # bar chart configuration
                "orientation": orientation,
                # hist chart configuration
                "n_bins": n_bins,
            },
        )

        # add the title of the figure
        if title:
            figure.suptitle(title, **get_text_config(config, "title"))

        if xlabel:
            figure.text(
                0.5, -0.03, xlabel, ha="center", **get_text_config(config, "xlabel")
            )

        if ylabel:
            figure.text(
                -0.03,
                0.5,
                ylabel,
                va="center",
                rotation="vertical",
                **get_text_config(config, "ylabel"),
            )

        plt.show()

    return wrapper


# ================================================
# Draw Line Chart
# ================================================


def draw_line_chart(
    axes: List[plt.Axes],
    charts: List[dict],
    chart_config: dict,
) -> None:
    """Draw a line chart

    Args:
        axes: The axes.
        charts: The charts data.
        chart_config: The draw config.
    """

    # assert the configuration
    assert_chart_config(
        chart_config=chart_config,
        supported_chart_config=["as_subplots", "grid", "yerr", "area"],
    )

    # get the color cycle
    color_cycle = custom_color_cycle(chart_config["as_subplots"], n_charts=len(charts))

    for idx, (chart, ax) in enumerate(zip(charts, axes)):
        # get the chart style attributes
        style = chart.get("style", {})

        # retrieve the chart data points
        x = get_chart_data("x", chart)
        y = get_chart_data("y", chart)
        yerr = get_chart_data("yerr", chart)

        draw_yerr_flag = (
            chart_config["yerr"]
            and isinstance(yerr, np.ndarray)
            and len(yerr) == len(y)
        )
        draw_area_flag = chart_config["area"]

        if draw_yerr_flag and draw_area_flag:
            warnings.warn(
                "Warning: Both the `error area` and `area under the curve` will be drawn. "
                + "Only one of `yerr` and `area` should be True."
            )
        # get style configuration
        chart_hash = hash(json.dumps(chart, sort_keys=True))
        line_config = {**color_cycle[chart_hash], **get_line_config(style)}
        area_config = {**color_cycle[chart_hash], **get_area_config(style)}

        if draw_yerr_flag:
            # draw the confidence interval around the line
            y_min = y - yerr
            y_max = y + yerr
            ax.fill_between(x, y_min, y_max, **area_config)

        if draw_area_flag:
            # draw the area under the line
            step = (
                line_config["drawstyle"].split("-")[1]
                if "steps-" in line_config["drawstyle"]
                else None
            )
            ax.fill_between(x, y, step=step, **area_config)

        # draw the line chart
        ax.plot(x, y, **line_config)

        if chart_config["grid"]:
            # show the chart grid
            ax.grid(axis=chart_config["grid"], **get_grid_config(style))

        # set the x-axis limit
        xmin, xmax = get_min_max_values(x)
        ax.set_xlim(xmin, xmax)


# ================================================
# Draw Bar Chart
# ================================================


def draw_bar_chart(
    axes: List[plt.Axes],
    charts: List[dict],
    chart_config: dict,
) -> None:
    """Draw a bar chart

    Args:
        axes: The axes.
        charts: The charts data.
        draw_config: The draw flags.
    """

    # assert the configuration
    assert_chart_config(
        chart_config=chart_config,
        supported_chart_config=["as_subplots", "grid", "yerr", "orientation"],
    )

    # preliminary variables
    x_start = get_chart_data("label", charts[0])
    x_start = np.arange(len(x_start))
    x_width = config["plot.bar.width"] / len(charts)  # the width of the bar
    offset = 0

    is_horizontal = chart_config.get("orientation", "vertical") == "horizontal"

    # get the color cycle
    color_cycle = custom_color_cycle(chart_config["as_subplots"], n_charts=len(charts))

    for idx, (chart, ax) in enumerate(zip(charts, axes)):
        # get the chart style attributes
        style = chart.get("style", {})

        # retrieve the chart data points
        y = get_chart_data("y", chart)
        yerr = get_chart_data("yerr", chart)
        labels = get_chart_data("label", chart)

        # assign the x-axis values
        x = np.arange(len(labels))

        chart_hash = hash(json.dumps(chart, sort_keys=True))
        bar_config = {**color_cycle[chart_hash], **get_bar_config(style, is_horizontal)}
        if not chart_config["as_subplots"]:
            # update the configuration and offset
            bar_config["height" if is_horizontal else "width"] = x_width
            offset = idx * x_width

        # draw the bar chart
        draw_func = ax.barh if is_horizontal else ax.bar
        error_values = {
            "xerr" if is_horizontal else "yerr": yerr if chart_config["yerr"] else None
        }

        draw_func(
            x + offset,
            y,
            label=labels,
            **error_values,
            **bar_config,
        )

        if chart_config["grid"]:
            # show the chart grid
            ax.grid(axis=chart_config["grid"], **get_grid_config(chart))

        # ---------------------------------------
        # Assign the tick position
        # ---------------------------------------

        def rotate_bar_labels(n_labels: int):
            """Rotate the bar labels based on the number of labels."""
            if chart_config["as_subplots"]:
                # rotate based on the number of labels
                return 90 if n_labels >= 7 else (45 if n_labels >= 4 else 0)
            # do not rotate the labels
            return 0

        def update_group_bar_labels(
            ticks_loc: List[float], labels: List[str], axis: str
        ):
            """Update the group bar labels on the specified axis."""
            if axis == "x":
                ax.set_xticks(ticks_loc, labels)
                ax.xaxis.set_major_locator(mticker.FixedLocator(ticks_loc))
                ax.set_xticklabels(labels, rotation=rotate_bar_labels(len(labels)))
            elif axis == "y":
                ax.set_yticks(ticks_loc, labels)
                ax.yaxis.set_major_locator(mticker.FixedLocator(ticks_loc))

        # get the tic positions
        ticks_loc = (
            x_start + (len(charts) - 1) / 2 * x_width
            if not chart_config["as_subplots"]
            else x
        )
        update_group_bar_labels(ticks_loc, labels, axis="y" if is_horizontal else "x")

        # ---------------------------------------
        # ! Overwrite the label positions
        # ---------------------------------------

        # graph configuration using actions
        config_actions = [
            ("subtitle", ax.set_title),
            ("xlabel", ax.set_xlabel if not is_horizontal else ax.set_ylabel),
            ("ylabel", ax.set_ylabel if not is_horizontal else ax.set_xlabel),
        ]

        for attr, action in config_actions:
            if attr in chart:
                action(chart[attr], **get_text_config(config, attr))

    # ---------------------------------------
    # Assign the axis limit
    # ---------------------------------------

    if not chart_config["as_subplots"]:
        axes[0].set_xlim(left=0) if is_horizontal else axes[0].set_ylim(bottom=0)


# ================================================
# Draw Histogram Chart
# ================================================


def draw_hist_chart(
    axes: List[plt.Axes],
    charts: List[dict],
    chart_config: dict,
) -> None:
    """Draw a bar chart

    Args:
        axes: The axes.
        charts: The charts data.
        draw_config: The draw flags.
    """

    # assert the configuration
    assert_chart_config(
        chart_config=chart_config,
        supported_chart_config=["as_subplots", "grid", "n_bins", "orientation"],
    )

    # get the chart settings
    orientation = chart_config.get("orientation", "vertical")
    n_bins = chart_config.get("n_bins", 20)

    # normalize the bin size for all charts
    x_all = [get_chart_data("x", chart) for chart in charts]
    bins = np.histogram(np.hstack(tuple(x_all)), bins=n_bins)[1]

    # get the color cycle
    color_cycle = custom_color_cycle(chart_config["as_subplots"], n_charts=len(charts))

    if not chart_config["as_subplots"]:
        # visualize all charts in a common subplot
        hist_config = [
            {
                **color_cycle[hash(json.dumps(chart, sort_keys=True))],
                **get_hist_config(chart.get("style", {})),
            }
            for chart in charts
        ]
        color = [c["color"] for c in hist_config]

        hist_config = {
            **hist_config[0],
            "color": None if color.count(None) > 0 else color,
        }

        # draw the histogram chart
        axes[0].hist(
            x_all,
            bins=bins,
            orientation=orientation,
            stacked=True,
            **hist_config,
        )
        if chart_config["grid"]:
            # show the chart grid
            axes[0].grid(axis=chart_config["grid"], **get_grid_config(charts[0]))

    else:
        # visualize each chart in a separate subplot
        for chart, ax in zip(charts, axes):
            # get the chart style attributes
            style = chart.get("style", {})

            # retrieve the chart data points
            x = get_chart_data("x", chart)
            density = get_chart_data("density", chart)
            cumulative = get_chart_data("cumulative", chart)

            chart_hash = hash(json.dumps(chart, sort_keys=True))
            hist_config = {**color_cycle[chart_hash], **get_hist_config(style)}

            # draw the histogram chart
            ax.hist(
                x,
                bins=bins,
                density=density,
                cumulative=cumulative,
                orientation=orientation,
                stacked=not chart_config["as_subplots"],
                **hist_config,
            )

            if chart_config["grid"]:
                # show the chart grid
                ax.grid(axis=chart_config["grid"], **get_grid_config(chart))
