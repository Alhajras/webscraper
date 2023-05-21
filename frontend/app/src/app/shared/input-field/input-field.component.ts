import {AfterContentInit, Component, ContentChild, ContentChildren, Input, QueryList} from '@angular/core'
import {FormControl, FormControlDirective} from '@angular/forms'
import {InputFieldErrorComponent} from "src/app/shared/input-field-error/input-field-error.component";

@Component({
  selector: 'app-input-field',
  templateUrl: './input-field.component.html',
  styleUrls: ['./input-field.component.scss'],
})
export class InputFieldComponent  implements AfterContentInit {
  @Input()
  public labelId!: string

  @Input()
  public labelText!: string

  @Input()
  public isRequired = false

  @Input()
  public helpText = ''

  @ContentChildren(InputFieldErrorComponent)
  public errorsList!: QueryList<InputFieldErrorComponent>

  @ContentChild(FormControlDirective)
  public formControl?: FormControl

  public errorDetails = new Map<string, any>()

  public ngAfterContentInit() {
    if (this.formControl == null) {
      return
    }
    this.errorsList?.toArray().forEach(error => {
      error.bindFormControl(this.formControl as FormControl)
    })
    this.formControl.valueChanges.subscribe(() => {
      this.renderErrorMessages()
    })
  }

  private renderErrorMessages() {
    const errors = new Map<string, any>()
    const control = this.formControl
    Object.entries(control?.errors ?? {}).forEach(([validator, details]) => {
      const overWrittenError = this.errorsList.find(error => error.validator === validator)
      if (overWrittenError != null) {
        overWrittenError.errorDetails = details
      } else if (control?.invalid === true && (control.dirty || control.touched)) {
        errors.set(validator, details)
      }
    })
    this.errorDetails = errors
  }
}
