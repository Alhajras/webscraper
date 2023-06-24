import { ComponentFixture, TestBed } from '@angular/core/testing';

import { GenericResultTemplateComponent } from 'src/app/base/search/generic-result-template/generic-result-template.component';

describe('FlaconiResultTemplateComponent', () => {
  let component: GenericResultTemplateComponent;
  let fixture: ComponentFixture<GenericResultTemplateComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ GenericResultTemplateComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(GenericResultTemplateComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
