import { Component, OnInit } from '@angular/core';
import { ApiService, BreakdownRow, ConfusionCell, Filters, PredictionRow, RunSummary } from '../api.service';

@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.scss'],
})
export class DashboardComponent implements OnInit {
  runs: RunSummary[] = [];
  selectedRun = '';
  filters: Filters = { set: '', language: '', errorsOnly: false };

  predictions: PredictionRow[] = [];
  confusion: ConfusionCell[] = [];
  byLanguage: BreakdownRow[] = [];
  byIntent: BreakdownRow[] = [];

  loadError = '';
  readonly columns = ['id', 'language', 'text', 'gold', 'pred', 'result'];

  constructor(private api: ApiService) {}

  ngOnInit(): void {
    this.api.runs().subscribe({
      next: (runs) => {
        this.runs = runs;
        this.selectedRun = runs.find((r) => r.id === 'haiku_gold')?.id ?? runs[0]?.id ?? '';
        this.load();
      },
      error: () => (this.loadError = 'Could not reach the API. It may be waking up; try again in a minute.'),
    });
  }

  get currentRun(): RunSummary | undefined {
    return this.runs.find((r) => r.id === this.selectedRun);
  }

  load(): void {
    if (!this.selectedRun) return;
    this.loadError = '';
    const set = this.filters.set || undefined;
    const language = this.filters.language || undefined;

    this.api.predictions(this.selectedRun, { set, language, errorsOnly: this.filters.errorsOnly }).subscribe({
      next: (rows) => (this.predictions = rows),
      error: () => (this.loadError = 'Could not load predictions.'),
    });
    this.api.confusion(this.selectedRun, set).subscribe({
      next: (cells) => (this.confusion = cells),
      error: () => (this.loadError = 'Could not load the confusion matrix.'),
    });
    this.api.breakdown(this.selectedRun, 'language', set).subscribe({
      next: (rows) => (this.byLanguage = rows),
    });
    this.api.breakdown(this.selectedRun, 'intent', set).subscribe({
      next: (rows) => (this.byIntent = rows),
    });
  }

  /** Confusion matrix cells as a grid: rows are gold labels, columns are predictions. */
  get labels(): string[] {
    return Array.from(new Set(this.confusion.flatMap((c) => [c.gold, c.pred]))).sort();
  }

  cell(gold: string, pred: string): number {
    return this.confusion.find((c) => c.gold === gold && c.pred === pred)?.count ?? 0;
  }

  percent(value: number): string {
    return `${Math.round(value * 100)}%`;
  }
}
