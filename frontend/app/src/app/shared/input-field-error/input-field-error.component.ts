import {AfterContentInit, Component, Input} from '@angular/core'
import {BehaviorSubject, Subscription} from 'rxjs'

import {FormControl} from '@angular/forms'

const renderErrorString = (formatString: string, details: any) => {
  if (details == null) {
    return formatString
  }
  Object.entries(details).forEach(([key, val]) => {
    formatString = formatString.replace(`{${key}}`, val as string)
  })

  return formatString
}

@Component({
  selector: 'app-input-field-error',
  templateUrl: './input-field-error.component.html',
  styleUrls: ['./input-field-error.component.scss'],
})

export class InputFieldErrorComponent implements AfterContentInit {
  @Input()
  public validator!: string

  @Input()
  public errorDetails?: boolean | Record<string, number | string | boolean>

  @Input()
  public errorFormat?: string

  @Input()
  public fieldFormControl?: FormControl

  public renderedErrorMessage?: string

  public showErrors$ = new BehaviorSubject(true)

  private errorSubscription?: Subscription

  private readonly standardValidators: Record<string, string> = {
    min: 'Minimum number required is {min}!',
    max: 'Maximum number required is {max}!',
    required: 'This field is required!',
    requiredTrue: 'This field is required!',
    email: 'Invalid email format!',
    minlength: 'Minimum characters are {requiredLength}!',
    maxlength: 'Maximum characters are {requiredLength}!',
    pattern: 'Invalid pattern!',
    nullvalidator: 'This field can not be empty!',
  }

  public ngAfterContentInit() {
    this.renderErrorMessage()
  }

  public bindFormControl(control: FormControl) {
    if (this.errorSubscription != null) {
      throw new Error('A form control may only be bound one time')
    }
    this.setError(false)
    this.fieldFormControl = control
    this.errorSubscription = control.valueChanges.subscribe(_ => {
      const hasErrors = control.hasError(this.validator) && control.invalid && (control.dirty || control.touched)
      this.errorDetails = hasErrors ? control.errors?.[this.validator] : null
      this.renderErrorMessage()
      this.setError(hasErrors)
    })

  }

  private renderErrorMessage() {
    let message = this.errorFormat ?? this.standardValidators[this.validator] ?? this.renderedErrorMessage
    message = renderErrorString(message, this.errorDetails)
    this.renderedErrorMessage = message
  }

  private setError(bool: boolean) {
    this.showErrors$.next(bool)
  }
}
