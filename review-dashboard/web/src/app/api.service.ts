import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../environments/environment';

export interface RunSummary {
  id: string;
  label: string;
  description: string;
  total: number;
  correct: number;
  accuracy: number;
}

export interface PredictionRow {
  exampleId: string;
  language: string;
  setName: string;
  text: string;
  gold: string;
  pred: string;
  correct: boolean;
  reason: string | null;
}

export interface ConfusionCell {
  gold: string;
  pred: string;
  count: number;
}

export interface BreakdownRow {
  key: string;
  total: number;
  correct: number;
  accuracy: number;
}

export interface Filters {
  set?: string;
  language?: string;
  errorsOnly?: boolean;
}

@Injectable({ providedIn: 'root' })
export class ApiService {
  private readonly base = environment.apiUrl;

  constructor(private http: HttpClient) {}

  runs(): Observable<RunSummary[]> {
    return this.http.get<RunSummary[]>(`${this.base}/runs`);
  }

  predictions(runId: string, f: Filters): Observable<PredictionRow[]> {
    let params = new HttpParams().set('errorsOnly', String(!!f.errorsOnly));
    if (f.set) params = params.set('set', f.set);
    if (f.language) params = params.set('language', f.language);
    return this.http.get<PredictionRow[]>(`${this.base}/runs/${encodeURIComponent(runId)}/predictions`, { params });
  }

  confusion(runId: string, set?: string): Observable<ConfusionCell[]> {
    let params = new HttpParams();
    if (set) params = params.set('set', set);
    return this.http.get<ConfusionCell[]>(`${this.base}/runs/${encodeURIComponent(runId)}/confusion`, { params });
  }

  breakdown(runId: string, by: 'language' | 'intent', set?: string): Observable<BreakdownRow[]> {
    let params = new HttpParams().set('by', by);
    if (set) params = params.set('set', set);
    return this.http.get<BreakdownRow[]>(`${this.base}/runs/${encodeURIComponent(runId)}/breakdown`, { params });
  }
}
