import { Component } from '@angular/core';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { environment } from '../../environments/environment';

export interface ClassifyResult {
  intent: string;
  reason: string;
}

@Component({
  selector: 'app-try-it',
  templateUrl: './try-it.component.html',
  styleUrls: ['./try-it.component.scss'],
})
export class TryItComponent {
  text = '';
  busy = false;
  result: ClassifyResult | null = null;
  error = '';

  readonly samples = [
    'Where is my package? It was supposed to arrive yesterday.',
    'Please cancel order 4471, I ordered by mistake.',
    'I was charged twice, please refund the extra payment.',
  ];

  constructor(private http: HttpClient) {}

  classify(): void {
    const text = this.text.trim();
    if (!text || this.busy) return;
    this.busy = true;
    this.error = '';
    this.result = null;
    this.http.post<ClassifyResult>(`${environment.classifierUrl}/classify`, { text }).subscribe({
      next: (r) => {
        this.result = r;
        this.busy = false;
      },
      error: (e: HttpErrorResponse) => {
        this.error = this.errorMessage(e);
        this.busy = false;
      },
    });
  }

  private errorMessage(e: HttpErrorResponse): string {
    if (e.status === 429) return 'Too many requests. Wait a minute and try again.';
    if (e.status === 503) return 'The classifier is not configured on the server.';
    if (e.status === 0) return 'Could not reach the classifier. It may be waking up; try again in a minute.';
    return 'The classifier returned an error. Try a different message.';
  }
}
