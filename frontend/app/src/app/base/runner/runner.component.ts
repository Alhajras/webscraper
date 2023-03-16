import {Component} from '@angular/core';
import {MenuItem} from "primeng/api";
import {FormBuilder, FormControl, FormGroup} from "@angular/forms";
import {TemplateService} from "src/app/services/template.service";
import {HttpErrorResponse} from "@angular/common/http";
import {TemplateDropDown} from "src/app/base/crawler/crawler.component";
import {Runner} from "src/app/models/runner.model";
import {RunnerService} from "src/app/services/runner.service";

@Component({
  selector: 'app-runner',
  templateUrl: './runner.component.html',
  styleUrls: ['./runner.component.scss']
})
export class RunnerComponent {
  public runners: Runner[] = []
  public updatedRunner: Runner | null = null
  public breadcrumbs: MenuItem[] = []
  public description!: FormControl
  public template!: FormControl
  public templatesList: TemplateDropDown[] = []
  public currentlySubmitting = false
  public displayModal = false
  public url!: FormControl
  public form!: FormGroup
  public header = 'Runner form'
  public name!: FormControl
  public errorMessage = ''
  public readonly columnCount = 8

  public constructor(
    private readonly fb: FormBuilder,
    private readonly runnerService: RunnerService,
    private readonly templateService: TemplateService,
  ) {
    runnerService.list().subscribe(runners => {
      this.runners = runners
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

  public start(): void{
    this.runnerService.start(this.updatedRunner ?? {}).toPromise().then()
  }
  public submit(): void {
    if (!this.form.valid) {
      // We should normally never get here since the submit button should be disabled.
      console.warn('Form not valid.')
      return
    }

    this.currentlySubmitting = true
    const runner = {
      description: this.description.value,
      name: this.name.value,
      url: this.url.value,
      template: this.template.value.template.id,
    }
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


  public editRunner(runner: Runner): void {
    this.updatedRunner = runner
    this.description = this.fb.control(runner.description)
    this.form = this.fb.group({
      description: this.description,
    })
    this.displayModal = true
  }
}
