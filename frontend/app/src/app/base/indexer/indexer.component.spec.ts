import { ComponentFixture, TestBed } from '@angular/core/testing';

import { IndexerComponent } from 'src/app/base/indexer/indexer.component';

describe('InspectorComponent', () => {
  let component: IndexerComponent;
  let fixture: ComponentFixture<IndexerComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ IndexerComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(IndexerComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
