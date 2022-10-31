from typing import Union

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objs as go

from pynwb.base import TimeSeries, DynamicTable
from ipywidgets import widgets


def trialize_time_series(
    time_series: TimeSeries, trials_table: Union[DynamicTable, pd.DataFrame], index: int = 0
) -> pd.DataFrame:

    if isinstance(trials_table, DynamicTable):
        trials_table_df = trials_table.to_dataframe()
    else:
        trials_table_df = trials_table

    if time_series.timestamps:
        timestamps = time_series.timestamps[:]
    else:
        number_of_frames = time_series.data.shape[0]
        dt = 1.0 / time_series.rate
        time_offset = time_series.starting_time if time_series.starting_time else 0
        timestamps = np.arange(0, number_of_frames) * dt + time_offset

    trials_table_df = trials_table_df.reset_index().rename(columns={"id": "trial"})

    # Map timestamps to the trial interval (start_time, stop_time)
    start_times = trials_table_df.start_time.to_numpy()
    stop_times = trials_table_df.stop_time.to_numpy()
    larger_than_start_time = start_times[np.newaxis, :] < timestamps[:, np.newaxis]
    smaller_than_stop_time = timestamps[:, np.newaxis] <= stop_times[np.newaxis, :]
    timestamps_contained_in_trial = np.logical_and(larger_than_start_time, smaller_than_stop_time)
    # First dimension is timestamp index second dimension is trial table index
    data_index_within_trials, index_in_trial_table = np.nonzero(timestamps_contained_in_trial)

    # Check efficiency of accessing HDF5 with indexes
    data = time_series.data[data_index_within_trials, index]
    data_df = pd.DataFrame(dict(timestamps=timestamps[data_index_within_trials], data=data))

    # Create an start_time in the data table and merge withe the trial table using a left join operation
    data_df["start_time"] = [trials_table_df.start_time[index] for index in index_in_trial_table]
    data_df_trialized = pd.merge(left=data_df, right=trials_table_df, on="start_time", how="left")
    data_df_trialized["centered_timestamps"] = data_df_trialized.timestamps - data_df_trialized.start_time

    return data_df_trialized


def create_empty_figure():
    empty_figure = go.Figure()
    empty_figure.update_layout(
        xaxis={"visible": False},
        yaxis={"visible": False},
        annotations=[{"text": "No data", "xref": "paper", "yref": "paper", "showarrow": False, "font": {"size": 28}}],
    )

    return empty_figure


def calculate_moving_average_over_trials(df, moving_average_window):

    df_sort = df.sort_values(by="centered_timestamps")
    df_sort["moving_average"] = df_sort["data"].rolling(moving_average_window).mean()

    return df_sort


