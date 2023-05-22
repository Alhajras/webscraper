import {Component} from '@angular/core';
import {MenuItem} from "primeng/api";
import {FormBuilder, FormControl, FormGroup} from "@angular/forms";
import {HttpErrorResponse} from "@angular/common/http";
import {Template} from "src/app/models/template.model";
import {TemplateService} from "src/app/services/template.service";

export interface TreeNode {
  data?: any;
  children?: TreeNode[];
  leaf?: boolean;
  expanded?: boolean;
}

@Component({
  selector: 'app-template',
  templateUrl: './template.component.html',
  styleUrls: ['./template.component.scss']
})
export class TemplateComponent {
  public templates: Template[] = []
  public updatedTemplate: Template | null = null
  public description!: FormControl
  public template!: FormControl
  public currentlySubmitting = false
  public displayModal = false
  public url!: FormControl
  public form!: FormGroup
  public header = 'Template form'
  public name!: FormControl
  public errorMessage = ''
  public downIcon = 'pi pi-chevron-down'
  public rightIcon = 'pi pi-chevron-right'
  public expandedRows: { [s: string]: boolean } = {}
  public readonly columnCount = 8
  public loading = false

  public constructor(
    private readonly fb: FormBuilder,
    private readonly templateService: TemplateService,
  ) {
    this.loading = true
    templateService.list().subscribe(templates => {
      this.templates = templates
      this.loading = false
    })
    this.name = this.fb.control('')
    this.form = this.fb.group({
      name: this.name,
    })
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
    const template = {
      name: this.name.value,
    }
    if (this.updatedTemplate !== null) {
      this.templateService.update(this.updatedTemplate.id, template).toPromise().then(() => {
        this.templateService.list().subscribe(templates => {
          this.templates = templates
        })
        this.closeModal()
        this.currentlySubmitting = false
        this.updatedTemplate = null
      }).catch((err: HttpErrorResponse) => {
        this.errorMessage = err.error
        this.currentlySubmitting = false
        console.log(err)
      })
      return;
    }
    this.templateService.post(template).toPromise().then(() => {
      this.templateService.list().subscribe(templates => {
        this.templates = templates
      })
      this.closeModal()
      this.currentlySubmitting = false
    }).catch((err: HttpErrorResponse) => {
      this.errorMessage = err.error
      this.currentlySubmitting = false
      console.log(err)
    })
  }

  private createTemplateNode(data: Template, expanded = false): TreeNode {
    return {
      data,
      expanded,
    }
  }

  public deleteTemplate(template: Template): void {
    template.deleted = true
    this.templateService.update(template.id, template).toPromise().then(() => {
      this.templateService.list().subscribe(templates => {
        this.templates = templates
      })
      this.closeModal()
      this.currentlySubmitting = false
    }).catch((err: HttpErrorResponse) => {
      this.errorMessage = err.error
      this.currentlySubmitting = false
      console.log(err)
    })
  }

  public editTemplate(template: Template): void {
    this.updatedTemplate = template
    this.name = this.fb.control(template.name)
    this.form = this.fb.group({
      name: this.name,
    })
    this.displayModal = true
  }
}
