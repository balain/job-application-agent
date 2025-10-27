"""
Analytics dashboard for career insights and visualization.
"""

import logging
from typing import List, Dict, Optional, Any
from datetime import datetime, date, timedelta
import json

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, BarColumn, TextColumn
from rich.layout import Layout
from rich.text import Text

from .career_analytics_models import (
    AnalyticsDashboard as AnalyticsDashboardModel, CareerAnalytics, SalaryBenchmark, CompetitiveAnalysis,
    CareerStage, Industry, TrendDirection
)
from .personalized_recommendation_engine import PersonalizedRecommendationEngine
from .industry_trend_analyzer import IndustryTrendAnalyzer
from .career_progression_tracker import CareerProgressionTracker

logger = logging.getLogger(__name__)
console = Console()


class AnalyticsDashboard:
    """Career analytics dashboard with visual insights."""
    
    def __init__(self):
        self.logger = logger
        self.recommendation_engine = PersonalizedRecommendationEngine()
        self.trend_analyzer = IndustryTrendAnalyzer()
        self.progression_tracker = CareerProgressionTracker()
    
    def create_dashboard(self, user_profile: Dict[str, Any]) -> AnalyticsDashboardModel:
        """
        Create comprehensive analytics dashboard.
        
        Args:
            user_profile: User profile data
            
        Returns:
            AnalyticsDashboard with all analytics data
        """
        console.print("[blue]Creating analytics dashboard...[/blue]")
        
        # Get user ID
        user_id = user_profile.get('user_id', user_profile.get('email', 'anonymous'))
        
        # Create career analytics
        career_analytics = self.recommendation_engine.create_career_analytics(user_profile)
        
        # Create salary benchmarks
        salary_benchmarks = self._create_salary_benchmarks(user_profile)
        
        # Create competitive analysis
        competitive_analysis = self.trend_analyzer.perform_competitive_analysis(user_profile)
        
        # Calculate key metrics
        key_metrics = self._calculate_key_metrics(career_analytics, competitive_analysis)
        
        # Generate trends summary
        trends_summary = self._generate_trends_summary(career_analytics)
        
        # Generate action items
        action_items = self._generate_action_items(career_analytics)
        
        console.print(f"[green]✓ Analytics dashboard created[/green]")
        
        return AnalyticsDashboardModel(
            user_id=user_id,
            career_analytics=career_analytics,
            salary_benchmarks=salary_benchmarks,
            competitive_analysis=competitive_analysis,
            key_metrics=key_metrics,
            trends_summary=trends_summary,
            action_items=action_items
        )
    
    def display_dashboard(self, dashboard: AnalyticsDashboardModel) -> None:
        """
        Display analytics dashboard in console.
        
        Args:
            dashboard: Analytics dashboard data
        """
        console.print("\n[bold cyan]CAREER ANALYTICS DASHBOARD[/bold cyan]")
        console.print("=" * 60)
        
        # Header
        console.print(f"\n[bold]User:[/bold] {dashboard.user_id}")
        console.print(f"[bold]Analysis Date:[/bold] {dashboard.dashboard_date.strftime('%Y-%m-%d %H:%M')}")
        
        # Key Metrics
        self._display_key_metrics(dashboard.key_metrics)
        
        # Career Score
        self._display_career_score(dashboard.career_analytics.career_score)
        
        # Career Progression
        self._display_career_progression(dashboard.career_analytics.career_progression)
        
        # Skill Trends
        self._display_skill_trends(dashboard.career_analytics.skill_trends)
        
        # Industry Insights
        self._display_industry_insights(dashboard.career_analytics.industry_insights)
        
        # Competitive Analysis
        self._display_competitive_analysis(dashboard.competitive_analysis)
        
        # Salary Benchmarks
        self._display_salary_benchmarks(dashboard.salary_benchmarks)
        
        # Personalized Recommendations
        self._display_recommendations(dashboard.career_analytics.personalized_recommendations)
        
        # Action Items
        self._display_action_items(dashboard.action_items)
        
        # Trends Summary
        self._display_trends_summary(dashboard.trends_summary)
    
    def _create_salary_benchmarks(self, user_profile: Dict[str, Any]) -> List[SalaryBenchmark]:
        """Create salary benchmarks for user's profile."""
        
        benchmarks = []
        
        # Primary industry benchmark
        primary_benchmark = self.trend_analyzer.create_salary_benchmark(user_profile)
        benchmarks.append(primary_benchmark)
        
        # Additional industry benchmarks for comparison
        relevant_industries = self.trend_analyzer._identify_relevant_industries(user_profile)
        
        for industry in relevant_industries[:2]:  # Top 2 additional industries
            if industry != primary_benchmark.industry:
                # Create benchmark for comparison industry
                comparison_profile = user_profile.copy()
                comparison_profile['industry'] = industry.value
                
                comparison_benchmark = self.trend_analyzer.create_salary_benchmark(comparison_profile)
                benchmarks.append(comparison_benchmark)
        
        return benchmarks
    
    def _calculate_key_metrics(self, career_analytics: CareerAnalytics, 
                             competitive_analysis: CompetitiveAnalysis) -> Dict[str, float]:
        """Calculate key performance metrics."""
        
        return {
            'career_score': career_analytics.career_score,
            'progression_score': career_analytics.career_progression.progression_score * 100,
            'competitive_score': competitive_analysis.competitive_score,
            'skill_demand_avg': sum(trend.demand_score for trend in career_analytics.skill_trends) / max(len(career_analytics.skill_trends), 1) * 100,
            'industry_growth_avg': sum(insight.growth_rate for insight in career_analytics.industry_insights) / max(len(career_analytics.industry_insights), 1),
            'time_to_next_stage': career_analytics.career_progression.time_to_next_stage,
            'skill_gaps_count': len(career_analytics.career_progression.skill_gaps),
            'recommendations_count': len(career_analytics.personalized_recommendations)
        }
    
    def _generate_trends_summary(self, career_analytics: CareerAnalytics) -> List[str]:
        """Generate trends summary."""
        
        trends = []
        
        # Career progression trend
        if career_analytics.career_progression.progression_score > 0.7:
            trends.append("Strong career progression momentum")
        elif career_analytics.career_progression.progression_score > 0.5:
            trends.append("Moderate career progression")
        else:
            trends.append("Career progression needs attention")
        
        # Skill trends
        rising_skills = [trend for trend in career_analytics.skill_trends if trend.trend_direction == TrendDirection.RISING]
        if rising_skills:
            trends.append(f"Strong demand for {len(rising_skills)} skills")
        
        # Industry trends
        high_growth_industries = [insight for insight in career_analytics.industry_insights if insight.growth_rate > 6.0]
        if high_growth_industries:
            trends.append(f"High growth in {len(high_growth_industries)} industries")
        
        # Market position
        if career_analytics.market_position in ["Top Performer", "Strong Competitor"]:
            trends.append("Strong market position")
        else:
            trends.append("Market position needs improvement")
        
        return trends
    
    def _generate_action_items(self, career_analytics: CareerAnalytics) -> List[str]:
        """Generate priority action items."""
        
        action_items = []
        
        # High priority recommendations
        high_priority_recs = [rec for rec in career_analytics.personalized_recommendations if rec.priority == 'high']
        for rec in high_priority_recs[:3]:  # Top 3 high priority
            action_items.append(f"High Priority: {rec.title}")
        
        # Skill gaps
        skill_gaps = career_analytics.career_progression.skill_gaps[:2]  # Top 2 gaps
        for gap in skill_gaps:
            action_items.append(f"Develop: {gap}")
        
        # Career progression
        if career_analytics.career_progression.progression_score < 0.6:
            action_items.append(f"Focus on progression to {career_analytics.career_progression.next_stage.value.replace('_', ' ').title()}")
        
        return action_items[:5]  # Limit to 5 action items
    
    def _display_key_metrics(self, key_metrics: Dict[str, float]) -> None:
        """Display key metrics table."""
        
        console.print("\n[bold yellow]KEY METRICS[/bold yellow]")
        
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Metric", style="cyan", no_wrap=True)
        table.add_column("Value", style="white")
        table.add_column("Status", style="green")
        
        # Career Score
        career_score = key_metrics['career_score']
        career_status = "Excellent" if career_score >= 80 else "Good" if career_score >= 60 else "Needs Improvement"
        table.add_row("Career Score", f"{career_score:.1f}/100", career_status)
        
        # Progression Score
        progression_score = key_metrics['progression_score']
        progression_status = "Ready" if progression_score >= 70 else "Developing" if progression_score >= 50 else "Needs Work"
        table.add_row("Progression Readiness", f"{progression_score:.1f}%", progression_status)
        
        # Competitive Score
        competitive_score = key_metrics['competitive_score']
        competitive_status = "Strong" if competitive_score >= 70 else "Average" if competitive_score >= 50 else "Weak"
        table.add_row("Competitive Position", f"{competitive_score:.1f}/100", competitive_status)
        
        # Skill Demand
        skill_demand = key_metrics['skill_demand_avg']
        skill_status = "High" if skill_demand >= 80 else "Medium" if skill_demand >= 60 else "Low"
        table.add_row("Skill Demand", f"{skill_demand:.1f}%", skill_status)
        
        # Time to Next Stage
        time_to_next = key_metrics['time_to_next_stage']
        time_status = "Soon" if time_to_next <= 12 else "Medium Term" if time_to_next <= 24 else "Long Term"
        table.add_row("Time to Next Stage", f"{time_to_next} months", time_status)
        
        console.print(table)
    
    def _display_career_score(self, career_score: float) -> None:
        """Display career score with visual indicator."""
        
        console.print(f"\n[bold green]CAREER SCORE: {career_score:.1f}/100[/bold green]")
        
        # Create progress bar
        progress = Progress(
            BarColumn(bar_width=50),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        )
        
        with progress:
            task = progress.add_task("Career Score", total=100, completed=career_score)
        
        # Score interpretation
        if career_score >= 80:
            console.print("[green]Excellent career position with strong growth potential[/green]")
        elif career_score >= 60:
            console.print("[yellow]Good career position with room for improvement[/yellow]")
        else:
            console.print("[red]Career position needs significant improvement[/red]")
    
    def _display_career_progression(self, career_progression) -> None:
        """Display career progression analysis."""
        
        console.print(f"\n[bold blue]CAREER PROGRESSION[/bold blue]")
        
        # Current and next stage
        current_stage = career_progression.current_stage.value.replace('_', ' ').title()
        next_stage = career_progression.next_stage.value.replace('_', ' ').title()
        
        console.print(f"Current Stage: [bold]{current_stage}[/bold]")
        console.print(f"Next Stage: [bold]{next_stage}[/bold]")
        console.print(f"Progression Score: [bold]{career_progression.progression_score:.1%}[/bold]")
        console.print(f"Time to Next Stage: [bold]{career_progression.time_to_next_stage} months[/bold]")
        
        # Skill gaps
        if career_progression.skill_gaps:
            console.print(f"\n[bold red]Skill Gaps:[/bold red]")
            for gap in career_progression.skill_gaps:
                console.print(f"  • {gap}")
        
        # Recommended actions
        if career_progression.recommended_actions:
            console.print(f"\n[bold yellow]Recommended Actions:[/bold yellow]")
            for action in career_progression.recommended_actions:
                console.print(f"  • {action}")
    
    def _display_skill_trends(self, skill_trends: List) -> None:
        """Display skill trends analysis."""
        
        if not skill_trends:
            return
        
        console.print(f"\n[bold blue]SKILL TRENDS[/bold blue]")
        
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Skill", style="cyan")
        table.add_column("Trend", style="white")
        table.add_column("Demand", style="green")
        table.add_column("Growth", style="yellow")
        table.add_column("Salary Impact", style="blue")
        
        for trend in skill_trends[:8]:  # Top 8 skills
            trend_icon = "📈" if trend.trend_direction == TrendDirection.RISING else "📊" if trend.trend_direction == TrendDirection.STABLE else "📉"
            table.add_row(
                trend.skill_name,
                f"{trend_icon} {trend.trend_direction.value.title()}",
                f"{trend.demand_score:.1%}",
                f"{trend.growth_rate:.1f}%",
                f"{trend.salary_impact:.1%}"
            )
        
        console.print(table)
    
    def _display_industry_insights(self, industry_insights: List) -> None:
        """Display industry insights."""
        
        if not industry_insights:
            return
        
        console.print(f"\n[bold blue]INDUSTRY INSIGHTS[/bold blue]")
        
        for insight in industry_insights:
            panel_content = f"""
[bold]Industry:[/bold] {insight.industry.value.title()}
[bold]Growth Rate:[/bold] {insight.growth_rate}%
[bold]Top Skills:[/bold] {', '.join(insight.top_skills[:5])}
[bold]Outlook:[/bold] {insight.future_outlook}
            """.strip()
            
            panel = Panel(panel_content, title=f"{insight.industry.value.title()} Industry", border_style="blue")
            console.print(panel)
    
    def _display_competitive_analysis(self, competitive_analysis: CompetitiveAnalysis) -> None:
        """Display competitive analysis."""
        
        console.print(f"\n[bold blue]COMPETITIVE ANALYSIS[/bold blue]")
        
        # Market position
        console.print(f"Market Position: [bold]{competitive_analysis.market_position}[/bold]")
        console.print(f"Competitive Score: [bold]{competitive_analysis.competitive_score:.1f}/100[/bold]")
        
        # SWOT Analysis
        console.print(f"\n[bold green]Strengths:[/bold green]")
        for strength in competitive_analysis.strengths:
            console.print(f"  • {strength}")
        
        console.print(f"\n[bold red]Weaknesses:[/bold red]")
        for weakness in competitive_analysis.weaknesses:
            console.print(f"  • {weakness}")
        
        console.print(f"\n[bold yellow]Opportunities:[/bold yellow]")
        for opportunity in competitive_analysis.opportunities:
            console.print(f"  • {opportunity}")
        
        console.print(f"\n[bold red]Threats:[/bold red]")
        for threat in competitive_analysis.threats:
            console.print(f"  • {threat}")
    
    def _display_salary_benchmarks(self, salary_benchmarks: List[SalaryBenchmark]) -> None:
        """Display salary benchmarks."""
        
        if not salary_benchmarks:
            return
        
        console.print(f"\n[bold blue]SALARY BENCHMARKS[/bold blue]")
        
        for benchmark in salary_benchmarks:
            console.print(f"\n[bold]{benchmark.position_title}[/bold] - {benchmark.industry.value.title()}")
            console.print(f"Location: {benchmark.location}")
            console.print(f"Experience Level: {benchmark.experience_level.title()}")
            
            salary_range = benchmark.salary_range
            console.print(f"Salary Range: ${salary_range['min']:,.0f} - ${salary_range['max']:,.0f}")
            console.print(f"Median Salary: ${salary_range['median']:,.0f}")
            
            # Percentile breakdown
            console.print(f"25th Percentile: ${benchmark.percentile_data['25th']:,.0f}")
            console.print(f"75th Percentile: ${benchmark.percentile_data['75th']:,.0f}")
            console.print(f"90th Percentile: ${benchmark.percentile_data['90th']:,.0f}")
    
    def _display_recommendations(self, recommendations: List) -> None:
        """Display personalized recommendations."""
        
        if not recommendations:
            return
        
        console.print(f"\n[bold blue]PERSONALIZED RECOMMENDATIONS[/bold blue]")
        
        for i, rec in enumerate(recommendations, 1):
            priority_color = "red" if rec.priority == "high" else "yellow" if rec.priority == "medium" else "green"
            
            console.print(f"\n[bold {priority_color}]{i}. {rec.title}[/bold {priority_color}]")
            console.print(f"   Priority: {rec.priority.title()}")
            console.print(f"   Description: {rec.description}")
            console.print(f"   Expected Impact: {rec.expected_impact}")
            console.print(f"   Time Investment: {rec.time_investment}")
            console.print(f"   Difficulty: {rec.difficulty_level}")
            
            if rec.resources:
                console.print(f"   Resources: {', '.join(rec.resources[:3])}")
    
    def _display_action_items(self, action_items: List[str]) -> None:
        """Display priority action items."""
        
        if not action_items:
            return
        
        console.print(f"\n[bold red]PRIORITY ACTION ITEMS[/bold red]")
        
        for i, item in enumerate(action_items, 1):
            console.print(f"  {i}. {item}")
    
    def _display_trends_summary(self, trends_summary: List[str]) -> None:
        """Display trends summary."""
        
        if not trends_summary:
            return
        
        console.print(f"\n[bold green]TRENDS SUMMARY[/bold green]")
        
        for trend in trends_summary:
            console.print(f"  • {trend}")
    
    def export_dashboard(self, dashboard: AnalyticsDashboardModel, file_path: str) -> None:
        """
        Export dashboard data to JSON file.
        
        Args:
            dashboard: Analytics dashboard data
            file_path: Output file path
        """
        console.print(f"[blue]Exporting dashboard to {file_path}...[/blue]")
        
        # Convert to dictionary for JSON serialization
        dashboard_dict = dashboard.model_dump()
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(dashboard_dict, f, indent=2, ensure_ascii=False, default=str)
        
        console.print(f"[green]✓ Dashboard exported successfully[/green]")
