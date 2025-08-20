import { ComponentFixture, TestBed } from '@angular/core/testing';

import { NovelList } from './novel-list';

describe('NovelList', () => {
  let component: NovelList;
  let fixture: ComponentFixture<NovelList>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [NovelList]
    })
    .compileComponents();

    fixture = TestBed.createComponent(NovelList);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
