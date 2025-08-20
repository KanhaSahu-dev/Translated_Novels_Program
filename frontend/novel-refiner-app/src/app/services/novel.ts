import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from './api';
import { 
  Novel, 
  Chapter, 
  ChapterContent, 
  NovelSearchResult, 
  NovelSearchRequest, 
  ChapterExtractionRequest 
} from '../models/novel.model';

@Injectable({
  providedIn: 'root'
})
export class NovelService {

  constructor(private apiService: ApiService) {}

  // Search for novels
  searchNovels(searchRequest: NovelSearchRequest): Observable<NovelSearchResult[]> {
    return this.apiService.post<NovelSearchResult[]>('/scraper/search', searchRequest);
  }

  // Start novel extraction
  extractNovel(extractionRequest: ChapterExtractionRequest): Observable<any> {
    return this.apiService.post<any>('/scraper/extract', extractionRequest);
  }

  // Get all novels
  getNovels(): Observable<Novel[]> {
    return this.apiService.get<Novel[]>('/scraper/novels');
  }

  // Get novel by ID
  getNovelById(novelId: number): Observable<Novel> {
    return this.apiService.get<Novel>(`/scraper/novels/${novelId}`);
  }

  // Get chapter content
  getChapterContent(chapterId: number): Observable<ChapterContent> {
    return this.apiService.get<ChapterContent>(`/scraper/chapters/${chapterId}`);
  }

  // Delete novel
  deleteNovel(novelId: number): Observable<any> {
    return this.apiService.delete<any>(`/scraper/novels/${novelId}`);
  }

  // Update chapter content (for manual edits)
  updateChapterContent(chapterId: number, content: Partial<ChapterContent>): Observable<ChapterContent> {
    return this.apiService.put<ChapterContent>(`/scraper/chapters/${chapterId}`, content);
  }

  // Get novels with processing status
  getNovelsWithStatus(): Observable<Novel[]> {
    return this.getNovels();
  }

  // Check if novel exists by URL
  checkNovelExists(novelUrl: string): Observable<boolean> {
    return new Observable(observer => {
      this.getNovels().subscribe({
        next: (novels) => {
          const exists = novels.some(novel => novel.url === novelUrl);
          observer.next(exists);
          observer.complete();
        },
        error: (error) => {
          observer.error(error);
        }
      });
    });
  }

  // Get chapters for a novel
  getNovelChapters(novelId: number): Observable<Chapter[]> {
    return new Observable(observer => {
      this.getNovelById(novelId).subscribe({
        next: (novel) => {
          observer.next(novel.chapters);
          observer.complete();
        },
        error: (error) => {
          observer.error(error);
        }
      });
    });
  }

  // Get processing statistics
  getProcessingStats(novelId: number): Observable<any> {
    return new Observable(observer => {
      this.getNovelById(novelId).subscribe({
        next: (novel) => {
          const totalChapters = novel.chapters.length;
          const processedChapters = novel.chapters.filter(ch => ch.is_processed).length;
          const stats = {
            totalChapters,
            processedChapters,
            completionPercentage: totalChapters > 0 ? (processedChapters / totalChapters) * 100 : 0,
            averageWordCount: totalChapters > 0 ? 
              novel.chapters.reduce((sum, ch) => sum + ch.word_count, 0) / totalChapters : 0
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
}
