import math
import warnings
from typing import Union, Tuple, Dict, List

import matplotlib.pyplot as plt

from ..config import config, Config


# ================================================
# Helper Functions
# ================================================


def get_attr_value(
    attr: str, obj: dict, default: Union[Config, dict, bool, int, float, str, None]
):
    """Retrieves the value of the specified attribute from the given object.

    Parameters
    ----------
    attr : str
        The name of the attribute.
    obj : dict
        The object.
    default : Union[Config, dict, bool, int, float, str, None]
        The default value to return if the attribute is not found.

    Returns
    -------
    The value of the attribute, or the default value if the attribute is not found.
    """
    if isinstance(default, Config) or isinstance(default, dict):
        return obj.get(attr, default[attr])
    return obj.get(attr, default)


def create_config_dict(
    styles: Dict[str, str], attrs: List[Tuple[str, str]]
) -> Dict[str, str]:
    """Create a configuration dictionary based on the given styles and attributes.

    Parameters
    ----------
    styles : Dict[str, str]
        A dictionary containing the styles.
    attrs : List[Tuple[str, str]]
        A list of tuples representing the attributes.

    Returns
    -------
    Dict[str, str]
        The configuration dictionary.
    """

    # Create a dictionary comprehension that maps each key to the attribute value
    return {
        key: get_attr_value(attr, styles, config)
        for key, attr in attrs
        if get_attr_value(attr, styles, config) is not None
    }


# ================================================
# Configuration Constructors
# ================================================


# -------------------------------------
# Subplot Configuration
# -------------------------------------


def get_subplot_config(
    subplots: bool, n_charts: int = 1, max_cols: int = 1
) -> dict[str, int]:
    """Calculate the configuration for subplots in a figure.

    Parameters
    ----------
    subplots : bool
        Whether to show subplots.
    n_charts : int, optional (default=1)
        The number of charts.
    max_cols : int, optional (default=1)
        The maximum number of columns.

    Returns
    -------
    dict[str, int]
        The configuration for subplots, including the number of rows (nrows) and
        the number of columns (ncols).
    """

    nrows = 1
    ncols = 1

    if subplots:
        assert n_charts > 0, "The number of charts must be greater than 0."
        assert max_cols > 0, "The maximum number of columns must be greater than 0."
        # there are more subplots
        nrows = math.ceil(n_charts / max_cols)
        ncols = max_cols if n_charts >= max_cols else n_charts % max_cols

    return {"nrows": nrows, "ncols": ncols}


# -------------------------------------
# Text Style
# -------------------------------------


def get_text_style(text_type: str = "") -> dict:
    """Get the text configuration

    Parameters
    ----------
    text_type : str, optional (default="")
        The text type.

    Returns
    -------
    dict
        The text configuration dict.
    """

    config_attrs = [
        ("fontsize", "font.{type}.size"),
        ("fontweight", "font.{type}.weight"),
        ("color", "font.{type}.color"),
        ("style", "font.{type}.style"),
        ("family", "font.{type}.family"),
    ]

    return {
        key: config.get(
            attr.format(type=text_type),
            config.get(attr.format(type="general")),
        )
        for key, attr in config_attrs
    }


# -------------------------------------
# Line Style
# -------------------------------------


def get_line_style(chart_style: dict) -> dict:
    """Get the line configuration

    Parameters
    ----------
    chart_style : dict
        The chart style dictionary.

    Returns
    -------
    dict
        The line configuration dict.
    """

    config_attrs = [
        ("color", "plot.line.color"),
        ("alpha", "plot.line.alpha"),
        ("linewidth", "plot.line.width"),
        ("linestyle", "plot.line.style"),
        ("marker", "plot.line.marker"),
        ("drawstyle", "plot.line.drawstyle"),
        ("zorder", "plot.line.zorder"),
    ]

    return create_config_dict(chart_style, config_attrs)


# -------------------------------------
# Bar Style
# -------------------------------------


def get_bar_style(chart_style: dict, is_horizontal: bool = False) -> dict:
    """Get the bar configuration

    Parameters
    ----------
    chart_style : dict
        The chart style dictionary.
    is_horizontal : bool
        Whether the bar is horizontal or not.

    Returns
    -------
    dict
        The bar configuration dict.
    """

    config_attrs = [
        ("color", "plot.bar.color"),
        ("alpha", "plot.bar.alpha"),
        ("height" if is_horizontal else "width", "plot.bar.width"),
        ("hatch", "plot.bar.hatch"),
        ("linewidth", "plot.bar.edge.width"),
        ("edgecolor", "plot.bar.edge.color"),
        ("ecolor", "plot.bar.error.color"),
        ("zorder", "plot.bar.zorder"),
    ]

    return create_config_dict(chart_style, config_attrs)


# -------------------------------------
# Hist Style
# -------------------------------------


def get_hist_style(chart_style: dict) -> dict:
    """Get the hist configuration

    Parameters
    ----------
    chart_style : dict
        The chart style dictionary.

    Returns
    -------
    dict
        The hist configuration dict.
    """

    config_attrs = [
        ("color", "plot.hist.color"),
        ("alpha", "plot.hist.alpha"),
        ("fill", "plot.hist.fill"),
        ("hatch", "plot.hist.hatch"),
        ("zorder", "plot.hist.zorder"),
        ("histtype", "plot.hist.type"),
        ("align", "plot.hist.align"),
        ("linewidth", "plot.hist.edge.width"),
        ("edgecolor", "plot.hist.edge.color"),
    ]

    return create_config_dict(chart_style, config_attrs)


