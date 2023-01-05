import { TestBed } from '@angular/core/testing';

import { SpiderService } from './spider.service';

describe('SpiderService', () => {
  let service: SpiderService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(SpiderService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
