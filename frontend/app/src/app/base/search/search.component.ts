import {Component} from '@angular/core';
import {FormControl, FormGroup} from "@angular/forms";
import {Template} from "src/app/models/template.model";
import {IndexerService} from "src/app/services/indexer.service";
import {InspectorValue} from "src/app/models/inspector-value.model";

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
  public header = 'crawler form'
  public errorMessage = ''
  public readonly columnCount = 8
  public loading = false
  public products: any[] = []
  public searchText = ''

  public closeModal(): void {
    this.displayModal = false
  }

  public constructor(
    private readonly indexerService: IndexerService,
  ) {
  }

  private createProduct(items: InspectorValue[]): Partial<Product> {
    console.log(items)
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
    this.indexerService.search(8, this.searchText).subscribe(values => {
      values.forEach(p => {
        this.products = [...this.products, this.createProduct(p)]
      })
      this.loading = false
    })
  }
}
