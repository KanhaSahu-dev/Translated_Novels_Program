import { TestBed } from '@angular/core/testing';

import { Glossary } from './glossary';

describe('Glossary', () => {
  let service: Glossary;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(Glossary);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
