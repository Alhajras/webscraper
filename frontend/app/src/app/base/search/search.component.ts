import {Component} from '@angular/core';
import {FormControl, FormGroup, Validators} from "@angular/forms";
import {Template} from "src/app/models/template.model";
import {IndexerService} from "src/app/services/indexer.service";
import {InspectorValue} from "src/app/models/inspector-value.model";
import {Indexer} from "src/app/models/indexer.model";

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
  public form!: FormGroup
  public currentlySubmitting = false
  public displayModal = false
  public errorMessage = ''
  public readonly columnCount = 8
  public loading = false
  public products: any[] = []
  public searchText = ''
  public cached_indexers = []
  public selectedIndexerForm!: Indexer

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

  private createProduct(items: InspectorValue[]): Partial<Product> {
    let product: Product = {}
    items.forEach((item: InspectorValue) => {
      switch (item.inspector) {
        case 1:
          product.name = item.value
          break;
        case 2:
          product.price = item.value
          break;
        default:
          product.image = item.attribute
      }
    })
    return product
  }

  public searchProducts() {
    this.loading = true
    this.products = []
    // TODO this is bad and must be dynamic
    this.indexerService.search(this.selectedIndexerForm.id, this.searchText).subscribe(values => {
      values.forEach(p => {
        this.products = [...this.products, this.createProduct(p)]
      })
      this.loading = false
    })
  }
}
