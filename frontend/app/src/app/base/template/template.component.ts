import { Component } from '@angular/core';
import {Spider} from "src/app/models/spider.model";
import {MenuItem} from "primeng/api";
import {FormBuilder, FormControl, FormGroup} from "@angular/forms";
import {SpiderService} from "src/app/services/spider.service";
import {HttpErrorResponse} from "@angular/common/http";

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
 public  templates: TreeNode[] = []
  public updatedSpider: Spider | null = null
  public breadcrumbs: MenuItem[] = []
  public description!: FormControl
  public template!: FormControl
  public currentlySubmitting = false
  public displayModal = false
  public url!: FormControl
  public form!: FormGroup
  public header = 'Spider form'
  public name!: FormControl
  public errorMessage = ''

  public constructor(
    private readonly fb: FormBuilder,
    private readonly spiderService: SpiderService,
  ) {
    spiderService.list().subscribe(spiders => {
      this.templates = spiders
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
    }
    if (this.updatedSpider !== null) {
      this.spiderService.update(this.updatedSpider.id, spider).toPromise().then(() => {
        this.spiderService.list().subscribe(spiders => {
          this.templates = spiders
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

    private createTemplateNode (key: string, data: Template, expanded = false): TreeNode {
    return {
      label: data.name,
      key,
      data,
      selectable: false,
      expanded,
    }
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
    this.form = this.fb.group({
      description: this.description,
      url: this.url,
      name: this.name,
    })
    this.displayModal = true
  }
}
