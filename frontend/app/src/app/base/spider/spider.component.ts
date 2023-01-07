import {Component} from '@angular/core';
import {MenuItem} from "primeng/api";
import {FormBuilder, FormControl, FormGroup} from "@angular/forms";
import {SpiderService} from "src/app/services/spider.service";
import {HttpErrorResponse} from "@angular/common/http";
import {Spider} from "src/app/models/spider.model";
import {Template} from "src/app/models/template.model";
import {TemplateService} from "src/app/services/template.service";

export interface TemplateDropDown {
  key: string
  template: Template
}

@Component({
  selector: 'app-spider',
  templateUrl: './spider.component.html',
  styleUrls: ['./spider.component.scss']
})
export class SpiderComponent {
  public spiders: Spider[] = []
  public updatedSpider: Spider | null = null
  public breadcrumbs: MenuItem[] = []
  public description!: FormControl
  public template!: FormControl
  public templatesList: TemplateDropDown[] = []
  public currentlySubmitting = false
  public displayModal = false
  public url!: FormControl
  public form!: FormGroup
  public header = 'Spider form'
  public name!: FormControl
  public errorMessage = ''
  public readonly columnCount = 8

  public constructor(
    private readonly fb: FormBuilder,
    private readonly spiderService: SpiderService,
    private readonly templateService: TemplateService,
  ) {
    spiderService.list().subscribe(spiders => {
      this.spiders = spiders
    })

    this.templateService.list().subscribe(templates => {
      this.templatesList = templates.map(t => ({
            key: t.name,
            template: t,
          }))
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
      template: this.template.value.template.id,
    }
    console.log(spider)
    if (this.updatedSpider !== null) {
      this.spiderService.update(this.updatedSpider.id, spider).toPromise().then(() => {
        this.spiderService.list().subscribe(spiders => {
          this.spiders = spiders
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
    this.spiderService.post(spider).toPromise().then(() => {
      this.spiderService.list().subscribe(spiders => {
        this.spiders = spiders
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
    this.spiderService.update(spider.id, spider).toPromise().then(() => {
      this.spiderService.list().subscribe(spiders => {
        this.spiders = spiders
      })
      this.closeModal()
      this.currentlySubmitting = false
    }).catch((err: HttpErrorResponse) => {
      this.errorMessage = err.error
      this.currentlySubmitting = false
      console.log(err)
    })
  }

  public editSpider(spider: Spider): void {
    this.updatedSpider = spider
    this.description = this.fb.control(spider.description)
    this.url = this.fb.control(spider.url)
    this.name = this.fb.control(spider.name)
    this.template = this.fb.control(spider.template)
    this.form = this.fb.group({
      description: this.description,
      url: this.url,
      name: this.name,
      template: this.template,
    })
    this.displayModal = true
  }
}
