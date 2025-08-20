import { ComponentFixture, TestBed } from '@angular/core/testing';

import { GlossaryManager } from './glossary-manager';

describe('GlossaryManager', () => {
  let component: GlossaryManager;
  let fixture: ComponentFixture<GlossaryManager>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [GlossaryManager]
    })
    .compileComponents();

    fixture = TestBed.createComponent(GlossaryManager);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
