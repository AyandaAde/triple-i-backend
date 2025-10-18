import base64
import io
from typing import Dict, Any, List, Optional
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Wedge
import numpy as np


def create_default_workforce_pie_chart(workforce_data: List[Dict[str, Any]]) -> str:
    if not workforce_data:

        # Create empty chart
        fig, ax = plt.subplots(figsize=(6, 6))
        ax.text(0.5, 0.5, 'No Data Available', ha='center', va='center', 
                transform=ax.transAxes, fontsize=14, color='gray')
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
    else:
        labels = [item.get("gender", "Unknown") for item in workforce_data]
        sizes = [item.get("employee_count", 0) for item in workforce_data]
        
        # Filter out zero values
        non_zero_data = [(label, size) for label, size in zip(labels, sizes) if size > 0]
        if not non_zero_data:
            fig, ax = plt.subplots(figsize=(6, 6))
            ax.text(0.5, 0.5, 'No Data Available', ha='center', va='center', 
                    transform=ax.transAxes, fontsize=14, color='gray')
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')
        else:
            labels, sizes = zip(*non_zero_data)
            
            fig, ax = plt.subplots(figsize=(6, 6))
            colors = ['#4C78A8', '#59A14F', '#E74C3C', '#F39C12', '#9B59B6', '#1ABC9C']
            
            wedges, texts, autotexts = ax.pie(
                sizes, 
                labels=labels, 
                autopct='%1.1f%%',
                colors=colors[:len(sizes)],
                startangle=90,
                wedgeprops=dict(width=0.4)
            )
            
            # Create donut hole
            centre_circle = plt.Circle((0, 0), 0.70, fc='white')
            fig.gca().add_artist(centre_circle)
            
            ax.set_title('Workforce by Gender', fontsize=14, fontweight='bold', pad=20)
            
            # Style the text
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
                autotext.set_fontsize(10)
    
    plt.tight_layout()
    return _fig_to_base64_png(fig)


def create_default_training_hours_chart(training_data: List[Dict[str, Any]]) -> str:

    if not training_data:
        # Create empty chart
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.text(0.5, 0.5, 'No Data Available', ha='center', va='center', 
                transform=ax.transAxes, fontsize=14, color='gray')
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
    else:
        labels = [item.get("gender", "Unknown") for item in training_data]
        values = [float(item.get("total_training_hours", 0.0)) for item in training_data]
        
        # Filter out zero values
        non_zero_data = [(label, value) for label, value in zip(labels, values) if value > 0]
        if not non_zero_data:
            fig, ax = plt.subplots(figsize=(8, 5))
            ax.text(0.5, 0.5, 'No Data Available', ha='center', va='center', 
                    transform=ax.transAxes, fontsize=14, color='gray')
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')
        else:
            labels, values = zip(*non_zero_data)
            
            fig, ax = plt.subplots(figsize=(8, 5))
            bars = ax.bar(labels, values, color='#4C78A8', alpha=0.8, edgecolor='#2E5B8A', linewidth=1)
            
            # Add value labels on bars
            for bar, value in zip(bars, values):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + max(values)*0.01,
                       f'{value:.1f}h', ha='center', va='bottom', fontweight='bold')
            
            ax.set_title('Total Training Hours by Gender', fontsize=14, fontweight='bold', pad=20)
            ax.set_xlabel('Gender', fontsize=12, fontweight='bold')
            ax.set_ylabel('Total Training Hours', fontsize=12, fontweight='bold')
            ax.grid(axis='y', linestyle='--', alpha=0.3)
            
            # Style the plot
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_linewidth(0.5)
            ax.spines['bottom'].set_linewidth(0.5)
    
    plt.tight_layout()
    return _fig_to_base64_png(fig)


def create_default_trend_chart(current_value: float, prior_value: Optional[float], title: str = "Training Hours Trend") -> str:

    if prior_value is None:
        # Create single value chart
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.text(0.5, 0.5, 'No Historical Data Available', ha='center', va='center', 
                transform=ax.transAxes, fontsize=14, color='gray')
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
    else:
        fig, ax = plt.subplots(figsize=(6, 4))
        
        periods = ['Prior Period', 'Current Period']
        values = [prior_value, current_value]
        colors = ['#A0A0A0', '#59A14F']
        
        bars = ax.bar(periods, values, color=colors, alpha=0.8, edgecolor='black', linewidth=1)
        
        # Add value labels on bars
        for bar, value in zip(bars, values):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + max(values)*0.01,
                   f'{value:.1f}', ha='center', va='bottom', fontweight='bold')
        
        # Calculate percentage change
        if prior_value > 0:
            change_pct = ((current_value - prior_value) / prior_value) * 100
            change_text = f"Change: {change_pct:+.1f}%"
            change_color = 'green' if change_pct >= 0 else 'red'
            ax.text(0.5, 0.95, change_text, ha='center', va='top', 
                   transform=ax.transAxes, fontsize=12, fontweight='bold', color=change_color)
        
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
        ax.set_ylabel('Value', fontsize=12, fontweight='bold')
        ax.grid(axis='y', linestyle='--', alpha=0.3)
        
        # Style the plot
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_linewidth(0.5)
        ax.spines['bottom'].set_linewidth(0.5)
    
    plt.tight_layout()
    return _fig_to_base64_png(fig)


