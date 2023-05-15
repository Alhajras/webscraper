import {Component, OnInit} from '@angular/core';
import {FormBuilder, FormControl, FormGroup} from "@angular/forms";
import {HttpErrorResponse} from "@angular/common/http";
import {Inspector} from "src/app/models/inspector.model";
import {Indexer} from "src/app/models/indexer.model";
import {IndexerService} from "src/app/services/indexer.service";

@Component({
  selector: 'app-indexer',
  templateUrl: './indexer.component.html',
  styleUrls: ['./indexer.component.scss']
})
export class IndexerComponent implements OnInit {
  public indexers: Indexer[] = []
  public updatedIndexer: Inspector | null = null
  public description!: FormControl
  public currentlySubmitting = false
  public displayModal = false
  public form!: FormGroup
  public header = 'Indexer form'
  public name!: FormControl
  public errorMessage = ''
  public readonly columnCount = 8
  public loading = false

  public constructor(
    private readonly fb: FormBuilder,
    private readonly indexerService: IndexerService,
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
    const indexer = {
      name: this.name.value,
      description: this.description.value
    }
    if (this.updatedIndexer !== null) {
      // this.inspectorService.update(this.updatedInspector.id, inspector).toPromise().then(() => {
      //   this.inspectorService.list({template: this.template.id}).subscribe(inspectors => {
      //     this.inspectors = inspectors
      //   })
      //   this.closeModal()
      //   this.currentlySubmitting = false
      //   this.updatedInspector = null
      // }).catch((err: HttpErrorResponse) => {
      //   this.errorMessage = err.error
      //   this.currentlySubmitting = false
      //   console.log(err)
      // })
      return;
    }
    // this.inspectorService.post(inspector).toPromise().then(() => {
    //   this.inspectorService.list({template: this.template.id}).subscribe(inspectors => {
    //     this.inspectors = inspectors
    //   })
    //   this.closeModal()
    //   this.currentlySubmitting = false
    // }).catch((err: HttpErrorResponse) => {
    //   this.errorMessage = err.error
    //   this.currentlySubmitting = false
    //   console.log(err)
    // })
  }

  public deleteInspector(inspector: Inspector): void {
    inspector.deleted = true
    // this.inspectorService.update(inspector.id, inspector).toPromise().then(() => {
    //   this.inspectorService.list().subscribe(inspectors => {
    //     // this.inspectors = inspectors
    //   })
    //   this.closeModal()
    //   this.currentlySubmitting = false
    // }).catch((err: HttpErrorResponse) => {
    //   this.errorMessage = err.error
    //   this.currentlySubmitting = false
    //   console.log(err)
    // })
  }

  public editInspector(inspector: Inspector): void {
    // this.updatedIndexer = inspector
    // this.name = this.fb.control(inspector.name)
    // this.selector = this.fb.control(inspector.selector)
    // this.form = this.fb.group({
    //   selector: this.selector,
    //   name: this.name,
    // })
    // this.displayModal = true
  }

  public ngOnInit(): void {
    this.indexerService.list().subscribe(indexers => {
      this.indexers = indexers
    })
    this.initForm()
  }

  public createIndexer() {
    this.initForm()
    this.updatedIndexer = null
    this.displayModal = true
  }

  private initForm() {
    // this.description = this.fb.control('')
    // this.selector = this.fb.control('')
    // this.name = this.fb.control('')
    // this.form = this.fb.group({
    //   description: this.description,
    //   url: this.selector,
    //   name: this.name,
    // })
  }
}
