import { TestBed } from '@angular/core/testing';

import { CrawlerService } from 'src/app/services/crawler.service';

describe('CrawlerService', () => {
  let service: CrawlerService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(CrawlerService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