def create_default_kpi_summary_chart(kpi_data: Dict[str, Any]) -> str:

    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Extract key metrics
    metrics = []
    values = []
    
    # Disability percentage
    disability = kpi_data.get("Percentage of Employees with Disabilities", {})
    if disability and disability.get("overall_percentage"):
        metrics.append("Disability %")
        values.append(disability["overall_percentage"])
    
    # Turnover rate
    turnover = kpi_data.get("Employee Turnover Rate", {})
    if turnover and turnover.get("overall_turnover_rate"):
        metrics.append("Turnover Rate %")
        values.append(turnover["overall_turnover_rate"])
    
    # Training hours
    training = kpi_data.get("Average Training Hours per Employee", {})
    if training and training.get("overall_average_hours"):
        metrics.append("Avg Training Hours")
        values.append(training["overall_average_hours"])
    
    # Injury rate
    injury = kpi_data.get("Workplace Injury Rate", {})
    if injury and injury.get("overall_injury_rate"):
        metrics.append("Injury Rate")
        values.append(injury["overall_injury_rate"])
    
    if not metrics:
        ax.text(0.5, 0.5, 'No KPI Data Available', ha='center', va='center', 
                transform=ax.transAxes, fontsize=14, color='gray')
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
    else:
        max_val = max(values) if values else 1
        normalized_values = [v / max_val * 100 for v in values]
        
        bars = ax.barh(metrics, normalized_values, color='#4C78A8', alpha=0.8)
        
        # Add value labels
        for i, (bar, value) in enumerate(zip(bars, values)):
            width = bar.get_width()
            ax.text(width + 1, bar.get_y() + bar.get_height()/2, 
                   f'{value:.1f}', ha='left', va='center', fontweight='bold')
        
        ax.set_title('Key Performance Indicators Summary', fontsize=14, fontweight='bold', pad=20)
        ax.set_xlabel('Normalized Values (%)', fontsize=12, fontweight='bold')
        ax.grid(axis='x', linestyle='--', alpha=0.3)
        
        # Style the plot
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_linewidth(0.5)
        ax.spines['bottom'].set_linewidth(0.5)
    
    plt.tight_layout()
    return _fig_to_base64_png(fig)


def generate_default_charts(kpi_data: Dict[str, Any], historical_kpi_data: Optional[Dict[str, Any]] = None) -> Dict[str, str]:
    charts = {}

    workforce_data = kpi_data.get("Total Workforce by Gender", [])
    if workforce_data:
        charts["workforce_by_gender"] = create_default_workforce_pie_chart(workforce_data)

    training_data = kpi_data.get("Average Training Hours per Employee", {})
    if training_data and training_data.get("breakdown_by_gender"):
        charts["training_hours_by_gender"] = create_default_training_hours_chart(
            training_data["breakdown_by_gender"]
        )

    current_training = training_data.get("overall_average_hours") if training_data else None
    prior_training = None
    if historical_kpi_data:
        hist_training = historical_kpi_data.get("Average Training Hours per Employee", {})
        if hist_training:
            prior_training = hist_training.get("overall_average_hours")
    
    if current_training is not None:
        if prior_training is not None:
            charts["trend_training_hours_per_employee"] = create_default_trend_chart(
                current_training, prior_training, "Average Training Hours - Year over Year"
            )
        else:
            charts["trend_training_hours_per_employee"] = None
            
    charts["kpi_summary"] = create_default_kpi_summary_chart(kpi_data)
    
    return charts


def _fig_to_base64_png(fig) -> str:
    buffer = io.BytesIO()
    fig.savefig(buffer, format='png', bbox_inches='tight', dpi=200, 
                facecolor='white', edgecolor='none')
    plt.close(fig)
    buffer.seek(0)
    return base64.b64encode(buffer.read()).decode('utf-8')


def create_placeholder_chart(chart_type: str, title: str = "Chart Not Available") -> str:
    
    fig, ax = plt.subplots(figsize=(6, 4))
    
    if chart_type == "pie":
        # Create empty pie chart
        ax.pie([1], labels=['No Data'], colors=['#E0E0E0'], startangle=90)
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
    elif chart_type == "bar":
        # Create empty bar chart
        ax.bar(['No Data'], [0], color='#E0E0E0')
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
        ax.set_ylabel('Value', fontsize=12, fontweight='bold')
    else:
        # Create empty trend chart
        ax.text(0.5, 0.5, 'No Historical Data Available', ha='center', va='center', 
                transform=ax.transAxes, fontsize=14, color='gray')
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
    
    plt.tight_layout()
    return _fig_to_base64_png(fig)
