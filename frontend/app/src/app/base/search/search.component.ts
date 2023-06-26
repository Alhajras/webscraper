import {Component, ContentChild, ViewChild} from '@angular/core';
import {FormGroup} from "@angular/forms";
import {Template} from "src/app/models/template.model";
import {IndexerService} from "src/app/services/indexer.service";
import {InspectorValue} from "src/app/models/inspector-value.model";
import {Indexer} from "src/app/models/indexer.model";
import {ShortTextPipe} from "src/app/shared/pipes/short-text.pipe";
import {debounceTime, distinctUntilChanged, lastValueFrom, Observable, Subject, switchMap} from "rxjs";
import {Overlay} from "primeng/overlay";
import {OverlayPanel} from "primeng/overlaypanel";
import {MenuItem} from "primeng/api";

export interface TemplateDropDown {
  key: string
  template: Template
}

export interface Product {
  id?: string;
  code?: string;
  name?: string;
  description?: string;
  price?: string;
  quantity?: number;
  inventoryStatus?: string;
  category?: string;
  image?: string;
  rating?: number;
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
  public products: InspectorValue[][] = [[{
    id: 1,
    value: 'https://i.otto.de/i/otto/af18196d-efa9-5499-810e-4bf355a9d6d0?h=520&w=551&sm=clamp',
    url: 'https://i.otto.de/i/otto/af18196d-efa9-5499-810e-4bf355a9d6d0?h=520&w=551&sm=clamp',
    type: 'image',
    inspector: 1,
    attribute: '',
  }, {
    id: 1,
    value: 'Dior perfume',
    url: '',
    type: 'text',
    inspector: 1,
    attribute: '',
  }, {
    id: 1,
    value: 'Luxury label\'s designer fashion store, also selling cosmetics, jewelry & other accessories.',
    url: '',
    type: 'text',
    inspector: 1,
    attribute: '',
  }, {
    id: 1,
    value: '55$',
    url: '',
    type: 'text',
    inspector: 1,
    attribute: '',
  },
    {
      id: 1,
      value: 'dior.de',
      type: 'link',
      url: '',
      inspector: 1,
      attribute: '',
    }]]
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
        this.indexerService.suggest(1, suggestion)
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
    this.products = []
    // TODO this is bad and must be dynamic
    this.indexerService.search(this.selectedIndexerForm.id, this.searchText).subscribe((values: {
      headers: string[],
      docs: any[]
    }) => {
      this.headers = values.headers
      this.products = values.docs
      this.loading = false
    })
  }

  public showSuggestions(event: KeyboardEvent, targetEl: HTMLInputElement): void {
    this.event = event
    this.targetEl = targetEl
    this.loadingSuggestions = true
    this.searchText$.next(this.searchText);
  }
}
