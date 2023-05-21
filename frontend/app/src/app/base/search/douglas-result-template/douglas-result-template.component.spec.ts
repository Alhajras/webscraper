import { ComponentFixture, TestBed } from '@angular/core/testing';

import { DouglasResultTemplateComponent } from './douglas-result-template.component';

describe('DouglasResultTemplateComponent', () => {
  let component: DouglasResultTemplateComponent;
  let fixture: ComponentFixture<DouglasResultTemplateComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ DouglasResultTemplateComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(DouglasResultTemplateComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