def add_moving_average_traces(figure, df, facet_col, facet_row):

    if facet_col is None and facet_row is None:
        num_trials = df["trial"].unique().size
        moving_average_window = 2 * num_trials
        df_sort = calculate_moving_average_over_trials(df, moving_average_window)

        figure.add_scattergl(
            x=df_sort.centered_timestamps,
            y=df_sort.moving_average,
            name="moving_average",
            line=dict(color="black", width=4),
        )
    elif facet_col is not None and facet_row is None:

        col_faceting_values = df[facet_col].dropna().unique()
        for col_index, col_face_value in enumerate(col_faceting_values):
            if isinstance(col_face_value, str):
                query_string = f"{facet_col}=='{col_face_value}'"
            else:
                query_string = f"{facet_col}=={col_face_value}"

            sub_df = df.query(query_string)
            # Calculate moving average
            num_trials = sub_df["trial"].unique().size
            moving_average_window = 2 * num_trials

            moving_average_df = calculate_moving_average_over_trials(sub_df, moving_average_window)

            figure.add_scattergl(
                x=moving_average_df.centered_timestamps,
                y=moving_average_df.moving_average,
                showlegend=False,
                line=dict(color="black", width=4),
                row=1,
                col=col_index + 1,
            )

    elif facet_col is None and facet_row is not None:

        row_faceting_values = df[facet_row].dropna().unique()
        row_faceting_values.sort()

        for row_index, row_face_value in enumerate(reversed(row_faceting_values)):
            if isinstance(row_face_value, str):
                query_string = f"{facet_row}=='{row_face_value}'"
            else:
                query_string = f"{facet_row}=={row_face_value}"

            sub_df = df.query(query_string)
            # Calculate moving average
            num_trials = sub_df["trial"].unique().size
            moving_average_window = 2 * num_trials

            moving_average_df = calculate_moving_average_over_trials(sub_df, moving_average_window)

            figure.add_scattergl(
                x=moving_average_df.centered_timestamps,
                y=moving_average_df.moving_average,
                showlegend=False,
                line=dict(color="black", width=4),
                row=row_index + 1,
                col=1,
            )
    else:
        col_faceting_values = df[facet_col].dropna().unique()
        row_faceting_values = df[facet_row].dropna().unique()
        for row_index, row_face_value in enumerate(reversed(row_faceting_values)):
            for col_index, col_face_value in enumerate(col_faceting_values):

                if isinstance(col_face_value, str):
                    col_query_string = f"{facet_col}=='{col_face_value}'"
                else:
                    col_query_string = f"{facet_col}=={col_face_value}"

                if isinstance(row_face_value, str):
                    row_query_string = f"{facet_row}=='{row_face_value}'"
                else:
                    row_query_string = f"{facet_row}=={row_face_value}"

                query_string = row_query_string + " and " + col_query_string

                sub_df = df.query(query_string)
                # Calculate moving average
                num_trials = sub_df["trial"].unique().size
                moving_average_window = 2 * num_trials

                moving_average_df = calculate_moving_average_over_trials(sub_df, moving_average_window)

                figure.add_scattergl(
                    x=moving_average_df.centered_timestamps,
                    y=moving_average_df.moving_average,
                    showlegend=False,
                    line=dict(color="black", width=4),
                    row=row_index + 1,
                    col=col_index + 1,
                )

    return figure


def build_faceting_figure(df, facet_col, facet_row, data_label="data"):
    faceting_values = [facet_row, facet_col]
    faceting_values = [value for value in faceting_values if value is not None]
    if faceting_values:
        values_to_sort_by = ["centered_timestamps"] + faceting_values
        df = df.dropna(subset=faceting_values).sort_values(by=values_to_sort_by)

    if df.empty:
        empty_figure = create_empty_figure()
        return empty_figure

    # Construct all the traces grouped by trial
    figure = px.line(df, x="centered_timestamps", y=data_label, color="trial", facet_col=facet_col, facet_row=facet_row)
    figure.update_traces(line_color="gray", line_width=1, showlegend=False)

    # Add moving average
    figure = add_moving_average_traces(figure, df, facet_col=facet_col, facet_row=facet_row)

    # Annotations
    figure.for_each_xaxis(lambda x: x.update(title=""))
    figure.for_each_yaxis(lambda y: y.update(title=""))
    figure.add_annotation(
        x=-0.075, y=0.5, textangle=270, text=f"{data_label}", xref="paper", yref="paper", showarrow=False
    )
    figure.add_annotation(x=0.5, y=-0.125, text="Centered timestamps (s)", xref="paper", yref="paper", showarrow=False)

    if facet_row is not None:
        figure.add_annotation(
            x=1.05, y=0.5, textangle=90, text=f"{facet_row}", xref="paper", yref="paper", showarrow=False
        )

    if facet_col is not None:
        figure.add_annotation(
            x=0.5, y=1.1, textangle=0, text=f"{facet_col}", xref="paper", yref="paper", showarrow=False
        )

    annotation_list = figure.layout.annotations
    valid_annotations = (annotation for annotation in annotation_list if "=" in annotation.text)
    for annotation in valid_annotations:
        annotation.text = annotation.text.split("=")[1]

    return figure


