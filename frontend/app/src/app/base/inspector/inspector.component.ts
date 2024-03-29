import {Component, Input, OnInit} from '@angular/core';
import {Template} from "src/app/models/template.model";
import {FormBuilder, FormControl, FormGroup, Validators} from "@angular/forms";
import {HttpErrorResponse} from "@angular/common/http";
import {Inspector} from "src/app/models/inspector.model";
import {InspectorService} from "src/app/services/inspector.service";
import {TypeDropDown} from "src/app/base/actions/action.component";
import {MessageService} from "primeng/api";

@Component({
  selector: 'app-inspector',
  templateUrl: './inspector.component.html',
  styleUrls: ['./inspector.component.scss']
})
export class InspectorComponent implements OnInit {
  @Input()
  public template!: Template
  public inspectors: Inspector[] = []
  public updatedInspector: Inspector | null = null
  public description!: FormControl
  public currentlySubmitting = false
  public displayModal = false
  public selector!: FormControl
  public attribute!: FormControl
  public type!: FormControl
  public name!: FormControl
  public variableName!: FormControl
  public cleanUpExpression!: FormControl
  public form!: FormGroup
  public header = 'Inspector form'
  public errorMessage = ''
  public templates = []
  public readonly columnCount = 8
  public typesList: TypeDropDown[] = [
    {key: 'text', value: 'text'},
    {key: 'image', value: 'image'},
    {key: 'link', value: 'link'}]

  public constructor(
    private readonly fb: FormBuilder,
    private readonly inspectorService: InspectorService,
    private messageService: MessageService
  ) {

  }

  /**
   * Close the edit dialog
   */
  public closeModal(): void {
    this.displayModal = false
  }

  /**
   * Submit request to save/update inspector
   */
  public submit(): void {
    if (!this.form.valid) {
      // We should normally never get here since the submit button should be disabled.
      console.warn('Form not valid.')
      return
    }

    this.currentlySubmitting = true
    const inspector = {
      name: this.name.value,
      variable_name: this.variableName.value,
      clean_up_expression: this.cleanUpExpression.value.length === 0 ? '' : this.cleanUpExpression.value.join('";"'),
      type: this.type.value.value,
      selector: this.selector.value,
      attribute: this.attribute.value,
      template: this.template.id,
    }
    if (this.updatedInspector !== null) {
      this.inspectorService.update(this.updatedInspector.id, inspector).toPromise().then(() => {
        this.inspectorService.list({template: this.template.id}).subscribe(inspectors => {
          this.inspectors = inspectors
        })
        this.closeModal()
        this.messageService.add({
          severity: 'success',
          summary: 'Success',
          detail: `Inspector ${this.name.value} is updated!`
        });
        this.currentlySubmitting = false
        this.updatedInspector = null
      }).catch((err: HttpErrorResponse) => {
        this.errorMessage = err.error
        this.currentlySubmitting = false
        this.messageService.add({
          severity: 'error',
          summary: 'Error',
          detail: `Inspector ${this.name.value} failed to update!`
        });
        console.log(err)
      })
      return;
    }
    this.inspectorService.post(inspector).toPromise().then(() => {
      this.inspectorService.list({template: this.template.id}).subscribe(inspectors => {
        this.inspectors = inspectors
      })
      this.closeModal()
      this.messageService.add({
        severity: 'success',
        summary: 'Success',
        detail: `Inspector ${this.name.value} is created!`
      });
      this.currentlySubmitting = false
    }).catch((err: HttpErrorResponse) => {
      this.errorMessage = err.error
      this.currentlySubmitting = false
      this.messageService.add({
        severity: 'error',
        summary: 'Error',
        detail: `Inspector ${this.name.value} failed to be create!`
      });
      console.log(err)
    })
  }

  public deleteInspector(inspector: Inspector): void {
    inspector.deleted = true
    this.inspectorService.update(inspector.id, inspector).toPromise().then(() => {
      this.inspectorService.list().subscribe(inspectors => {
        this.inspectors = inspectors.filter(inspect => inspect.template === this.template.id)
      })
      this.closeModal()
      this.messageService.add({
        severity: 'success',
        summary: 'Success',
        detail: `Inspector ${inspector.name} is deleted!`
      });
      this.currentlySubmitting = false
    }).catch((err: HttpErrorResponse) => {
      this.errorMessage = err.error
      this.currentlySubmitting = false
      this.messageService.add({
        severity: 'error',
        summary: 'Error',
        detail: `Inspector ${inspector.name} failed to be deleted!`
      });
      console.log(err)
    })
  }

  public editInspector(inspector: Inspector): void {
    this.updatedInspector = inspector
    this.name = this.fb.control(inspector.name, [Validators.required])
    this.variableName = this.fb.control(inspector.variable_name)
    this.cleanUpExpression = this.fb.control(inspector.clean_up_expression === '' ? '' : inspector.clean_up_expression.split("\";\""))
    this.type = this.fb.control({key: inspector.type, value: inspector.type}, [Validators.required])
    this.selector = this.fb.control(inspector.selector, [Validators.required])
    this.attribute = this.fb.control(inspector.attribute)
    this.form = this.fb.group({
      selector: this.selector,
      attribute: this.attribute,
      name: this.name,
      variableName: this.variableName,
      cleanUpExpression: this.cleanUpExpression,
      type: this.type,
    })
    this.displayModal = true
  }

  public ngOnInit(): void {
    this.inspectorService.list({template: this.template.id}).subscribe(inspectors => {
      this.inspectors = inspectors
    })
    this.initForm()
  }

  public createInspector(): void {
    this.initForm()
    this.updatedInspector = null
    this.displayModal = true
  }

  private initForm(): void {
    this.description = this.fb.control('')
    this.selector = this.fb.control('', [Validators.required])
    this.attribute = this.fb.control('')
    this.name = this.fb.control('', [Validators.required])
    this.variableName = this.fb.control('')
    this.cleanUpExpression = this.fb.control([])
    this.type = this.fb.control({key: 'text', value: 'text'}, [Validators.required])
    this.form = this.fb.group({
      description: this.description,
      url: this.selector,
      attribute: this.attribute,
      name: this.name,
      cleanUpExpression: this.cleanUpExpression,
      type: this.type,
    })
  }
}
