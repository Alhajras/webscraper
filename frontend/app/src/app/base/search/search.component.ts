import {Component} from '@angular/core';
import {FormBuilder, FormControl, FormGroup} from "@angular/forms";
import {HttpErrorResponse} from "@angular/common/http";
import {Crawler} from "src/app/models/crawler.model";
import {Template} from "src/app/models/template.model";
import {TemplateService} from "src/app/services/template.service";
import {CrawlerService} from "src/app/services/crawler.service";

export interface TemplateDropDown {
  key: string
  template: Template
}

export interface Product {
    id?: string;
    code?: string;
    name?: string;
    description?: string;
    price?: number;
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
  public templatesList: TemplateDropDown[] = []
  public currentlySubmitting = false
  public displayModal = false
  public header = 'crawler form'
  public errorMessage = ''
  public readonly columnCount = 8
  public loading = false
  public products:Product[]=[]

  public closeModal(): void {
    this.displayModal = false
  }

  public constructor(
    private readonly fb: FormBuilder,
    private readonly crawlerService: CrawlerService,
    private readonly templateService: TemplateService,
  ) {
this.products = [{
    id: '1000',
    code: 'f230fh0g3',
    name: 'Bamboo Watch',
    description: 'Product Description',
    image: 'bamboo-watch.jpg',
    price: 65,
    category: 'Accessories',
    quantity: 24,
    inventoryStatus: 'INSTOCK',
    rating: 5
},]
  }
}
