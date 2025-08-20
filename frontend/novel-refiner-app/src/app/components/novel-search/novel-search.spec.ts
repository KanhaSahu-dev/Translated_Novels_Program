import { ComponentFixture, TestBed } from '@angular/core/testing';

import { NovelSearch } from './novel-search';

describe('NovelSearch', () => {
  let component: NovelSearch;
  let fixture: ComponentFixture<NovelSearch>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [NovelSearch]
    })
    .compileComponents();

    fixture = TestBed.createComponent(NovelSearch);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
