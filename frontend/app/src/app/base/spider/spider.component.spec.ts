import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SpiderComponent } from 'src/app/base/spider/spider.component';

describe('SpiderComponent', () => {
  let component: SpiderComponent;
  let fixture: ComponentFixture<SpiderComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ SpiderComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(SpiderComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
