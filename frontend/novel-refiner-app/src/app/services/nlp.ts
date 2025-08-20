import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from './api';
import { 
  RefinementResult,
  RefineTextRequest,
  RefineChapterRequest,
  ChapterRefinementResponse,
  BatchRefineRequest,
  ProcessingStatus,
  ContextAnalysis
} from '../models/nlp.model';

@Injectable({
  providedIn: 'root'
})
export class NlpService {

  constructor(private apiService: ApiService) {}

  // Initialize NLP models
  initializeModels(): Observable<any> {
    return this.apiService.post<any>('/nlp/initialize', {});
  }

  // Refine arbitrary text
  refineText(request: RefineTextRequest): Observable<RefinementResult> {
    return this.apiService.post<RefinementResult>('/nlp/refine-text', request);
  }

  // Refine a specific chapter
  refineChapter(request: RefineChapterRequest): Observable<ChapterRefinementResponse> {
    return this.apiService.post<ChapterRefinementResponse>('/nlp/refine-chapter', request);
  }

  // Start batch refinement
  batchRefineChapters(request: BatchRefineRequest): Observable<any> {
    return this.apiService.post<any>('/nlp/batch-refine', request);
  }

  // Get processing status for a novel
  getProcessingStatus(novelId: number): Observable<ProcessingStatus> {
    return this.apiService.get<ProcessingStatus>(`/nlp/processing-status/${novelId}`);
  }

  // Get context analysis for a novel
  getContextAnalysis(novelId: number): Observable<ContextAnalysis> {
    return this.apiService.get<ContextAnalysis>(`/nlp/context-analysis/${novelId}`);
  }

  // Quick refine text (simplified interface)
  quickRefine(text: string, novelId?: number): Observable<RefinementResult> {
    const request: RefineTextRequest = {
      text: text,
      use_glossary: !!novelId,
      novel_id: novelId
    };
    return this.refineText(request);
  }

  // Refine multiple chapters with progress tracking
  refineChaptersWithProgress(novelId: number, chapterIds: number[]): Observable<any> {
    const request: BatchRefineRequest = {
      novel_id: novelId,
      chapter_ids: chapterIds,
      use_glossary: true
    };
    return this.batchRefineChapters(request);
  }

  // Get refinement quality metrics
  getRefinementQuality(originalText: string, refinedText: string): any {
    const originalWords = originalText.split(/\s+/).length;
    const refinedWords = refinedText.split(/\s+/).length;
    const lengthChangePercentage = ((refinedWords - originalWords) / originalWords) * 100;
    
    // Simple readability metrics
    const originalSentences = originalText.split(/[.!?]+/).length;
    const refinedSentences = refinedText.split(/[.!?]+/).length;
    
    const originalAvgWordsPerSentence = originalWords / originalSentences;
    const refinedAvgWordsPerSentence = refinedWords / refinedSentences;
    
    return {
      originalWordCount: originalWords,
      refinedWordCount: refinedWords,
      lengthChangePercentage: Math.round(lengthChangePercentage * 100) / 100,
      originalSentenceCount: originalSentences,
      refinedSentenceCount: refinedSentences,
      originalAvgWordsPerSentence: Math.round(originalAvgWordsPerSentence * 100) / 100,
      refinedAvgWordsPerSentence: Math.round(refinedAvgWordsPerSentence * 100) / 100,
      readabilityImprovement: refinedAvgWordsPerSentence < originalAvgWordsPerSentence
    };
  }

  // Check processing status periodically
  pollProcessingStatus(novelId: number, intervalMs: number = 5000): Observable<ProcessingStatus> {
    return new Observable(observer => {
      const poll = () => {
        this.getProcessingStatus(novelId).subscribe({
          next: (status) => {
            observer.next(status);
            if (status.completion_percentage < 100) {
              setTimeout(poll, intervalMs);
            } else {
              observer.complete();
            }
          },
          error: (error) => {
            observer.error(error);
          }
        });
      };
      poll();
    });
  }

  // Validate text before processing
  validateTextForProcessing(text: string): { valid: boolean; errors: string[] } {
    const errors: string[] = [];
    
    if (!text || text.trim().length === 0) {
      errors.push('Text cannot be empty');
    }
    
    if (text.length > 50000) {
      errors.push('Text is too long (maximum 50,000 characters)');
    }
    
    if (text.length < 10) {
      errors.push('Text is too short (minimum 10 characters)');
    }
    
    return {
      valid: errors.length === 0,
      errors: errors
    };
  }

  // Preview refinement changes
  previewRefinement(text: string, novelId?: number): Observable<RefinementResult> {
    // Same as quickRefine but can be used for preview purposes
    return this.quickRefine(text, novelId);
  }
}
