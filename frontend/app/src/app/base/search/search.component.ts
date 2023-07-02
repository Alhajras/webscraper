import {Component, ViewChild} from '@angular/core';
import {FormGroup} from "@angular/forms";
import {Template} from "src/app/models/template.model";
import {IndexerService} from "src/app/services/indexer.service";
import {InspectorValue} from "src/app/models/inspector-value.model";
import {Indexer} from "src/app/models/indexer.model";
import {debounceTime, distinctUntilChanged, Subject, switchMap} from "rxjs";
import {OverlayPanel} from "primeng/overlaypanel";
import {MenuItem} from "primeng/api";

export interface TemplateDropDown {
  key: string
  template: Template
}

export interface Document {
  id: number;
  inspector_values: any[];
}

@Component({
  selector: 'app-search',
  templateUrl: './search.component.html',
  styleUrls: ['./search.component.scss']
})
export class SearchComponent {
  @ViewChild('op')
  public suggestionsOverlayPanel!: OverlayPanel

  public form!: FormGroup
  public currentlySubmitting = false
  public displayModal = false
  public errorMessage = ''
  public readonly columnCount = 8
  public loading = false
  public documents: Record<number, Document[]> = {}

  public searchText = ''
  public cached_indexers = []
  public selectedIndexerForm!: Indexer
  public headers: string[] = ['Image', 'Title', 'Description', 'Source', 'Price']
  public suggestions: MenuItem[] = []
  private searchText$ = new Subject<string>();
  public event!: KeyboardEvent
  public targetEl!: HTMLInputElement
  public loadingSuggestions = false

  public closeModal(): void {
    this.displayModal = false
  }

  public constructor(
    private readonly indexerService: IndexerService,
  ) {
    this.indexerService.indexedIndexers().subscribe(cached_indexers => {
      this.cached_indexers = cached_indexers
    })
  }

  public ngOnInit(): void {
    this.searchText$.pipe(
      debounceTime(500),
      distinctUntilChanged(),
      switchMap(suggestion =>
        this.indexerService.suggest(this.selectedIndexerForm.id, suggestion)
      )).subscribe(s => {
      this.suggestions = s.suggestions.map(s => ({
        label: s, command: (s: { event: PointerEvent, item: MenuItem }) => {
          this.searchText = s.item.label ?? this.searchText
          this.loadingSuggestions = false
          this.searchProducts()
        }
      }))
      this.loadingSuggestions = false
      if (this.suggestions.length > 0) {
        console.log(this.suggestionsOverlayPanel)
        this.suggestionsOverlayPanel.show(this.event, this.targetEl)
      }
    })
  }

  public searchProducts() {
    this.suggestionsOverlayPanel.hide()
    this.loading = true
    this.documents = []
    // TODO this is bad and must be dynamic
    this.indexerService.search(this.selectedIndexerForm.id, this.searchText).subscribe((values: {
      headers: string[],
      docs: Record<number, Document[]>
    }) => {
      this.headers = values.headers
      this.documents = values.docs
      this.loading = false
    })
  }

  public showSuggestions(event: KeyboardEvent, targetEl: HTMLInputElement): void {
    if (/^[a-zA-Z]$/.test(event.key)) {
      this.event = event
      this.targetEl = targetEl
      this.loadingSuggestions = true
      this.searchText$.next(this.searchText);
    }
  }
}
