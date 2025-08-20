import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ChapterView } from './chapter-view';

describe('ChapterView', () => {
  let component: ChapterView;
  let fixture: ComponentFixture<ChapterView>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ChapterView]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ChapterView);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
