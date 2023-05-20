import { ComponentFixture, TestBed } from '@angular/core/testing'

import { MarkedTextComponent } from './marked-text.component'

describe('MarkedTextComponent', () => {
  let component: MarkedTextComponent
  let fixture: ComponentFixture<MarkedTextComponent>

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [MarkedTextComponent],
    })
      .compileComponents()
  })

  beforeEach(() => {
    fixture = TestBed.createComponent(MarkedTextComponent)
    component = fixture.componentInstance
    component.text = 'initial'
    fixture.detectChanges()
  })

  it('should create', () => {
    expect(component).toBeTruthy()
  })

  it('should wrap all matching text in mark nodes', () => {
    component.text = 'ababA'
    component.searchString = 'a'
    component.ngOnInit()
    expect(component.innerHtml).toEqual('<mark>a</mark>b<mark>a</mark>b<mark>A</mark>')
  })

  it('should handle empty input', () => {
    component.text = 'ababA'
    component.searchString = ''
    component.ngOnInit()
    expect(component.innerHtml).toEqual('ababA')
  })
})
