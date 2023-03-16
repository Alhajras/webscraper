import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CrawlerComponent } from 'src/app/base/crawler/crawler.component';

describe('RunnerComponent', () => {
  let component: CrawlerComponent;
  let fixture: ComponentFixture<CrawlerComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ CrawlerComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(CrawlerComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
