"""
Construction Timeline Estimator for Industrial Parks

Generates detailed construction schedules with:
- Site preparation (clearing, grading)
- Infrastructure (roads, utilities, ponds)
- Landscaping and final touches
- Critical path method (CPM) analysis
- Gantt chart data generation

Follows IEAT Thailand construction standards.
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


@dataclass
class Task:
    """Construction task with dependencies."""
    id: str
    name: str
    duration_days: int
    dependencies: List[str]
    resource: str
    critical: bool = False


class TimelineGenerator:
    """
    Generate construction timelines for industrial parks.
    
    Features:
    - Milestone-based scheduling
    - Critical path analysis
    - Parallel task identification
    - Gantt chart data
    """
    
    def __init__(self):
        """Initialize timeline generator with standard tasks."""
        self.base_tasks = self._define_standard_tasks()
    
    def generate_timeline(
        self,
        design: Dict,
        start_date: Optional[datetime] = None
    ) -> Dict:
        """
        Generate construction timeline for design.
        
        Args:
            design: {
                "site_boundary": Polygon,
                "lots": List[Polygon],
                "roads": Dict,
                "infrastructure": Dict,
                "grading": Dict
            }
            start_date: Project start date
        
        Returns:
            {
                "tasks": List[Dict],
                "total_months": float,
                "total_days": int,
                "critical_path": List[str],
                "milestones": List[Dict],
                "gantt_data": List[Dict],
                "parallel_tasks": int
            }
        """
        logger.info("[TIMELINE] Generating construction timeline")
        
        # Calculate task durations based on design
        tasks = self._calculate_task_durations(design)
        
        # Calculate start/end dates
        start = start_date or datetime.now()
        scheduled_tasks = self._schedule_tasks(tasks, start)
        
        # Find critical path
        critical_path = self._find_critical_path(scheduled_tasks)
        
        # Mark critical tasks
        for task in scheduled_tasks:
            task.critical = task['id'] in critical_path
        
        # Generate milestones
        milestones = self._generate_milestones(scheduled_tasks)
        
        # Calculate project metrics
        end_date = max(t['end_date'] for t in scheduled_tasks)
        total_days = (end_date - start).days
        total_months = total_days / 30
        
        # Count parallel tasks
        parallel_tasks = self._count_parallel_tasks(scheduled_tasks)
        
        # Generate Gantt chart data
        gantt_data = self._generate_gantt_data(scheduled_tasks)
        
        logger.info(
            f"[TIMELINE] Timeline generated: {total_months:.1f} months "
            f"({total_days} days)"
        )
        
        return {
            "tasks": scheduled_tasks,
            "total_months": round(total_months, 1),
            "total_days": total_days,
            "critical_path": critical_path,
            "critical_path_pct": (len(critical_path) / len(tasks)) * 100,
            "milestones": milestones,
            "gantt_data": gantt_data,
            "parallel_tasks": parallel_tasks,
            "start_date": start.isoformat(),
            "end_date": end_date.isoformat()
        }
    
    def _define_standard_tasks(self) -> List[Task]:
        """Define standard construction tasks."""
        return [
            # Phase 1: Site Preparation
            Task(
                "T001",
                "Site Survey & Staking",
                5,
                [],
                "Surveyor"
            ),
            Task(
                "T002",
                "Site Clearing & Demolition",
                10,
                ["T001"],
                "Earthworks"
            ),
            Task(
                "T003",
                "Grading & Earthworks",
                15,  # Base duration, scaled by volume
                ["T002"],
                "Earthworks"
            ),
            
            # Phase 2: Drainage & Retention
            Task(
                "T004",
                "Retention Ponds Excavation",
                20,
                ["T003"],
                "Earthworks"
            ),
            Task(
                "T005",
                "Retention Ponds Lining & Finishing",
                10,
                ["T004"],
                "Concrete"
            ),
            
            # Phase 3: Underground Utilities
            Task(
                "T006",
                "Water Network Installation",
                20,
                ["T003"],
                "Utilities"
            ),
            Task(
                "T007",
                "Sewer Network Installation",
                25,
                ["T003"],
                "Utilities"
            ),
            Task(
                "T008",
                "Electrical Conduits",
                15,
                ["T003"],
                "Electrical"
            ),
            Task(
                "T009",
                "Telecommunications Conduits",
                10,
                ["T003"],
                "Utilities"
            ),
            
            # Phase 4: Treatment Facilities
            Task(
                "T010",
                "Water Treatment Plant",
                30,
                ["T006"],
                "Facilities"
            ),
            Task(
                "T011",
                "Wastewater Treatment Plant",
                35,
                ["T007"],
                "Facilities"
            ),
            Task(
                "T012",
                "Substation Construction",
                40,
                ["T008"],
                "Electrical"
            ),
            
            # Phase 5: Roads
            Task(
                "T013",
                "Main Road Base Course",
                20,
                ["T006", "T007", "T008"],
                "Paving"
            ),
            Task(
                "T014",
                "Main Road Asphalt",
                15,
                ["T013"],
                "Paving"
            ),
            Task(
                "T015",
                "Secondary Road Base Course",
                15,
                ["T006", "T007", "T008"],
                "Paving"
            ),
            Task(
                "T016",
                "Secondary Road Asphalt",
                10,
                ["T015"],
                "Paving"
            ),
            
            # Phase 6: Green Space & Landscaping
            Task(
                "T017",
                "Topsoil & Landscape Preparation",
                10,
                ["T014", "T016"],
                "Landscaping"
            ),
            Task(
                "T018",
                "Tree Planting & Green Space",
                15,
                ["T017"],
                "Landscaping"
            ),
            
            # Phase 7: Final Touches
            Task(
                "T019",
                "Street Lighting & Signage",
                10,
                ["T012", "T014"],
                "Electrical"
            ),
            Task(
                "T020",
                "Entrance Gate & Security",
                7,
                ["T014"],
                "Construction"
            ),
            Task(
                "T021",
                "Final Inspection & Approval",
                5,
                ["T018", "T019", "T020"],
                "Management"
            )
        ]
    
    def _calculate_task_durations(self, design: Dict) -> List[Task]:
        """Calculate actual task durations based on design specifics."""
        tasks = [
            Task(t.id, t.name, t.duration_days, t.dependencies, t.resource)
            for t in self.base_tasks
        ]
        
        # Scale grading duration by cut/fill volume
        grading = design.get("grading", {})
        cut_fill_volume = grading.get("total_volume_m3", 50000)
        grading_task = next(t for t in tasks if t.id == "T003")
        grading_task.duration_days = max(
            15,
            int(cut_fill_volume / 5000)  # 5000 m³/day
        )
        
        # Scale road tasks by total road length
        roads = design.get("roads", {})
        road_length_km = roads.get("total_length_km", 3.0)
        for task_id in ["T013", "T014", "T015", "T016"]:
            road_task = next(t for t in tasks if t.id == task_id)
            road_task.duration_days = max(
                10,
                int(road_length_km * 5)  # 5 days per km
            )
        
        # Scale pond task by number of ponds
        infrastructure = design.get("infrastructure", {})
        num_ponds = len(infrastructure.get("retention_ponds", []))
        pond_task = next(t for t in tasks if t.id == "T004")
        pond_task.duration_days = max(15, num_ponds * 10)
        
        return tasks
    
    def _schedule_tasks(
        self,
        tasks: List[Task],
        start_date: datetime
    ) -> List[Dict]:
        """
        Schedule tasks with start/end dates.
        
        Uses forward pass to calculate early start/finish.
        """
        # Create task dict for easy lookup
        task_dict = {t.id: t for t in tasks}
        scheduled = {}
        
        # Calculate early start/finish (forward pass)
        for task in tasks:
            # Find latest finish of dependencies
            if task.dependencies:
                dep_finishes = [
                    scheduled[dep_id]['end_date']
                    for dep_id in task.dependencies
                ]
                early_start = max(dep_finishes)
            else:
                early_start = start_date
            
            early_finish = early_start + timedelta(days=task.duration_days)
            
            scheduled[task.id] = {
                "id": task.id,
                "name": task.name,
                "duration_days": task.duration_days,
                "dependencies": task.dependencies,
                "resource": task.resource,
                "start_date": early_start,
                "end_date": early_finish,
                "critical": False
            }
        
        return list(scheduled.values())
    
    def _find_critical_path(self, tasks: List[Dict]) -> List[str]:
        """
        Find critical path using backward pass.
        
        Critical path = tasks with zero slack.
        """
        # Create task dict
        task_dict = {t['id']: t for t in tasks}
        
        # Calculate late start/finish (backward pass)
        project_end = max(t['end_date'] for t in tasks)
        late_times = {}
        
        # Start from end tasks
        end_tasks = [
            t for t in tasks
            if not any(t['id'] in t2['dependencies'] for t2 in tasks)
        ]
        
        # Backward pass
        for task in reversed(tasks):
            # Find earliest late finish of successors
            successors = [
                t for t in tasks if task['id'] in t['dependencies']
            ]
            
            if successors:
                late_finish = min(
                    late_times[s['id']]['late_start']
                    for s in successors
                )
            else:
                late_finish = project_end
            
            late_start = late_finish - timedelta(
                days=task['duration_days']
            )
            
            late_times[task['id']] = {
                'late_start': late_start,
                'late_finish': late_finish
            }
        
        # Find tasks with zero slack
        critical_path = []
        for task in tasks:
            slack = (
                late_times[task['id']]['late_start'] - task['start_date']
            ).days
            if slack == 0:
                critical_path.append(task['id'])
        
        return critical_path
    
    def _generate_milestones(self, tasks: List[Dict]) -> List[Dict]:
        """Generate project milestones."""
        milestones = []
        
        # Phase completion milestones
        phase_tasks = {
            "Site Preparation Complete": ["T003"],
            "Retention Ponds Complete": ["T005"],
            "Underground Utilities Complete": ["T009"],
            "Treatment Facilities Complete": ["T012"],
            "Roads Complete": ["T016"],
            "Landscaping Complete": ["T018"],
            "Project Complete": ["T021"]
        }
        
        task_dict = {t['id']: t for t in tasks}
        
        for milestone_name, task_ids in phase_tasks.items():
            milestone_date = max(
                task_dict[tid]['end_date'] for tid in task_ids
            )
            milestones.append({
                "name": milestone_name,
                "date": milestone_date.isoformat(),
                "tasks_completed": task_ids
            })
        
        return milestones
    
    def _count_parallel_tasks(self, tasks: List[Dict]) -> int:
        """Count maximum number of parallel tasks."""
        # Find all unique time periods
        dates = set()
        for task in tasks:
            dates.add(task['start_date'])
            dates.add(task['end_date'])
        
        max_parallel = 0
        for date in sorted(dates):
            # Count tasks active at this date
            active = sum(
                1 for t in tasks
                if t['start_date'] <= date < t['end_date']
            )
            max_parallel = max(max_parallel, active)
        
        return max_parallel
    
    def _generate_gantt_data(self, tasks: List[Dict]) -> List[Dict]:
        """Generate data for Gantt chart visualization."""
        return [
            {
                "id": t['id'],
                "name": t['name'],
                "start": t['start_date'].isoformat(),
                "end": t['end_date'].isoformat(),
                "duration": t['duration_days'],
                "dependencies": t['dependencies'],
                "resource": t['resource'],
                "critical": t['critical'],
                "progress": 0  # Will be updated during construction
            }
            for t in tasks
        ]


# Example usage
if __name__ == "__main__":
    # Mock design
    test_design = {
        "site_boundary": None,
        "grading": {"total_volume_m3": 75000},
        "roads": {"total_length_km": 4.5},
        "infrastructure": {
            "retention_ponds": [{"id": 1}, {"id": 2}]
        }
    }
    
    generator = TimelineGenerator()
    timeline = generator.generate_timeline(test_design)
    
    print(f"\n✓ Timeline Generated")
    print(f"  • Total Duration: {timeline['total_months']:.1f} months "
          f"({timeline['total_days']} days)")
    print(f"  • Critical Path: {len(timeline['critical_path'])} tasks")
    print(f"  • Parallel Tasks: {timeline['parallel_tasks']}")
    print(f"  • Milestones: {len(timeline['milestones'])}")
    print(f"\n  Key Milestones:")
    for m in timeline['milestones']:
        print(f"    - {m['name']}: {m['date'][:10]}")
