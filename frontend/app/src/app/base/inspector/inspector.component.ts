import {Component, Input, OnInit} from '@angular/core';
import {Template} from "src/app/models/template.model";
import {FormBuilder, FormControl, FormGroup} from "@angular/forms";
import {HttpErrorResponse} from "@angular/common/http";
import {Inspector} from "src/app/models/inspector.model";
import {InspectorService} from "src/app/services/inspector.service";

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
  public form!: FormGroup
  public header = 'Inspector form'
  public name!: FormControl
  public errorMessage = ''
  public templates = []
  public readonly columnCount = 8

  public constructor(
    private readonly fb: FormBuilder,
    private readonly inspectorService: InspectorService,
  ) {

  }

  public closeModal(): void {
    this.displayModal = false
  }

  public submit(): void {
    if (!this.form.valid) {
      // We should normally never get here since the submit button should be disabled.
      console.warn('Form not valid.')
      return
    }

    this.currentlySubmitting = true
    const inspector = {
      name: this.name.value,
      selector: this.selector.value,
      attribute: this.attribute.value === '' ? null : this.attribute.value,
      template: this.template.id,
    }
    if (this.updatedInspector !== null) {
      this.inspectorService.update(this.updatedInspector.id, inspector).toPromise().then(() => {
        this.inspectorService.list({template: this.template.id}).subscribe(inspectors => {
          this.inspectors = inspectors
        })
        this.closeModal()
        this.currentlySubmitting = false
        this.updatedInspector = null
      }).catch((err: HttpErrorResponse) => {
        this.errorMessage = err.error
        this.currentlySubmitting = false
        console.log(err)
      })
      return;
    }
    this.inspectorService.post(inspector).toPromise().then(() => {
      this.inspectorService.list({template: this.template.id}).subscribe(inspectors => {
        this.inspectors = inspectors
      })
      this.closeModal()
      this.currentlySubmitting = false
    }).catch((err: HttpErrorResponse) => {
      this.errorMessage = err.error
      this.currentlySubmitting = false
      console.log(err)
    })
  }

  public deleteInspector(inspector: Inspector): void {
    inspector.deleted = true
    this.inspectorService.update(inspector.id, inspector).toPromise().then(() => {
      this.inspectorService.list().subscribe(inspectors => {
        this.inspectors = inspectors
      })
      this.closeModal()
      this.currentlySubmitting = false
    }).catch((err: HttpErrorResponse) => {
      this.errorMessage = err.error
      this.currentlySubmitting = false
      console.log(err)
    })
  }

  public editInspector(inspector: Inspector): void {
    this.updatedInspector = inspector
    this.name = this.fb.control(inspector.name)
    this.selector = this.fb.control(inspector.selector)
    this.attribute = this.fb.control(inspector.attribute)
    this.form = this.fb.group({
      selector: this.selector,
      attribute: this.attribute,
      name: this.name,
    })
    this.displayModal = true
  }

  public ngOnInit(): void {
    this.inspectorService.list({template: this.template.id}).subscribe(inspectors => {
      this.inspectors = inspectors
    })
    this.initForm()
  }

  public createInspector():void {
    this.initForm()
    this.updatedInspector = null
    this.displayModal = true
  }

  private initForm():void {
    this.description = this.fb.control('')
    this.selector = this.fb.control('')
    this.attribute = this.fb.control('')
    this.name = this.fb.control('')
    this.form = this.fb.group({
      description: this.description,
      url: this.selector,
      attribute: this.attribute,
      name: this.name,
    })
  }
}
