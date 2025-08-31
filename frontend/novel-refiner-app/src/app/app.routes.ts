import { Routes } from '@angular/router';
import { NovelSearch } from './components/novel-search/novel-search';
import { NovelList } from './components/novel-list/novel-list';
import { GlossaryManager } from './components/glossary-manager/glossary-manager';
import { ChapterView } from './components/chapter-view/chapter-view';

export const routes: Routes = [
  { path: '', redirectTo: '/search', pathMatch: 'full' },
  { path: 'search', component: NovelSearch },
  { path: 'list', component: NovelList },
  { path: 'glossary', component: GlossaryManager },
  { path: 'chapters', component: ChapterView },
  { path: '**', redirectTo: '/search' }
];
