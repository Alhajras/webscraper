import {Component, OnInit} from '@angular/core';
import {FormBuilder, FormControl, FormGroup} from "@angular/forms";
import {HttpErrorResponse} from "@angular/common/http";
import {Indexer} from "src/app/models/indexer.model";
import {IndexerService} from "src/app/services/indexer.service";
import {InspectorService} from "src/app/services/inspector.service";

@Component({
  selector: 'app-indexer',
  templateUrl: './indexer.component.html',
  styleUrls: ['./indexer.component.scss']
})
export class IndexerComponent implements OnInit {
  public indexers: Indexer[] = []
  public updatedIndexer: Indexer | null = null
  public name!: FormControl
  public selectedInspectors!: FormControl
  public kParameter!: FormControl
  public bParameter!: FormControl
  public useSynonym!: FormControl
  public qGram!: FormControl

  public description!: FormControl
  public skipWordsList!: FormControl
  public smallWordsThreshold!: FormControl
  public dictionary!: FormControl
  public currentlySubmitting = false
  public displayModal = false
  public form!: FormGroup
  public header = 'Indexer form'
  public selectorsIdsOptions: { name: string, id: number }[] = []
  public errorMessage = ''
  public readonly columnCount = 5
  public loading = false

  public constructor(
    private readonly fb: FormBuilder,
    private readonly indexerService: IndexerService,
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
    const indexer = {
      name: this.name.value,
      k_parameter: this.kParameter.value,
      b_parameter: this.bParameter.value,
      q_gram_use_synonym: this.useSynonym.value,
      inspectors_to_be_indexed: this.selectedInspectors.value.map((inspector: any) => inspector.id),
      q_gram_q: this.qGram.value,
      dictionary: this.dictionary.value,
      small_words_threshold: this.smallWordsThreshold.value,
      skip_words: this.skipWordsList.value.length === 0 ? '' : this.skipWordsList.value.join('";"'),
    }
    if (this.updatedIndexer !== null) {
      this.indexerService.update(this.updatedIndexer.id, indexer).toPromise().then(() => {
        this.ngOnInit()
        this.closeModal()
        this.currentlySubmitting = false
        this.updatedIndexer = null
      }).catch((err: HttpErrorResponse) => {
        this.errorMessage = err.error
        this.currentlySubmitting = false
        console.log(err)
      })
      return;
    }
    this.indexerService.post(indexer).toPromise().then(() => {
      this.reloadIndexers()
      this.closeModal()
      this.currentlySubmitting = false
    }).catch((err: HttpErrorResponse) => {
      this.errorMessage = err.error
      this.currentlySubmitting = false
      console.log(err)
    })
  }

  public deleteInspector(indexer: Indexer): void {
    indexer.deleted = true
    this.indexerService.update(indexer.id, {name:indexer.name,  deleted: true}).toPromise().then(() => {
      this.reloadIndexers()
      this.closeModal()
      this.currentlySubmitting = false
    }).catch((err: HttpErrorResponse) => {
      this.errorMessage = err.error
      this.currentlySubmitting = false
      console.log(err)
    })
  }

  public editInspector(indexer: Indexer): void {
    this.updatedIndexer = indexer
    this.name = this.fb.control(indexer.name)
    this.kParameter = this.fb.control(indexer.k_parameter)
    this.bParameter = this.fb.control(indexer.b_parameter)
    this.useSynonym = this.fb.control(indexer.q_gram_use_synonym)
    this.qGram = this.fb.control(indexer.q_gram_q)
    this.dictionary = this.fb.control(indexer.dictionary)
    this.smallWordsThreshold = this.fb.control(indexer.small_words_threshold)
    this.skipWordsList = this.fb.control(indexer.skip_words === '' ? '' : indexer.skip_words.split("\";\""))
    this.form = this.fb.group({
      name: this.name,
      kParameter: this.kParameter,
      bParameter: this.bParameter,
      useSynonym: this.useSynonym,
      qGram: this.qGram,
      dictionary: this.dictionary,
      smallWordsThreshold: this.smallWordsThreshold,
      skip_words: this.skipWordsList,
    })
    this.displayModal = true
  }

  private reloadIndexers(): void {
    this.indexerService.list().subscribe(indexers => {
      this.indexers = indexers
    })

  }

  public ngOnInit(): void {
    this.reloadIndexers()
    this.initForm()
  }

  public createIndexer() {
    this.initForm()
    this.updatedIndexer = null
    this.displayModal = true
  }

  private initForm() {
    this.inspectorService.list().subscribe(inspectors => {
      this.selectorsIdsOptions = inspectors.filter(inspector => inspector.type !== 'image').map(inspector => {
        return {
          name: `${inspector.name} (${inspector.template_name}) `,
          id: inspector.id
        }
      })
    })
    // this.description = this.fb.control('')
    this.selectedInspectors = this.fb.control('')
    this.name = this.fb.control('')
    this.skipWordsList = this.fb.control('')
    this.smallWordsThreshold = this.fb.control(0)
    this.kParameter = this.fb.control(1.75)
    this.bParameter = this.fb.control(0.75)
    this.useSynonym = this.fb.control(true)
    this.qGram = this.fb.control(3)
    this.dictionary = this.fb.control('wikidata-entities.tsv')
    this.form = this.fb.group({
      selectedInspectors: this.selectedInspectors,
      name: this.name,
      skipWordsList: this.skipWordsList,
      smallWordsThreshold: this.smallWordsThreshold,
      bParameter: this.bParameter,
      useSynonym: this.useSynonym,
      qGram: this.qGram,
      dictionary: this.dictionary,
      kParameter: this.kParameter,
    })
  }

  public startIndexing(indexer: Indexer) {
    this.currentlySubmitting = true

    this.indexerService.startIndexing(indexer.id, indexer).subscribe(i => {
      this.currentlySubmitting = false
    })
  }
}
