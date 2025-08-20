import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders, HttpErrorResponse } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError, retry } from 'rxjs/operators';

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private readonly baseUrl = 'http://localhost:8000/api';
  
  private httpOptions = {
    headers: new HttpHeaders({
      'Content-Type': 'application/json'
    })
  };

  constructor(private http: HttpClient) {}

  // Generic GET request
  get<T>(endpoint: string, params?: any): Observable<T> {
    const url = `${this.baseUrl}${endpoint}`;
    const options = params ? { ...this.httpOptions, params } : this.httpOptions;
    
    return this.http.get<T>(url, options)
      .pipe(
        retry(1),
        catchError(this.handleError)
      );
  }

  // Generic POST request
  post<T>(endpoint: string, data: any): Observable<T> {
    const url = `${this.baseUrl}${endpoint}`;
    
    return this.http.post<T>(url, data, this.httpOptions)
      .pipe(
        catchError(this.handleError)
      );
  }

  // Generic PUT request
  put<T>(endpoint: string, data: any): Observable<T> {
    const url = `${this.baseUrl}${endpoint}`;
    
    return this.http.put<T>(url, data, this.httpOptions)
      .pipe(
        catchError(this.handleError)
      );
  }

  // Generic DELETE request
  delete<T>(endpoint: string): Observable<T> {
    const url = `${this.baseUrl}${endpoint}`;
    
    return this.http.delete<T>(url, this.httpOptions)
      .pipe(
        catchError(this.handleError)
      );
  }

  // File upload request
  upload<T>(endpoint: string, formData: FormData): Observable<T> {
    const url = `${this.baseUrl}${endpoint}`;
    
    // Don't set Content-Type header for FormData - browser will set it automatically
    return this.http.post<T>(url, formData)
      .pipe(
        catchError(this.handleError)
      );
  }

  // Error handling
  private handleError(error: HttpErrorResponse) {
    let errorMessage = 'An unknown error occurred';
    
    if (error.error instanceof ErrorEvent) {
      // Client-side error
      errorMessage = `Client Error: ${error.error.message}`;
    } else {
      // Server-side error
      if (error.error && error.error.detail) {
        errorMessage = error.error.detail;
      } else if (error.message) {
        errorMessage = error.message;
      } else {
        errorMessage = `Server Error Code: ${error.status}\nMessage: ${error.message}`;
      }
    }
    
    console.error('API Error:', error);
    return throwError(() => new Error(errorMessage));
  }

  // Health check
  healthCheck(): Observable<any> {
    return this.get('/health');
  }

  // Get base URL for external use
  getBaseUrl(): string {
    return this.baseUrl;
  }
}
