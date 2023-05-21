import { ComponentFixture, TestBed } from '@angular/core/testing';

import { FlaconiResultTemplateComponent } from './flaconi-result-template.component';

describe('FlaconiResultTemplateComponent', () => {
  let component: FlaconiResultTemplateComponent;
  let fixture: ComponentFixture<FlaconiResultTemplateComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ FlaconiResultTemplateComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(FlaconiResultTemplateComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
