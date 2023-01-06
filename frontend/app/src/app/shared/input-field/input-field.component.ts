import {Component, ContentChild, Input} from '@angular/core'
import {FormControl, FormControlDirective} from '@angular/forms'

@Component({
  selector: 'app-input-field',
  templateUrl: './input-field.component.html',
  styleUrls: ['./input-field.component.scss'],
})
export class InputFieldComponent {
  @Input()
  public labelId!: string

  @Input()
  public labelText!: string

  @Input()
  public isRequired = false

  @Input()
  public helpText = ''


  @ContentChild(FormControlDirective)
  public formControl?: FormControl

}
