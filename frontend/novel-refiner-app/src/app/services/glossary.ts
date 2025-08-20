import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from './api';
import { 
  GlossaryTerm,
  GlossaryTermCreate,
  GlossaryTermUpdate,
  BulkGlossaryImport,
  TermTypeInfo,
  GlossaryExport,
  BulkImportResult
} from '../models/glossary.model';

@Injectable({
  providedIn: 'root'
})
export class GlossaryService {

  constructor(private apiService: ApiService) {}

  // Create a new glossary term
  createTerm(term: GlossaryTermCreate): Observable<GlossaryTerm> {
    return this.apiService.post<GlossaryTerm>('/glossary/terms', term);
  }

  // Get glossary terms for a novel
  getTerms(novelId: number, termType?: string, activeOnly: boolean = true): Observable<GlossaryTerm[]> {
    const params: any = { active_only: activeOnly };
    if (termType) {
      params.term_type = termType;
    }
    return this.apiService.get<GlossaryTerm[]>(`/glossary/terms/${novelId}`, params);
  }

  // Update a glossary term
  updateTerm(termId: number, update: GlossaryTermUpdate): Observable<GlossaryTerm> {
    return this.apiService.put<GlossaryTerm>(`/glossary/terms/${termId}`, update);
  }

  // Delete a glossary term
  deleteTerm(termId: number): Observable<any> {
    return this.apiService.delete<any>(`/glossary/terms/${termId}`);
  }

  // Bulk import glossary terms
  bulkImport(importData: BulkGlossaryImport): Observable<BulkImportResult> {
    return this.apiService.post<BulkImportResult>('/glossary/bulk-import', importData);
  }

  // Get term types for a novel
  getTermTypes(novelId: number): Observable<{ novel_id: number; term_types: TermTypeInfo; total_active_terms: number }> {
    return this.apiService.get<any>(`/glossary/term-types/${novelId}`);
  }

  // Export glossary
  exportGlossary(novelId: number): Observable<GlossaryExport> {
    return this.apiService.post<GlossaryExport>(`/glossary/export/${novelId}`, {});
  }

  // Get all terms grouped by type
  getTermsByType(novelId: number): Observable<{ [termType: string]: GlossaryTerm[] }> {
    return new Observable(observer => {
      this.getTerms(novelId).subscribe({
        next: (terms) => {
          const groupedTerms: { [termType: string]: GlossaryTerm[] } = {};
          
          terms.forEach(term => {
            if (!groupedTerms[term.term_type]) {
              groupedTerms[term.term_type] = [];
            }
            groupedTerms[term.term_type].push(term);
          });
          
          observer.next(groupedTerms);
          observer.complete();
        },
        error: (error) => {
          observer.error(error);
        }
      });
    });
  }

  // Search terms
  searchTerms(novelId: number, searchQuery: string): Observable<GlossaryTerm[]> {
    return new Observable(observer => {
      this.getTerms(novelId).subscribe({
        next: (terms) => {
          const filteredTerms = terms.filter(term => 
            term.original_term.toLowerCase().includes(searchQuery.toLowerCase()) ||
            term.preferred_term.toLowerCase().includes(searchQuery.toLowerCase()) ||
            (term.context && term.context.toLowerCase().includes(searchQuery.toLowerCase()))
          );
          
          observer.next(filteredTerms);
          observer.complete();
        },
        error: (error) => {
          observer.error(error);
        }
      });
    });
  }

  // Get frequently used terms
  getFrequentTerms(novelId: number, limit: number = 20): Observable<GlossaryTerm[]> {
    return new Observable(observer => {
      this.getTerms(novelId).subscribe({
        next: (terms) => {
          const sortedTerms = terms
            .sort((a, b) => b.frequency - a.frequency)
            .slice(0, limit);
          
          observer.next(sortedTerms);
          observer.complete();
        },
        error: (error) => {
          observer.error(error);
        }
      });
    });
  }

  // Validate term before creation
  validateTerm(term: GlossaryTermCreate, existingTerms: GlossaryTerm[]): { valid: boolean; errors: string[] } {
    const errors: string[] = [];
    
    if (!term.original_term || term.original_term.trim().length === 0) {
      errors.push('Original term cannot be empty');
    }
    
    if (!term.preferred_term || term.preferred_term.trim().length === 0) {
      errors.push('Preferred term cannot be empty');
    }
    
    if (!term.term_type || term.term_type.trim().length === 0) {
      errors.push('Term type cannot be empty');
    }
    
    // Check for duplicates
    const duplicate = existingTerms.find(existing => 
      existing.original_term.toLowerCase() === term.original_term.toLowerCase()
    );
    
    if (duplicate) {
      errors.push('A term with this original term already exists');
    }
    
    // Check term length
    if (term.original_term && term.original_term.length > 200) {
      errors.push('Original term is too long (maximum 200 characters)');
    }
    
    if (term.preferred_term && term.preferred_term.length > 200) {
      errors.push('Preferred term is too long (maximum 200 characters)');
    }
    
    return {
      valid: errors.length === 0,
      errors: errors
    };
  }

  // Get term statistics
  getTermStatistics(novelId: number): Observable<any> {
    return new Observable(observer => {
      this.getTerms(novelId, undefined, false).subscribe({
        next: (terms) => {
          const activeTerms = terms.filter(t => t.is_active);
          const inactiveTerms = terms.filter(t => !t.is_active);
          
          const typeStats: { [type: string]: number } = {};
          terms.forEach(term => {
            typeStats[term.term_type] = (typeStats[term.term_type] || 0) + 1;
          });
          
          const stats = {
            totalTerms: terms.length,
            activeTerms: activeTerms.length,
            inactiveTerms: inactiveTerms.length,
            typeBreakdown: typeStats,
            averageFrequency: terms.length > 0 ? 
              terms.reduce((sum, term) => sum + term.frequency, 0) / terms.length : 0,
            mostFrequentTerm: terms.length > 0 ? 
              terms.reduce((max, term) => term.frequency > max.frequency ? term : max) : null
          };
          
          observer.next(stats);
          observer.complete();
        },
        error: (error) => {
          observer.error(error);
        }
      });
    });
  }

  // Create term from suggestion
  createTermFromSuggestion(novelId: number, originalTerm: string, preferredTerm: string, termType: string = 'general'): Observable<GlossaryTerm> {
    const term: GlossaryTermCreate = {
      novel_id: novelId,
      original_term: originalTerm,
      preferred_term: preferredTerm,
      term_type: termType
    };
    
    return this.createTerm(term);
  }
}
