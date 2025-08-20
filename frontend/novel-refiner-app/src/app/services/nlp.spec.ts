import { TestBed } from '@angular/core/testing';

import { Nlp } from './nlp';

describe('Nlp', () => {
  let service: Nlp;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(Nlp);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
