# chart_generator.py
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import List, Optional


class ChartGenerator:
    """Generates various charts and visualizations"""
    
    def __init__(self, time_periods: List[str]):
        self.time_periods = time_periods
    
    def create_power_consumption_chart(self, plot_df: pd.DataFrame) -> go.Figure:
        """Create power consumption over time chart"""
        fig = px.line(plot_df, x=plot_df.index, y="Total Load (W)", markers=True)
        fig.update_layout(
            xaxis_title="Time Period",
            yaxis_title="Power Consumption (W)",
            title="Power Consumption (W) Over Time",
            height=400
        )
        return fig
    
    def create_stacked_energy_chart(self, energy_df: pd.DataFrame) -> go.Figure:
        """Create stacked bar chart for energy by appliance"""
        stacked_fig = go.Figure()
        for appliance in energy_df["Appliance"]:
            stacked_fig.add_trace(go.Bar(
                name=appliance,
                x=self.time_periods,
                y=energy_df[energy_df["Appliance"] == appliance][self.time_periods].values[0]
            ))
        stacked_fig.update_layout(
            barmode='stack',
            xaxis_title="Time",
            yaxis_title="Wh Consumed",
            title="Energy Consumption by Appliance per Time Period (Including Use Time %)",
            height=450
        )
        return stacked_fig
    
    def create_daily_energy_bar_chart(self, df: pd.DataFrame) -> Optional[go.Figure]:
        """Create bar chart for daily energy consumption by appliance"""
        appliance_daily_energy = []
        appliance_names = []
        appliance_priorities = []

        for appliance in df["Appliance"]:
            daily_energy = df.loc[df["Appliance"] == appliance, "Total Daily Energy (Wh)"].values[0]
            if daily_energy > 0:
                appliance_names.append(appliance)
                appliance_daily_energy.append(daily_energy)
                priority = df.loc[df["Appliance"] == appliance, "Priority"].values[0]
                appliance_priorities.append(priority.lower())

        if not appliance_daily_energy:
            return None

        # Build per-priority series
        y_essential = [e if p == "essential" else 0 for e, p in zip(appliance_daily_energy, appliance_priorities)]
        y_medium = [e if p == "medium" else 0 for e, p in zip(appliance_daily_energy, appliance_priorities)]
        y_non_ess = [e if (p not in ["essential", "medium"]) else 0 for e, p in zip(appliance_daily_energy, appliance_priorities)]

        text_vals = [f"{e:.0f}" for e in appliance_daily_energy]
        text_ess = [t if p == "essential" else "" for t, p in zip(text_vals, appliance_priorities)]
        text_med = [t if p == "medium" else "" for t, p in zip(text_vals, appliance_priorities)]
        text_non = [t if (p not in ["essential", "medium"]) else "" for t, p in zip(text_vals, appliance_priorities)]

        fig_bar = go.Figure()

        fig_bar.add_trace(go.Bar(
            name="Essential",
            x=appliance_names, y=y_essential,
            marker_color="#FF6B6B",
            text=text_ess, textposition="outside",
            hovertemplate="<b>%{x}</b><br>Daily Energy: %{y:.0f} Wh<br>Daily Energy: %{customdata:.2f} kWh<br><extra></extra>",
            customdata=[e/1000 if p == "essential" else 0 for e, p in zip(appliance_daily_energy, appliance_priorities)],
            showlegend=True
        ))

        fig_bar.add_trace(go.Bar(
            name="Medium",
            x=appliance_names, y=y_medium,
            marker_color="#FFD93D",
            text=text_med, textposition="outside",
            hovertemplate="<b>%{x}</b><br>Daily Energy: %{y:.0f} Wh<br>Daily Energy: %{customdata:.2f} kWh<br><extra></extra>",
            customdata=[e/1000 if p == "medium" else 0 for e, p in zip(appliance_daily_energy, appliance_priorities)],
            showlegend=True
        ))

        fig_bar.add_trace(go.Bar(
            name="Non-Essential",
            x=appliance_names, y=y_non_ess,
            marker_color="#45B7D1",
            text=text_non, textposition="outside",
            hovertemplate="<b>%{x}</b><br>Daily Energy: %{y:.0f} Wh<br>Daily Energy: %{customdata:.2f} kWh<br><extra></extra>",
            customdata=[e/1000 if p not in ["essential", "medium"] else 0 for e, p in zip(appliance_daily_energy, appliance_priorities)],
            showlegend=True
        ))

        fig_bar.update_layout(
            title="Daily Energy Consumption by Appliance (Including Use Time %)",
            xaxis_title="Appliances",
            yaxis_title="Daily Energy Consumption (Wh)",
            height=600,
            xaxis_tickangle=-60,
            margin=dict(b=200),
            yaxis=dict(gridcolor="lightgray"),
            barmode="stack",
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5)
        )

        return fig_bar
    
    def create_time_series_chart(self, power_df: pd.DataFrame, title: str = "Power Consumption Time Series") -> go.Figure:
        """Create time series chart for individual appliances"""
        fig_timeseries = go.Figure()
        colors = px.colors.qualitative.Set3 + px.colors.qualitative.Pastel + px.colors.qualitative.Set1

        for i, appliance in enumerate(power_df["Appliance"]):
            appliance_data = power_df[power_df["Appliance"] == appliance][self.time_periods].values[0]
            if max(appliance_data) > 0:
                fig_timeseries.add_trace(go.Scatter(
                    x=self.time_periods,
                    y=appliance_data,
                    mode='lines+markers',
                    name=appliance,
                    line=dict(color=colors[i % len(colors)], width=2),
                    marker=dict(size=6),
                    hovertemplate=f'<b>{appliance}</b><br>' +
                                 'Time: %{x}<br>' +
                                 'Avg Power: %{y:.1f} W<br>' +
                                 '<extra></extra>'
                ))

        fig_timeseries.update_layout(
            title=title,
            xaxis_title="Time Period",
            yaxis_title="Power Consumption (W)",
            height=600,
            hovermode='x unified',
            legend=dict(orientation="v", yanchor="top", y=1, xanchor="left", x=1.02),
            margin=dict(r=200)
        )
        fig_timeseries.update_xaxes(showgrid=False)
        fig_timeseries.update_yaxes(showgrid=False)
        return fig_timeseries
    
    def create_comparison_chart(self, comparison_df: pd.DataFrame) -> go.Figure:
        """Create aggregated load profiles comparison chart"""
        fig_comparison = go.Figure()

        fig_comparison.add_trace(go.Scatter(
            x=comparison_df["Time Period"], y=comparison_df["All Appliances (Off-Grid)"],
            mode="lines+markers", name="All Appliances (Off-Grid)"
        ))

        fig_comparison.add_trace(go.Scatter(
            x=comparison_df["Time Period"], y=comparison_df["Essential + Medium (No Heating)"],
            mode="lines+markers", name="Essential + Medium (No Heating)"
        ))

        fig_comparison.add_trace(go.Scatter(
            x=comparison_df["Time Period"], y=comparison_df["Essentials Only"],
            mode="lines+markers", name="Essentials Only"
        ))

        fig_comparison.update_layout(
            title="Aggregated Load Profiles by Category",
            xaxis_title="Time Period",
            yaxis_title="Power Consumption (W)",
            hovermode="x unified",
            height=500
        )

        return fig_comparison