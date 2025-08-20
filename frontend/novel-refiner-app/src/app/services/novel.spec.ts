import { TestBed } from '@angular/core/testing';

import { Novel } from './novel';

describe('Novel', () => {
  let service: Novel;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(Novel);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
