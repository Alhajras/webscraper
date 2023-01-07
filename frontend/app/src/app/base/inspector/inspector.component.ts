import {Component, Input, OnInit} from '@angular/core';
import {Template} from "src/app/models/template.model";
import {Spider} from "src/app/models/spider.model";
import {MenuItem} from "primeng/api";
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
  public updatedSpider: Inspector | null = null
  public breadcrumbs: MenuItem[] = []
  public description!: FormControl
  public currentlySubmitting = false
  public displayModal = false
  public url!: FormControl
  public form!: FormGroup
  public header = 'Spider form'
  public name!: FormControl
  public errorMessage = ''
  public templates = []

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
    const spider = {
      description: this.description.value,
      name: this.name.value,
      url: this.url.value,
    }
    if (this.updatedSpider !== null) {
      this.inspectorService.update(this.updatedSpider.id, spider).toPromise().then(() => {
        this.inspectorService.list().subscribe(inspectors => {
          this.inspectors = inspectors
        })
        this.closeModal()
        this.currentlySubmitting = false
        this.updatedSpider = null
      }).catch((err: HttpErrorResponse) => {
        this.errorMessage = err.error
        this.currentlySubmitting = false
        console.log(err)
      })
      return;
    }
    this.inspectorService.post(spider).toPromise().then(() => {
      this.inspectorService.list().subscribe(spiders => {
        this.inspectors = spiders
      })
      this.closeModal()
      this.currentlySubmitting = false
    }).catch((err: HttpErrorResponse) => {
      this.errorMessage = err.error
      this.currentlySubmitting = false
      console.log(err)
    })
  }

  public deleteSpider(spider: Spider): void {
    spider.deleted = true
    this.inspectorService.update(spider.id, spider).toPromise().then(() => {
      this.inspectorService.list().subscribe(spiders => {
        this.inspectors = spiders
      })
      this.closeModal()
      this.currentlySubmitting = false
    }).catch((err: HttpErrorResponse) => {
      this.errorMessage = err.error
      this.currentlySubmitting = false
      console.log(err)
    })
  }

  public editSpider(inspector: Inspector): void {
    this.updatedSpider = inspector
    this.name = this.fb.control(inspector.name)
    this.form = this.fb.group({
      description: this.description,
      url: this.url,
      name: this.name,
    })
    this.displayModal = true
  }

  public ngOnInit(): void {
    this.inspectorService.list({template: this.template.id}).subscribe(inspectors => {
      this.inspectors = inspectors
    })
    this.description = this.fb.control('')
    this.url = this.fb.control('')
    this.name = this.fb.control('')
    this.form = this.fb.group({
      description: this.description,
      url: this.url,
      name: this.name,
    })
  }
}
