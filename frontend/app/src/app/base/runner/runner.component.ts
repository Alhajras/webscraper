import {Component} from '@angular/core';
import {FormBuilder, FormControl, FormGroup, Validators} from "@angular/forms";
import {HttpErrorResponse} from "@angular/common/http";
import {Runner} from "src/app/models/runner.model";
import {RunnerService} from "src/app/services/runner.service";
import {Crawler} from "src/app/models/crawler.model";
import {CrawlerService} from "src/app/services/crawler.service";

export interface CrawlerDropDown {
  key: string
  crawler: Crawler
}

@Component({
  selector: 'app-runner',
  templateUrl: './runner.component.html',
  styleUrls: ['./runner.component.scss']
})
export class RunnerComponent {
  public runners: Runner[] = []
  public updatedRunner: Runner | null = null
  public descriptionForm: FormControl = this.fb.control('')
  public crawlerForm: FormControl = this.fb.control('', [Validators.required])
  public name: FormControl = this.fb.control('', [Validators.required])
  public crawlersList: CrawlerDropDown[] = []
  public currentlySubmitting = false
  public displayModal = false
  public form!: FormGroup
  public header = 'Runner form'
  public errorMessage = ''
  public readonly columnCount = 8
  private readonly pullingTimeSec = 10000

  public constructor(
    private readonly fb: FormBuilder,
    private readonly runnerService: RunnerService,
    private readonly crawlerService: CrawlerService,
  ) {
    this.init()
    setInterval(() => {
      this.init()
    }, this.pullingTimeSec);
  }

  private init(): void {

    this.runnerService.list().subscribe(runners => {
      this.runners = runners
    })

    this.crawlerService.list().subscribe(crawlers => {
      this.crawlersList = crawlers.map(c => ({
        key: c.name,
        crawler: c,
      }))
    })

    this.form = this.fb.group({
      description: this.descriptionForm,
      name: this.name,
      crawler: this.crawlerForm,
    })
  }

  public closeModal(): void {
    this.displayModal = false
  }

  public start(): void {
    const runner = {
      description: this.descriptionForm.value,
      name: this.name.value,
      crawler: this.crawlerForm.value.crawler.id,
    }
    this.runnerService.start(runner).toPromise().then(() => {
      this.displayModal = false
    })
  }

  public submit(): void {
    if (!this.form.valid) {
      // We should normally never get here since the submit button should be disabled.
      console.warn('Form not valid.')
      return
    }

    this.currentlySubmitting = true
    const runner = {
      description: this.descriptionForm.value,
      name: this.name.value,
      crawler: this.crawlerForm.value.id,
    }

    if (this.updatedRunner !== null) {
      this.updateRunner(runner)
      return;
    }
    this.createRunner(runner)
  }

  private updateRunner(runner: Partial<Runner>) {
    if (this.updatedRunner !== null) {
      this.runnerService.update(this.updatedRunner.id, runner).toPromise().then(() => {
        this.runnerService.list().subscribe(runners => {
          this.runners = runners
        })
        this.closeModal()
        this.currentlySubmitting = false
        this.updatedRunner = null
      }).catch((err: HttpErrorResponse) => {
        this.errorMessage = err.error
        this.currentlySubmitting = false
        console.log(err)
      })
      return;
    }
  }

  public deleteRunner(runner: Runner): void {
    runner.deleted = true
    this.runnerService.update(runner.id, runner).toPromise().then(() => {
      this.runnerService.list().subscribe(runners => {
        this.runners = runners
      })
      this.closeModal()
      this.currentlySubmitting = false
    }).catch((err: HttpErrorResponse) => {
      this.errorMessage = err.error
      this.currentlySubmitting = false
      console.log(err)
    })
  }

  public stopRunner(runner: Runner): void {
    runner.deleted = true
    this.runnerService.stop(runner.id, runner).toPromise().then(() => {
      this.closeModal()
      this.currentlySubmitting = false
    }).catch((err: HttpErrorResponse) => {
      this.errorMessage = err.error
      this.currentlySubmitting = false
      console.log(err)
    })
  }

  public editRunner(runner: Runner): void {
    this.updatedRunner = runner
    this.descriptionForm = this.fb.control(runner.description)
    this.form = this.fb.group({
      description: this.descriptionForm,
    })
    this.displayModal = true
  }

  private createRunner(runner: Partial<Runner>) {
    this.runnerService.post(runner).toPromise().then(() => {
      this.runnerService.list().subscribe(runners => {
        this.runners = runners
      })
      this.closeModal()
      this.currentlySubmitting = false
    }).catch((err: HttpErrorResponse) => {
      this.errorMessage = err.error
      this.currentlySubmitting = false
      console.log(err)
    })
  }
}
