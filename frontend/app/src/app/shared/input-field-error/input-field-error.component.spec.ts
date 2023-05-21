import { ComponentFixture, TestBed, fakeAsync } from '@angular/core/testing'
import { FormControl, Validators } from '@angular/forms'

import { By } from '@angular/platform-browser'
import { DebugElement } from '@angular/core'
import { InputFieldErrorComponent } from './input-field-error.component'

describe('InputFieldErrorComponent', () => {
  let component: InputFieldErrorComponent
  let fixture: ComponentFixture<InputFieldErrorComponent>
  let el: DebugElement
  let name: FormControl

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [InputFieldErrorComponent],
    })
      .compileComponents()
  })

  beforeEach(() => {
    fixture = TestBed.createComponent(InputFieldErrorComponent)
    component = fixture.componentInstance
    el = fixture.debugElement
    fixture.detectChanges()
  })

  it('should create', () => {
    expect(component).toBeTruthy()
  })

  it('should render error messages with arbitrary error details', fakeAsync(() => {
    const formControl = new FormControl('', [Validators.required, () => ({ junk: { word: 1, value: 2 } })])
    component.bindFormControl(formControl)
    component.validator = 'required'
    component.errorFormat = 'This is invalid input!'
    component.ngAfterContentInit()
    expect(component.renderedErrorMessage).toEqual('This is invalid input!')

    component.validator = 'junk'
    component.errorFormat = '{word} {value}'
    component.errorDetails = { word: 1, value: 2 }
    component.ngAfterContentInit()
    expect(component.renderedErrorMessage).toContain('1 2')
  }))

  it('should render maxLength validator message from its error details', () => {
    const control = new FormControl(name, [Validators.maxLength(100)])
    component.bindFormControl(control)
    control.setValue('Loooooooooooooooo' +
      'ooooooooooooooooooooooooooooooooooooooooooooooooooooooooo' +
      'ooooooooooooooooooooooooooooooooooooooooooooooooooooooooo' +
      'oooooooooooooooooong input name')
    component.validator = 'maxlength'
    component.errorDetails = { requiredLength: 100 }
    component.ngAfterContentInit()
    expect(component.renderedErrorMessage).toContain('Maximum characters are 100!')
  })

  it('should render minLength validator message from its error details', () => {
    const control = new FormControl(name, [Validators.minLength(8)])
    component.bindFormControl(control)
    component.validator = 'minlength'
    component.errorDetails = { requiredLength: 8 }
    component.ngAfterContentInit()
    expect(component.renderedErrorMessage).toContain('Minimum characters are 8!')
  })

  it('should render a required validator message from its error details', () => {
    const control = new FormControl(name, [Validators.required])
    component.bindFormControl(control)
    component.validator = 'required'
    component.errorDetails = true
    component.ngAfterContentInit()
    expect(component.renderedErrorMessage).toContain('This field is required!')
  })

  it('should render en email validator message from its error details', fakeAsync(() => {
    const formControl = new FormControl('', [Validators.required, Validators.email])
    component.bindFormControl(formControl)
    component.validator = 'email'
    component.errorDetails = true
    component.ngAfterContentInit()
    expect(component.renderedErrorMessage).toContain('Invalid email format!')
  }))

  it('should always display error messages that are not bound to a form control', () => {
    component.errorFormat = 'Here are some words'
    expect(component.showErrors$.getValue()).toBeTrue()
    component.ngAfterContentInit()
    fixture.detectChanges()
    expect(component.showErrors$.getValue()).toBeTrue()
    expect(el.nativeElement.textContent).toContain('Here are some words')
  })

  it('should only display error messages that are bound to a form control when they have changed', () => {
    component.validator = 'required'
    component.errorFormat = 'xxx'
    const formControl = new FormControl('', [Validators.required])
    component.bindFormControl(formControl)
    expect(component.showErrors$.getValue()).toBeFalse()
    fixture.detectChanges()
    expect(formControl.dirty).toBeFalse()
    expect(formControl.touched).toBeFalse()
    expect(formControl.valid).toBeFalse()
    expect(formControl.hasError('required')).toBeTrue()
    expect(el.query(By.css('.p-error'))).toBeNull()

    formControl.markAsDirty()
    formControl.setValue('')
    fixture.detectChanges()
    expect(formControl.hasError('required')).toBeTrue()
    expect(el.query(By.css('.p-error'))).not.toBeNull()
    expect(el.nativeElement.textContent).toContain('xxx')

    formControl.markAsDirty()
    formControl.setValue('www.preondock.com')
    fixture.detectChanges()
    expect(formControl.hasError('required')).toBeFalse()
    expect(el.query(By.css('.p-error'))).toBeNull()

    formControl.markAsTouched()
    formControl.setValue('')
    fixture.detectChanges()
    expect(formControl.hasError('required')).toBeTrue()
    expect(el.query(By.css('.p-error'))).not.toBeNull()
    expect(el.nativeElement.textContent).toContain('xxx')
  })
})
