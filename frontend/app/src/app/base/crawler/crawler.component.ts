import {Component} from '@angular/core';
import {FormBuilder, FormControl, FormGroup, Validators} from "@angular/forms";
import {HttpErrorResponse} from "@angular/common/http";
import {Crawler} from "src/app/models/crawler.model";
import {Template} from "src/app/models/template.model";
import {TemplateService} from "src/app/services/template.service";
import {CrawlerService} from "src/app/services/crawler.service";

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
  public description!: FormControl
  public template!: FormControl
  public seedUrl!: FormControl
  public name!: FormControl
  public threads!: FormControl
  public retry!: FormControl
  public sleep!: FormControl
  public timeout!: FormControl
  public maxPages!: FormControl
  public maxDepth!: FormControl
  public robotFileUrl!: FormControl
  public excludedUrls!: FormControl
  public scopeDivs!: FormControl

  public form!: FormGroup
  public templatesList: TemplateDropDown[] = []
  public currentlySubmitting = false
  public displayModal = false
  public header = 'Crawler form'
  public errorMessage = ''
  public readonly columnCount = 6
  public loading = false

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
      seed_url: this.seedUrl.value,
      template: this.template.value.template.id,
      threads: this.threads.value,
      retry: this.retry.value,
      sleep: this.sleep.value,
      timeout: this.timeout.value,
      max_pages: this.maxPages.value,
      max_depth: this.maxDepth.value,
      robot_file_url: this.robotFileUrl.value,
      excluded_urls: this.excludedUrls.value ?? this.excludedUrls.value.join('";"'),
      scope_divs: this.scopeDivs.value ?? this.scopeDivs.value.join('";"')
    }
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

  public constructor(
    private readonly fb: FormBuilder,
    private readonly crawlerService: CrawlerService,
    private readonly templateService: TemplateService,
  ) {
    this.loading = true
    crawlerService.list().subscribe(crawlers => {
      this.crawlers = crawlers
      this.loading = false
    })

    this.templateService.list().subscribe(templates => {
      this.templatesList = templates.map(t => ({
        key: t.name,
        template: t,
      }))
    })

    const urlReg = '(https?://)?([\\da-z.-]+)\\.([a-z.]{2,6})[/\\w .-]*/?';

    this.template = this.fb.control('', [Validators.required])
    this.description = this.fb.control('')
    this.seedUrl = this.fb.control('' , [Validators.required, Validators.pattern(urlReg)])
    this.name = this.fb.control('', [Validators.required])
    this.threads= this.fb.control('')
    this.retry= this.fb.control(0)
    this.sleep= this.fb.control(0)
    this.timeout= this.fb.control('')
    this.maxPages= this.fb.control('')
    this.maxDepth= this.fb.control(2)
    this.robotFileUrl= this.fb.control('', Validators.pattern(urlReg))
    this.excludedUrls= this.fb.control('' , Validators.pattern(urlReg))
    this.scopeDivs= this.fb.control('')

    this.form = this.fb.group({
      description: this.description,
      url: this.seedUrl,
      name: this.name,
      threads: this.threads,
      retry: this.retry,
      sleep: this.sleep,
      timeout: this.timeout,
      max_pages: this.maxPages,
      max_depth: this.maxDepth,
      robot_file_url: this.robotFileUrl,
      excluded_urls: this.excludedUrls,
      scope_divs: this.scopeDivs
    })
  }

  public editCrawler(crawler: Crawler): void {
    this.updatedCrawler = crawler
    this.description = this.fb.control(crawler.description)
    this.seedUrl = this.fb.control(crawler.seed_url)
    this.name = this.fb.control(crawler.name)
    this.template = this.fb.control(crawler.template)
    this.threads = this.fb.control(crawler.threads)
    this.retry = this.fb.control(crawler.retry)
    this.sleep = this.fb.control(crawler.sleep)
    this.timeout = this.fb.control(crawler.timeout)
    this.maxPages = this.fb.control(crawler.max_pages)
    this.maxDepth = this.fb.control(crawler.max_depth)
    this.robotFileUrl = this.fb.control(crawler.robot_file_url)
    this.excludedUrls = this.fb.control(crawler.excluded_urls.split("\";\""))
    this.scopeDivs = this.fb.control(crawler.scope_divs.split("\";\""))

    this.form = this.fb.group({
      description: this.description,
      seed_url: this.seedUrl,
      name: this.name,
      template: this.template,
      threads: this.threads,
      retry: this.retry,
      sleep: this.sleep,
      timeout: this.timeout,
      max_pages: this.maxPages,
      max_depth: this.maxDepth,
      robot_file_url: this.robotFileUrl,
      excluded_urls: this.excludedUrls,
      scope_divs: this.scopeDivs
    })
    this.displayModal = true
  }
}
