import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-novel-search',
  imports: [FormsModule, CommonModule],
  templateUrl: './novel-search.html',
  styleUrl: './novel-search.scss'
})
export class NovelSearch {
  searchQuery: string = '';
  sourceSite: string = 'novelhi.com';
  isSearching: boolean = false;
  searchResults: any[] = [];
  errorMessage: string = '';

  async searchNovels() {
    if (!this.searchQuery.trim()) {
      this.errorMessage = 'Please enter a search term';
      return;
    }

    this.isSearching = true;
    this.errorMessage = '';
    this.searchResults = [];

    try {
      // Call the backend API
      const response = await fetch('http://localhost:8000/api/scraper/search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: this.searchQuery,
          source: this.sourceSite
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      this.searchResults = data.results || [];
      
      if (this.searchResults.length === 0) {
        this.errorMessage = 'No novels found. Try a different search term.';
      }
    } catch (error) {
      console.error('Search error:', error);
      this.errorMessage = 'Failed to search. Please check if the backend server is running.';
    } finally {
      this.isSearching = false;
    }
  }

  async extractNovel(novelUrl: string) {
    try {
      const response = await fetch('http://localhost:8000/api/scraper/extract', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          url: novelUrl,
          source: this.sourceSite
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      alert(`Successfully extracted novel: ${data.title}\nChapters found: ${data.chapters_count}`);
      
      // Clear search results after successful extraction
      this.searchResults = [];
      this.searchQuery = '';
    } catch (error) {
      console.error('Extraction error:', error);
      alert('Failed to extract novel. Please try again.');
    }
  }
}