# -------------------------------------
# Area Style
# -------------------------------------


def get_area_style(chart_style: dict) -> dict:
    """Get the area configuration

    Parameters
    ----------
    chart_style : dict
        The chart style dictionary.

    Returns
    -------
    dict
        The area configuration dict.
    """

    config_attrs = [
        ("alpha", "plot.area.alpha"),
        ("color", "plot.area.color"),
        ("linewidth", "plot.area.line.width"),
        ("hatch", "plot.area.hatch"),
        ("zorder", "plot.area.zorder"),
    ]

    return create_config_dict(chart_style, config_attrs)


# -------------------------------------
# Grid Style
# -------------------------------------


def get_grid_style(chart_style: dict) -> dict:
    """Get the grid configuration

    Parameters
    ----------
    chart_style : dict
        The chart style dictionary.

    Returns
    -------
    dict
        The grid configuration dict.
    """

    config_attrs = [
        ("alpha", "plot.grid.alpha"),
        ("color", "plot.grid.color"),
        ("linewidth", "plot.grid.line.width"),
        ("linestyle", "plot.grid.line.style"),
        ("zorder", "plot.grid.zorder"),
    ]
    return create_config_dict(chart_style, config_attrs)


# -------------------------------------
# Legend Style
# -------------------------------------


def get_legend_style() -> dict:
    """Get the legend configuration

    Returns
    -------
    dict
        The legend configuration dict.
    """

    config_attrs = [
        ("shadow", "plot.legend.shadow"),
        ("frameon", "plot.legend.frameon"),
        ("fontsize", "plot.legend.font.size"),
        ("alignment", "plot.legend.alignment"),
        ("title_fontsize", "plot.legend.title.size"),
        ("labelcolor", "plot.legend.label.color"),
    ]
    return create_config_dict({}, config_attrs)


# ================================================
# Chart Configurations
# ================================================


def configure_axes_spines(ax: plt.Axes):
    """Configure axes spines.

    Parameters
    ----------
    ax : plt.Axes
        The axes.
    """

    # Turn on the axes
    ax.axis("on")

    # Loop through each axis and configure spines
    for axis in ["top", "bottom", "left", "right"]:
        # Set the linewidth and visibility of the spine
        ax.spines[axis].set(
            linewidth=config["axes.spines.width"],
            visible=config[f"axes.spines.{axis}.visible"],
            zorder=config["axes.spines.zorder"],
        )


def configure_axis_ticks_style(ax: plt.Axes, axis_type: str):
    """Configure axis ticks.

    Parameters
    ----------
    ax : plt.Axes
        The axes.
    axis_type : str
        The axis type. Options: "xaxis", "yaxis".
    """

    # Set tick parameters for major ticks
    getattr(ax, axis_type).set_tick_params(
        which="major",
        width=config["axes.spines.width"],
        length=config["axes.ticks.length"],
        labelsize=config["axes.ticks.label.size"],
    )


def configure_axis_ticks_position(ax: plt.Axes, chart: dict):
    """Configure axis ticks position

    Parameters
    ----------
    ax : plt.Axes
        The axes.
    chart : dict
        The chart style.
    """

    tick_attrs = [
        ("xticks", "xticklabels", "xaxis"),
        ("yticks", "yticklabels", "yaxis"),
    ]
    for attrs in tick_attrs:
        ticks = chart.get(attrs[0], None)
        ticklabels = chart.get(attrs[1], None)
        func = ax.set_xticks if attrs[2] == "xaxis" else ax.set_yticks

        if ticks is None and ticklabels is not None:
            warnings.warn(
                f"The attribute `{attrs[0]}` is not specified but `{attrs[1]}` is. "
                + f"Please provide the `{attrs[0]}` values."
            )
            continue
        elif ticks is not None:
            if ticklabels is None:
                # draw only the ticks
                func(ticks)
            elif len(ticks) != len(ticklabels):
                warnings.warn(
                    f"The values of `{attrs[0]}` and `{attrs[1]}` are of different lengths. "
                    + f"Please provide the same number of values. Ignoring `{attrs[1]}` values..."
                )
                # draw only the ticks
                func(ticks)
            else:
                # draw both the ticks and the labels
                func(ticks, labels=ticklabels)


def configure_axis_limits(ax: plt.Axes, settings: dict):
    """Configure axis limits.

    Parameters
    ----------
    ax : plt.Axes
        The axes.

    settings : dict
        The settings.
    """

    if settings["x_min"] is not None or settings["x_max"] is not None:
        xmin, xmax = ax.get_xlim()
        xmin = settings["x_min"] if settings["x_min"] is not None else xmin
        xmax = settings["x_max"] if settings["x_max"] is not None else xmax
        ax.set_xlim(xmin=xmin, xmax=xmax)

    if settings["y_min"] is not None or settings["y_max"] is not None:
        ymin, ymax = ax.get_ylim()
        ymin = settings["y_min"] if settings["y_min"] is not None else ymin
        ymax = settings["y_max"] if settings["y_max"] is not None else ymax
        ax.set_ylim(ymin=ymin, ymax=ymax)


def configure_labels(settings: dict, actions: List[Tuple[str, callable]]):
    """Configure chart labels.

    Parameters
    ----------
    settings : dict
        The chart settings.
    actions : List[Tuple[str, callable]]
        The actions.
    """

    for label, action in actions:
        if label in settings:
            action(settings[label], **get_text_style(label))