class TrializedTimeSeries(widgets.HBox):
    def __init__(self, time_series: TimeSeries, trials_table: DynamicTable = None):
        super().__init__()

        self.time_series = time_series
        self.data_dimensions = self.time_series.data.shape[1]
        self.trials_table = trials_table
        if self.trials_table is None:
            self.trials_table = time_series.get_ancestor("NWBFile").trials

        self.trials_table_df = self.trials_table.to_dataframe()

        # Labels to refer to data created by the widget. Should not collapse with the column names on the dynamic table
        self.data_label = "data_widget"
        self.trial_label = "trial_widget"
        self.timestamps_label = "timestamps"
        self.centered_timestamps_label = "centered_timestamps"

        self.available_columns = self.trials_table_df.columns

        invalid_columns = ["start_time", "stop_time"]
        invalid_columns += [self.data_label, self.trial_label, self.timestamps_label, self.centered_timestamps_label]
        get_indexed_column_name = lambda col: "_".join(col.name.split("_")[:-1])
        ragged_columns = [get_indexed_column_name(col) for col in self.trials_table.columns if "index" in col.name]
        invalid_columns += ragged_columns

        self.invalid_columns = invalid_columns

        self.columns_for_filtering = [
            column for column in self.trials_table_df.columns if column not in self.invalid_columns
        ]

        self.options_per_column = {
            column: list(self.trials_table_df[column].dropna().unique()) for column in self.columns_for_filtering
        }

        # Define widgets
        self.columns_for_filtering.append(None)
        self.select_filter_columns = widgets.SelectMultiple(
            options=self.columns_for_filtering,
            description="Col to filter",
            value=[None],
        )

        self.default_filter_widget = widgets.Select()
        self.filter_menu = widgets.VBox([self.default_filter_widget])

        self.faceting_column_selection = widgets.Dropdown(
            options=self.columns_for_filtering, description="col faceting"
        )
        self.faceting_row_selection = widgets.Dropdown(options=self.columns_for_filtering, description="row faceting")

        dimension_options = list(range(self.data_dimensions))
        self.data_column_selection = widgets.Dropdown(options=dimension_options, description="Data dim", value=0)

        self.plot_button = widgets.Button(description="Plot selection!")

        self.figure_widget = go.FigureWidget()

        # Set observers
        self.select_filter_columns.observe(self.update_filter_menu, names="value")
        self.select_filter_columns.observe(self.update_row_faceting, names="value")
        self.select_filter_columns.observe(self.update_column_faceting, names="value")

        # Register plotting button callback
        self.plot_button.on_click(self.update_plot_widget)

        # Create the structure
        self.control = widgets.VBox(
            [
                self.select_filter_columns,
                self.filter_menu,
                self.faceting_column_selection,
                self.faceting_row_selection,
                self.plot_button,
                self.data_column_selection,
            ]
        )
        self.children = [self.control, self.figure_widget]

    def update_filter_menu(self, change):
        selected_columns = self.select_filter_columns.value
        if selected_columns != (None,):
            selection_boxes = [
                widgets.Dropdown(options=self.options_per_column[column], description=column)
                for column in selected_columns
            ]
            self.filter_menu.children = tuple(selection_boxes)
        else:
            self.filter_menu.children = (self.default_filter_widget,)

    def update_row_faceting(self, change):
        non_selected_columns = list(set(self.columns_for_filtering).difference(self.select_filter_columns.value))

        self.faceting_row_selection.options = list(non_selected_columns) + [None]
        self.faceting_row_selection.value = None

    def update_column_faceting(self, change):
        non_selected_columns = list(set(self.columns_for_filtering).difference(self.select_filter_columns.value))
        self.faceting_column_selection.options = list(non_selected_columns) + [None]
        self.faceting_column_selection.value = None

    def query_expresion(self, children):
        if isinstance(children.value, str):
            return f" {children.description} == '{children.value}' "
        else:
            return f" {children.description} == {children.value} "

    def update_plot_widget(self, button_instance):

        # Load and prepare data
        self.trialized_data_df = trialize_time_series(
            time_series=self.time_series, trials_table=self.trials_table, index=self.data_column_selection.value
        )

        if self.filter_menu.children != (self.default_filter_widget,):
            query_string = "and".join([self.query_expresion(children) for children in self.filter_menu.children])
            df_query = self.trialized_data_df.query(query_string)
        else:
            query_string = ""
            df_query = self.trialized_data_df

        # Generate the plot
        facet_col = self.faceting_column_selection.value
        facet_row = self.faceting_row_selection.value
        figure = build_faceting_figure(df=df_query, facet_col=facet_col, facet_row=facet_row)

        # Update the widget
        with self.figure_widget.batch_update():
            self.figure_widget.update(layout_annotations=None)
            self.figure_widget.update(figure.to_dict(), overwrite=True)
