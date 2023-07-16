import {Component, OnInit} from '@angular/core';
import {FormBuilder, FormControl, FormGroup, Validators} from "@angular/forms";
import {HttpErrorResponse} from "@angular/common/http";
import {Indexer} from "src/app/models/indexer.model";
import {IndexerService} from "src/app/services/indexer.service";
import {InspectorService} from "src/app/services/inspector.service";
import {lastValueFrom} from "rxjs";
import {Inspector} from "src/app/models/inspector.model";
import {OverlayPanel} from "primeng/overlaypanel";

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
  public boostingFormula!: FormControl

  public description!: FormControl
  public skipWordsList!: FormControl
  public weightWordsList!: FormControl
  public smallWordsThreshold!: FormControl
  public dictionary!: FormControl
  public currentlySubmitting = false
  public displayModal = false
  public form!: FormGroup
  public header = 'Indexer form'
  public selectorsIdsOptions: Inspector[] = []
  public errorMessage = ''
  public readonly columnCount = 5
  public loading = false
  private readonly pullingTimeSec = 10000
  public events = [
    {status: 'New'},
    {status: 'Dictionary'},
    {status: 'Indexing'},
    {status: 'Exit'},
    {status: 'Completed'},
  ];

  public constructor(
    private readonly fb: FormBuilder,
    private readonly indexerService: IndexerService,
    private readonly inspectorService: InspectorService,
  ) {

  }

  /**
   *  Closes the modal window
   */
  public closeModal(): void {
    this.displayModal = false
  }

  /**
   *   Submits the form data
   */
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
      inspectors_to_be_indexed: this.selectedInspectors.value.map((inspector: Inspector) => inspector.id),
      q_gram_q: this.qGram.value,
      boosting_formula: this.boostingFormula.value,
      dictionary: this.dictionary.value,
      small_words_threshold: this.smallWordsThreshold.value,
      skip_words: this.skipWordsList.value.length === 0 ? '' : this.skipWordsList.value.join('";"'),
      weight_words: this.weightWordsList.value.length === 0 ? '' : this.weightWordsList.value.join('";"'),
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

  /**
   * Deletes an indexer
   * @param indexer - Indexer that wants to remove the inspectors from
   */
  public deleteIndexer(indexer: Indexer): void {
    indexer.deleted = true
    this.indexerService.update(indexer.id, {name: indexer.name, deleted: true}).toPromise().then(() => {
      this.reloadIndexers()
      this.closeModal()
      this.currentlySubmitting = false
    }).catch((err: HttpErrorResponse) => {
      this.errorMessage = err.error
      this.currentlySubmitting = false
      console.log(err)
    })
  }

  /**
   * Edits an existing indexer
   * @param indexer - Indexer to be edited
   */
  public editIndexer(indexer: Indexer): void {
    this.updatedIndexer = indexer
    this.name = this.fb.control(indexer.name, [Validators.required])

    this.selectedInspectors = this.fb.control(indexer.inspectors, [Validators.required])
    this.kParameter = this.fb.control(indexer.k_parameter)
    this.bParameter = this.fb.control(indexer.b_parameter)
    this.useSynonym = this.fb.control(indexer.q_gram_use_synonym)
    this.qGram = this.fb.control(indexer.q_gram_q)
    this.boostingFormula = this.fb.control(indexer.boosting_formula)
    this.dictionary = this.fb.control(indexer.dictionary)
    this.smallWordsThreshold = this.fb.control(indexer.small_words_threshold)
    this.skipWordsList = this.fb.control(indexer.skip_words === '' ? '' : indexer.skip_words.split("\";\""))
    this.weightWordsList = this.fb.control(indexer.weight_words === '' ? '' : indexer.weight_words.split("\";\""))
    this.form = this.fb.group({
      name: this.name,
      kParameter: this.kParameter,
      bParameter: this.bParameter,
      useSynonym: this.useSynonym,
      qGram: this.qGram,
      boostingFormula: this.boostingFormula,
      dictionary: this.dictionary,
      smallWordsThreshold: this.smallWordsThreshold,
      skip_words: this.skipWordsList,
      weight_words_list: this.weightWordsList,
    })
    this.displayModal = true
  }

  /**
   * Reloads the list of indexers
   * @private
   */
  private reloadIndexers(): void {
    this.indexerService.list().subscribe(indexers => {
      this.indexers = indexers
      this.loading = false
    })

  }

  /**
   *  Initializes the component
   */
  public ngOnInit(): void {
    this.loading = true
    this.initForm()
    this.reloadIndexers()
    setInterval(() => {
      this.reloadIndexers()
    }, this.pullingTimeSec);
  }

  /**
   *  Creates a new indexer
   */
  public createIndexer(): void {
    this.initForm()
    this.updatedIndexer = null
    this.displayModal = true
  }

  /**
   * Initializes the form with default values
   * @private
   */
  private initForm(): void {
    this.inspectorService.list().subscribe(inspectors => {
      this.selectorsIdsOptions = inspectors.filter(inspector => inspector.type !== 'image')
    })
    this.selectedInspectors = this.fb.control('', [Validators.required])
    this.name = this.fb.control('', [Validators.required])
    this.skipWordsList = this.fb.control('')
    this.weightWordsList = this.fb.control('')
    this.smallWordsThreshold = this.fb.control(0)
    this.kParameter = this.fb.control(1.75)
    this.bParameter = this.fb.control(0.75)
    this.useSynonym = this.fb.control(true)
    this.qGram = this.fb.control(3)
    this.boostingFormula = this.fb.control('')
    this.dictionary = this.fb.control('wikidata-entities.tsv')
    this.form = this.fb.group({
      selectedInspectors: this.selectedInspectors,
      name: this.name,
      skipWordsList: this.skipWordsList,
      weightWordsList: this.weightWordsList,
      smallWordsThreshold: this.smallWordsThreshold,
      bParameter: this.bParameter,
      useSynonym: this.useSynonym,
      qGram: this.qGram,
      boostingFormula: this.boostingFormula,
      dictionary: this.dictionary,
      kParameter: this.kParameter,
    })
  }

  /**
   * Start the indexing process
   * @param indexer
   */
  public startIndexing(indexer: Indexer): void {
    lastValueFrom(this.indexerService.startIndexing(indexer.id, indexer)).then().catch()
    this.reloadIndexers()
  }

  public openRankingBooster(event: MouseEvent, op: OverlayPanel): void {
    op.toggle(event)
  }
}
