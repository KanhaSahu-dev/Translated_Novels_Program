import { Routes } from '@angular/router';
import { NovelSearchComponent } from './components/novel-search/novel-search';
import { NovelListComponent } from './components/novel-list/novel-list';
import { GlossaryManagerComponent } from './components/glossary-manager/glossary-manager';
import { ChapterViewComponent } from './components/chapter-view/chapter-view';

export const routes: Routes = [
  { path: '', redirectTo: '/search', pathMatch: 'full' },
  { path: 'search', component: NovelSearchComponent },
  { path: 'list', component: NovelListComponent },
  { path: 'glossary', component: GlossaryManagerComponent },
  { path: 'chapters', component: ChapterViewComponent },
  { path: '**', redirectTo: '/search' }
];
