import {Component} from '@angular/core';
import {FormBuilder, FormControl, FormGroup, Validators} from "@angular/forms";
import {HttpErrorResponse} from "@angular/common/http";
import {Runner} from "src/app/models/runner.model";
import {RunnerService} from "src/app/services/runner.service";
import {Crawler} from "src/app/models/crawler.model";
import {CrawlerService} from "src/app/services/crawler.service";
import {MenuItem, MessageService} from "primeng/api";
import {Menu} from "primeng/menu";

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
  public saveButton = {
    label: 'Download CSV',
    icon: 'pi pi-save',
    command: () => {
      this.download(this.runner);
    }
  }
  public stopButton = {
    label: 'Stop',
    icon: 'pi pi-times',
    command: () => {
      this.stopRunner(this.runner);
    }
  }
  public startButton = {
    label: 'Start',
    icon: 'pi pi-play',
    command: () => {
      this.restartRunner(this.runner);
    }
  }
  public editButton = {
    label: 'Edit',
    icon: 'pi pi-pencil',
    command: () => {
      this.editRunner(this.runner);
    }
  }
  public deleteButton = {
    label: 'Delete',
    icon: 'pi pi-trash',
    command: () => {
      this.deleteRunner(this.runner);
    }
  }
  public actions: MenuItem[] = []
  public outputRunner : Runner | null = null
  public runners: Runner[] = []
  public runner!: Runner
  public updatedRunner: Runner | null = null
  public descriptionForm: FormControl = this.fb.control('')
  public crawlerForm: FormControl = this.fb.control('', [Validators.required])
  public name: FormControl = this.fb.control('', [Validators.required])
  public machine: FormControl = this.fb.control('localhost', [Validators.required])
  public crawlersList: CrawlerDropDown[] = []
  public currentlySubmitting = false
  public displayModal = false
  public form!: FormGroup
  public header = 'Runner form'
  public errorMessage = ''
  public readonly columnCount = 5
  private readonly pullingTimeSec = 10000
  public loading = false
  public events = [
    {status: 'New'},
    {status: 'Running'},
    {status: 'Exit'},
    {status: 'Completed'},
  ];
  public displayOutputLog = false

  public constructor(
    private readonly fb: FormBuilder,
    private readonly runnerService: RunnerService,
    private readonly crawlerService: CrawlerService,
    private messageService: MessageService
  ) {
    this.loading = true
    this.init()
    setInterval(() => {
      this.init()
    }, this.pullingTimeSec);
  }

  private init(): void {

    this.runnerService.list().subscribe(runners => {
      this.runners = runners
      this.loading = false
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
      machine: this.machine,
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
      machine: this.machine.value,
    }
    this.runnerService.start(runner).toPromise().then(() => {
      this.displayModal = false
      this.messageService.add({
        severity: 'success',
        summary: 'Success',
        detail: `Runner ${this.name.value} created!`
      });
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
      machine: this.machine.value,
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
        this.messageService.add({
          severity: 'success',
          summary: 'Success',
          detail: `Runner ${this.name.value} is updated!`
        });
        this.currentlySubmitting = false
        this.updatedRunner = null
      }).catch((err: HttpErrorResponse) => {
        this.errorMessage = err.error
        this.currentlySubmitting = false
        this.messageService.add({
          severity: 'error',
          summary: 'Error',
          detail: `Runner ${this.name.value} failed to update!`
        });
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
      this.messageService.add({
        severity: 'success',
        summary: 'Success',
        detail: `Runner ${runner.name} is deleted!`
      });
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
      this.messageService.add({
        severity: 'success',
        summary: 'Success',
        detail: `Runner ${runner.name} is stopped!`
      });
    }).catch((err: HttpErrorResponse) => {
      this.errorMessage = err.error
      this.currentlySubmitting = false
      console.log(err)
    })
  }

  public editRunner(runner: Runner): void {
    this.updatedRunner = runner
    this.descriptionForm = this.fb.control(runner.description)
    this.name = this.fb.control(runner.name, [Validators.required])
    this.machine = this.fb.control(runner.machine, [Validators.required])

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
      this.messageService.add({
        severity: 'success',
        summary: 'Success',
        detail: `Runner ${runner.name} is created!`
      });
      this.currentlySubmitting = false
    }).catch((err: HttpErrorResponse) => {
      this.errorMessage = err.error
      this.currentlySubmitting = false
      console.log(err)
    })
  }

  public restartRunner(runner: Partial<Runner>): void {
    this.runnerService.reStart(runner).toPromise().then(() => {
      this.messageService.add({
        severity: 'success',
        summary: 'Success',
        detail: `Runner ${this.name.value} started!`
      });
    }).catch()
  }

  public download(runner: Runner): void {
    this.runnerService.download(runner.id, runner).toPromise().then(csvData => {
        const blob = new Blob([csvData], {type: 'text/csv'});
        const downloadLink = document.createElement('a');
        downloadLink.href = URL.createObjectURL(blob);
        downloadLink.download = `${runner.id}.runner_output.csv`;
        downloadLink.click()
        URL.revokeObjectURL(downloadLink.href)
        this.messageService.add({
          severity: 'success',
          summary: 'Success',
          detail: `Starting to download ${runner.id}.runner_output.csv `
        });
      }
    ).catch()
  }

  public openMenu($event: MouseEvent, menu: Menu, runner: Runner): void {
    this.actions = []
    this.runner = runner
    if (runner.collected_documents) {
      this.actions.push(this.saveButton)

    } else {
      this.actions.push({disabled: true, ...this.saveButton})

    }
    if (runner.status !== 'Exit' && runner.status !== 'Completed' && runner.status !== 'New') {
      this.actions.push(this.stopButton)
      this.actions.push({disabled: true, ...this.startButton})
      this.actions.push({disabled: true, ...this.deleteButton})
    }

    if (runner.status === 'Exit' || runner.status === 'Completed' || runner.status === 'New') {
      this.actions.push({disabled: true, ...this.stopButton})
      this.actions.push(this.startButton)
      this.actions.push(this.deleteButton)
    }


    menu.toggle($event)
  }

  public closeOutputLogModal(): void {
    this.displayOutputLog = false

  }

  public openOutput(runner: Runner): void {
    this.displayOutputLog = true
    this.outputRunner = runner
  }
}
