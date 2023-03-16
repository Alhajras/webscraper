import {Component} from '@angular/core';
import {MenuItem} from "primeng/api";
import {FormBuilder, FormControl, FormGroup} from "@angular/forms";
import {CrawlerService} from "src/app/services/crawler.service";
import {HttpErrorResponse} from "@angular/common/http";
import {Crawler} from "src/app/models/crawler.model";
import {Template} from "src/app/models/template.model";
import {TemplateService} from "src/app/services/template.service";

export interface TemplateDropDown {
  key: string
  template: Template
}

@Component({
  selector: 'app-crawler',
  templateUrl: './crawler.component.html',
  styleUrls: ['./crawler.component.scss']
})
export class CrawlerComponent {
  public crawlers: Crawler[] = []
  public updatedCrawler: Crawler | null = null
  public breadcrumbs: MenuItem[] = []
  public description!: FormControl
  public template!: FormControl
  public templatesList: TemplateDropDown[] = []
  public currentlySubmitting = false
  public displayModal = false
  public url!: FormControl
  public form!: FormGroup
  public header = 'crawler form'
  public name!: FormControl
  public errorMessage = ''
  public readonly columnCount = 8

  public constructor(
    private readonly fb: FormBuilder,
    private readonly crawlerService: CrawlerService,
    private readonly templateService: TemplateService,
  ) {
    crawlerService.list().subscribe(crawlers => {
      this.crawlers = crawlers
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
    const crawler = {
      description: this.description.value,
      name: this.name.value,
      url: this.url.value,
      template: this.template.value.template.id,
    }
    console.log(crawler)
    if (this.updatedCrawler !== null) {
      this.crawlerService.update(this.updatedCrawler.id, crawler).toPromise().then(() => {
        this.crawlerService.list().subscribe(crawlers => {
          this.crawlers = crawlers
        })
        this.closeModal()
        this.currentlySubmitting = false
        this.updatedCrawler = null
      }).catch((err: HttpErrorResponse) => {
        this.errorMessage = err.error
        this.currentlySubmitting = false
        console.log(err)
      })
      return;
    }
    this.crawlerService.post(crawler).toPromise().then(() => {
      this.crawlerService.list().subscribe(crawlers => {
        this.crawlers = crawlers
      })
      this.closeModal()
      this.currentlySubmitting = false
    }).catch((err: HttpErrorResponse) => {
      this.errorMessage = err.error
      this.currentlySubmitting = false
      console.log(err)
    })
  }

  public deleteCrawler(crawler: Crawler): void {
    crawler.deleted = true
    this.crawlerService.update(crawler.id, crawler).toPromise().then(() => {
      this.crawlerService.list().subscribe(crawlers => {
        this.crawlers = crawlers
      })
      this.closeModal()
      this.currentlySubmitting = false
    }).catch((err: HttpErrorResponse) => {
      this.errorMessage = err.error
      this.currentlySubmitting = false
      console.log(err)
    })
  }

  public editCrawler(crawler: Crawler): void {
    this.updatedCrawler = crawler
    this.description = this.fb.control(crawler.description)
    this.url = this.fb.control(crawler.url)
    this.name = this.fb.control(crawler.name)
    this.template = this.fb.control(crawler.template)
    this.form = this.fb.group({
      description: this.description,
      url: this.url,
      name: this.name,
      template: this.template,
    })
    this.displayModal = true
  }
}
