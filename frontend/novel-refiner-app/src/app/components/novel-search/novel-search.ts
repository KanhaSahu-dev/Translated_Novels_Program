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
  customUrl: string = '';
  isSearching: boolean = false;
  searchResults: any[] = [];
  errorMessage: string = '';

  async searchNovels() {
    if (this.sourceSite === 'custom') {
      if (!this.customUrl.trim()) {
        this.errorMessage = 'Please enter a custom URL';
        return;
      }
      // For custom URL, we'll directly extract without search
      await this.extractNovel(this.customUrl);
      return;
    }

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
          novel_name: this.searchQuery
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
          novel_url: novelUrl,
          max_chapters: 10,
          use_selenium: false
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      alert(`✅ Novel extraction started!\n\nNovel URL: ${data.novel_url}\nStatus: ${data.status}\n\nChapters will be extracted in the background. Check the Novel List page to see progress.`);
      
      // Clear search results after successful extraction
      this.searchResults = [];
      this.searchQuery = '';
      this.customUrl = '';
    } catch (error) {
      console.error('Extraction error:', error);
      alert('Failed to extract novel. Please try again.');
    }
  }
}
